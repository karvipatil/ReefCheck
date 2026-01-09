from typing import Optional
from datetime import datetime, timedelta
import boto3
import streamlit as st
import os
import pandas as pd

os.environ["AWS_REGION"] = st.secrets['aws']['AWS_REGION']
os.environ["AWS_SECRET_ACCESS_KEY"] = st.secrets['aws']["AWS_SECRET_ACCESS_KEY"]
os.environ["AWS_ACCESS_KEY_ID"] = st.secrets['aws']["AWS_ACCESS_KEY_ID"]
os.environ["ENV"] = st.secrets['aws']["ENV"]


def adding_record(table_name: str,
                  data_id: str, 
                  user_id: str, 
                  user_name: str, 
                  image_url: str, 
                  excel_url: str, 
                  upload_status: str, 
                  creation_date: Optional[str] = None, 
                  additional_attributes: Optional[dict] = None):
  """
  Task: adding new record to the DynamoDB table
  
  Args: 
  table_name: name of DynamoDB table, 
  data_id: numerical identification of data, 
  user_id: numerical identification of user, 
  user_name: name of user, 
  image_url: url of the image, 
  excel_url: url of the excel, 
  upload_status: whether upload was successful or not, 
  creation_date: date of file creation, 
  additional_attributes: additional information

  Returns: 
  dictionary: response from DynamoDB
  """
  # initializing aws session and DynamoDB
  session = boto3.Session(aws_access_key_id= os.getenv("AWS_ACCESS_KEY_ID"), 
                          aws_secret_access_key= os.getenv("AWS_SECRET_ACCESS_KEY"),
                          region_name= os.getenv("AWS_REGION"))
  dynamodb = session.resource("dynamodb")
  table = dynamodb.Table(table_name)

  # create the items
  item = {
      "data_id": data_id,
      "user_id": user_id,
      "user_name": user_name,
      "image_url": image_url,
      "excel_url": excel_url,
      "upload_status": upload_status,
      'creation_date': creation_date or datetime.utcnow().isoformat()

      }
  # if additional attributes are added, updating item with key and value
  if additional_attributes:
    item.update(additional_attributes)

  try:
    response = table.put_item(Item=item)
    return {
        "success": True, 
        "message": "Item inputted successfully.",
        "item": item,
        "response": response
            }
  except Exception as e:
    return  {
        "success": False, 
        "message": "Item not inputted.",
        "item": item,
            }
        

def getting_records(table_name: str, days: int=7, gsi_name: str="CreationDateIndex"):
    """
    Fetching records from DynamoDB

    Args: table_name: str, days: int (default 7), gsi_name: str ("CreationDateIndex")
    Output: dict containing succ/fail, status message, pandas dataframe containing records
    """
    try:
      end_date = datetime.utcnow()
      start_date = end_date - timedelta(days=days)
      # initializing aws session and DynamoDB
      session = boto3.Session(aws_access_key_id= os.getenv("AWS_ACCESS_KEY_ID"), 
                              aws_secret_access_key= os.getenv("AWS_SECRET_ACCESS_KEY"),
                              region_name= os.getenv("AWS_REGION"))
      dynamodb = session.resource("dynamodb")
      table = dynamodb.Table(table_name)

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
      items = response.get("items", [])
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
          # convert to dataframe
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







