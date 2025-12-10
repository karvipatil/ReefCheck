from typing import Optional
from datetime import datetime
import boto3
import streamlit as st
import os

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
          
