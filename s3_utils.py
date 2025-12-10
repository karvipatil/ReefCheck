import os
import boto3
from botocore.session import PartialCredentialsError
from boto3.session import NoCredentialsError
import streamlit as st


os.environ["AWS_REGION"] = st.secrets['aws']['AWS_REGION']
os.environ["AWS_SECRET_ACCESS_KEY"] = st.secrets['aws']["AWS_SECRET_ACCESS_KEY"]
os.environ["AWS_ACCESS_KEY_ID"] = st.secrets['aws']["AWS_ACCESS_KEY_ID"]
os.environ["AWS_BUCKET_NAME"] = st.secrets['aws']["AWS_BUCKET_NAME"]



def upload_to_s3(file_path: str, s3_key: str):
  """
  Uploading the file to AWS s3 bucket

  Args: file_path, s3_key
  Outputs: object_url
  
  
  """
  try:
    # initialize s3 client
    s3 = boto3.client('s3',
                      region_name=os.environ["AWS_REGION"],
                      aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"], 
                      aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"] 
                      )
    
    # upload file
    s3.upload_file(file_path, os.environ["AWS_BUCKET_NAME"], s3_key, ExtraArgs={'ACL': 'public-read'})
    print(f"File: {file_path} uploaded to s3://{os.environ['AWS_BUCKET_NAME']}/{s3_key}")
    # creating object url
    object_url = f"https://{os.environ['AWS_BUCKET_NAME']}.s3.{os.environ['AWS_REGION']}.amazonaws.com/{s3_key}"
    return object_url


  except FileNotFoundError:
    print(f"The file, {file_path}, has not been found")
    return None
  
  except NoCredentialsError:
    print(f"The credentials for the file, {file_path}, are not available.")
    return None
  
  except PartialCredentialsError:
    print(f"The credentials for the file, {file_path}, are only partially available.")
    return None
  
  except Exception as e: 
    print(f"Error when uploading the file, {str(e)}")
    return None


def upload_bucket_path(user_name: str, user_id:str, type_: str, slate_type: str, data_id: str) -> str:
    """
    Returning the bucket path to the user

    Args: user_name, user_id, type, slate_type, data_id
    Outputs: bucket path
    
    """
    user_names = user_name.split(" ")
    user_name_ = "_".join(user_names)
    if type_ == 'image':
        return f"{os.environ['ENV']}/{slate_type}/{user_name_}_{user_id}/images/{data_id}.png"
    elif type_ == 'excel':
        return f"{os.environ['ENV']}/{slate_type}/{user_name_}_{user_id}/excel/{data_id}.xlsx"
    
