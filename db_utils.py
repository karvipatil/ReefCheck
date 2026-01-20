import boto3
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional, Union, Any
import pandas as pd
import streamlit as st

# Type alias for DynamoDB item
dynamodb_item = Dict[str, Any]


os.environ["AWS_ACCESS_KEY_ID"] = st.secrets["aws"]["AWS_ACCESS_KEY"]
os.environ["AWS_SECRET_ACCESS_KEY"] = st.secrets["aws"]["AWS_SECRET_KEY"]
os.environ["AWS_REGION"] = st.secrets["aws"]["REGION_NAME"]
os.environ["ENV"] = st.secrets["aws"]["ENV"]


def add_record(
    table_name: str,
    data_id: str,
    user_id: str,
    user_name: str,
    image_url: str,
    excel_url: str,
    status: str,
    creation_date: Optional[str] = None,
    additional_attributes: Optional[Dict] = None
) -> Dict:
    """
    Add a new record to the specified DynamoDB table.
    
    Args:
        table_name (str): Name of the DynamoDB table
        user_id (str): User ID associated with the record
        image_url (str): URL of the image
        excel_url (str): URL of the Excel file
        creation_date (str, optional): ISO format datetime string. Defaults to current datetime.
        additional_attributes (Dict, optional): Additional attributes to store. Defaults to None.
        
    Returns:
        Dict: The response from DynamoDB with success/error information
    """
    # Initialize AWS session and DynamoDB resource
    session = boto3.Session(
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )
    
    dynamodb = session.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    # Prepare the item
    item = {
        'data_id': data_id,
        'user_id': user_id,
        'user_name': user_name,
        'creation_date': creation_date or datetime.utcnow().isoformat(),
        'image_url': image_url,
        'excel_url': excel_url,
        'status': status
    }
    
    # Add any additional attributes if provided
    if additional_attributes:
        item.update(additional_attributes)
    
    try:
        # Put the item in the table
        response = table.put_item(Item=item)
        return {
            'success': True,
            'message': 'Record added successfully',
            'item': item,
            'response': response
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error adding record: {str(e)}',
            'item': item
        }


def get_recent_records(table_name: str, days: int = 14, gsi_name: str = 'CreationDateIndex') -> Dict[str, Union[bool, str, pd.DataFrame]]:
    """
    Fetch records from the DynamoDB table that were created within the specified number of days.
    
    Args:
        table_name (str): Name of the DynamoDB table
        days (int, optional): Number of days to look back. Defaults to 14 (2 weeks).
        gsi_name (str, optional): Name of the Global Secondary Index on creation_date.
                                 Defaults to 'CreationDateIndex'.
        
    Returns:
        Dict: A dictionary containing:
            - success (bool): Whether the operation was successful
            - message (str): Status message
            - data (pd.DataFrame): DataFrame containing the records, or None if there was an error
    """
    try:
        # Calculate the date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Initialize AWS session and DynamoDB resource
        session = boto3.Session(
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        
        dynamodb = session.resource('dynamodb')
        table = dynamodb.Table(table_name)
        
        # Use query on the GSI for creation_date
        response = table.query(
            IndexName=gsi_name,
            KeyConditionExpression='#pk = :pk_value AND #cd BETWEEN :start_date AND :end_date',
            ExpressionAttributeNames={
                '#pk': 'status',  # The partition key of the GSI
                '#cd': 'creation_date'  # The sort key of the GSI
            },
            ExpressionAttributeValues={
                ':pk_value': 'success',
                ':start_date': start_date.isoformat(),
                ':end_date': end_date.isoformat()
            },
            ScanIndexForward=False  # Sort in descending order (newest first)
        )
        
        items = response.get('Items', [])
        
        # Handle pagination if there are more items
        while 'LastEvaluatedKey' in response:
            response = table.query(
                IndexName=gsi_name,
                KeyConditionExpression='#pk = :pk_value AND #cd BETWEEN :start_date AND :end_date',
                ExpressionAttributeNames={
                    '#pk': 'status',
                    '#cd': 'creation_date'
                },
                ExpressionAttributeValues={
                    ':pk_value': 'success',
                    ':start_date': start_date.isoformat(),
                    ':end_date': end_date.isoformat()
                },
                ExclusiveStartKey=response['LastEvaluatedKey'],
                ScanIndexForward=False
            )
            items.extend(response.get('Items', []))
        
        if not items:
            return {
                'success': True,
                'message': 'No records found in the specified date range',
                'data': pd.DataFrame()
            }
        
        # Convert to DataFrame
        df = pd.DataFrame(items)
        
        # Convert creation_date to datetime and sort
        if 'creation_date' in df.columns:
            df['creation_date'] = pd.to_datetime(df['creation_date'])
            df = df.sort_values('creation_date', ascending=False)
        
        return {
            'success': True,
            'message': f'Successfully retrieved {len(df)} records',
            'data': df
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error fetching records: {str(e)}',
            'data': None
        }
