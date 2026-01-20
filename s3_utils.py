import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import streamlit as st
import os

os.environ["AWS_ACCESS_KEY_ID"] = st.secrets["aws"]["AWS_ACCESS_KEY"]
os.environ["AWS_SECRET_ACCESS_KEY"] = st.secrets["aws"]["AWS_SECRET_KEY"]
os.environ["AWS_REGION"] = st.secrets["aws"]["REGION_NAME"]
os.environ["AWS_BUCKET_NAME"] = st.secrets["aws"]["AWS_BUCKET_NAME"]

# AWS S3 utilities
def upload_to_s3(file_path: str, s3_key: str) -> str:
    """
    Uploads a file to AWS S3 bucket.
    
    Args:
        bucket_name: Name of the S3 bucket
        file_path: Local path to the file to upload
        s3_key: Destination key/path in the bucket
        aws_access_key: AWS access key
        aws_secret_key: AWS secret key
        region_name: AWS region (default: us-east-1)
        
    Returns:
        bool: True if upload was successful, False otherwise
    """
    try:
        # Initialize S3 client
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
            region_name=os.environ["AWS_REGION"]
        )
        
        # Upload the file
        s3.upload_file(
            file_path, 
            os.environ["AWS_BUCKET_NAME"], 
            s3_key,
            ExtraArgs={'ACL': 'public-read'}
        )
        print(f"File {file_path} uploaded to s3://{os.environ['AWS_BUCKET_NAME']}/{s3_key}")
        # create the object url
        object_url = f"https://{os.environ['AWS_BUCKET_NAME']}.s3.{os.environ['AWS_REGION']}.amazonaws.com/{s3_key}"
        return object_url
        
    except FileNotFoundError:
        print(f"The file {file_path} was not found")
        return None
    except NoCredentialsError:
        print("AWS credentials not available")
        return None
    except PartialCredentialsError:
        print("Incomplete AWS credentials")
        return None
    except Exception as e:
        print(f"Error uploading file to S3: {str(e)}")
        return None


def download_from_s3(s3_key: str, local_path: str) -> bool:
    """
    Downloads a file from AWS S3 bucket.
    
    Args:
        bucket_name: Name of the S3 bucket
        s3_key: Source key/path in the bucket
        local_path: Local path to save the downloaded file
        aws_access_key: AWS access key
        aws_secret_key: AWS secret key
        region_name: AWS region (default: us-east-1)
        
    Returns:
        bool: True if download was successful, False otherwise
    """
    try:
        # Initialize S3 client
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
            region_name=os.environ["AWS_REGION"]
        )
        
        # Download the file
        s3.download_file(os.environ["AWS_BUCKET_NAME"], s3_key, local_path)
        print(f"File downloaded from s3://{os.environ['AWS_BUCKET_NAME']}/{s3_key} to {local_path}")
        return True
        
    except NoCredentialsError:
        print("AWS credentials not available")
        return False
    except PartialCredentialsError:
        print("Incomplete AWS credentials")
        return False
    except Exception as e:
        print(f"Error downloading file from S3: {str(e)}")
        return False


def upload_bucket_path(user_name: str, user_id:str, type_: str, slate_type: str, data_id: str) -> str:
    user_names = user_name.split(" ")
    user_name_ = "_".join(user_names)

    if type_ == 'image':
        return f"{os.environ["ENV"]}/{slate_type}/{user_name_}_{user_id}/images/{data_id}.png"
    elif type_ == 'excel':
        return f"{os.environ["ENV"]}/{slate_type}/{user_name_}_{user_id}/excel/{data_id}.xlsx"