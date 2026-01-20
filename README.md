# ReefCheck

Conversation opened. 1 unread message.

Skip to content
Using Gmail with screen readers
1 of 9,349
Readme
Inbox
Summarize this email

Madhuri Patil
Attachments
1:35 AM (0 minutes ago)
to me


 One attachment
  •  Scanned by Gmail
# ReefCheck Analyzer

A Streamlit-based web application for digitizing and analyzing underwater reef survey slates using AI-powered image recognition.

## Overview

ReefCheck Analyzer automates the process of extracting data from handwritten reef monitoring slates used by divers. It uses GPT-4o vision capabilities to read substrate observations and fish/invertebrate counts from uploaded slate images, converting them into structured Excel files.

## Features

- **Substrate Slate Processing**: Extract substrate observations (hard coral, rubble, sand, etc.) from 4-segment distance slates
- **Fish & Invertebrate Slate Processing**: Digitize fish counts, invertebrate observations, coral disease, and rare animal sightings
- **Google OAuth Authentication**: Secure login with Google accounts
- **Cloud Storage**: Automatic upload of images and Excel files to AWS S3
- **Admin Dashboard**: Analytics and reporting for uploaded data with visualizations
- **Editable Results**: Review and correct AI-extracted data before saving

## Tech Stack

- **Frontend**: Streamlit
- **AI/ML**: OpenAI GPT-4o, LangChain
- **Cloud**: AWS S3 (storage), AWS DynamoDB (database)
- **Authentication**: Google OAuth via Streamlit's OIDC support

## Project Structure

```
ReefCheck/
├── login.py                 # Main entry point with authentication
├── pages/
│   ├── 00_substrate_slate.py    # Substrate slate processing page
│   ├── 01_fish_invert_slate.py  # Fish/invertebrate slate processing
│   └── 02_Admin_Panel.py        # Admin analytics dashboard
├── llm.py                   # OpenAI/LangChain integration
├── prompt.py                # AI prompts for slate extraction
├── db_utils.py              # DynamoDB operations
├── s3_utils.py              # S3 upload utilities
├── utils.py                 # Data processing and Excel generation
├── visualization.py         # Plotly charts for admin dashboard
├── session_records.py       # Streamlit session state management
└── requirements.txt         # Python dependencies
```

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd ReefCheck
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure secrets

Create `.streamlit/secrets.toml` with your credentials:

```toml
[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "your-random-secret-string"
client_id = "your-google-oauth-client-id"
client_secret = "your-google-oauth-client-secret"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"

[llm]
LANGCHAIN_TRACING_V2 = "true"
LANGCHAIN_API_KEY = "your-langchain-api-key"
LANGCHAIN_ENDPOINT = "https://api.smith.langchain.com"
LANGCHAIN_PROJECT = "your-project-name"
OPENAI_API_KEY = "your-openai-api-key"

[aws]
ENV = "dev"
AWS_REGION = "us-east-1"
AWS_ACCESS_KEY_ID = "your-aws-access-key"
AWS_SECRET_ACCESS_KEY = "your-aws-secret-key"
AWS_BUCKET_NAME = "your-s3-bucket-name"

[admin]
ADMIN_USERS = ["admin@example.com"]
```

### 5. AWS Setup

- Create an S3 bucket with public read access for uploaded files
- Create a DynamoDB table named `{ENV}-reefcheck` with:
  - Partition key: `data_id` (String)
  - GSI `CreationDateIndex` with partition key `status` and sort key `creation_date`

### 6. Run the application

```bash
streamlit run login.py
```

The app will be available at `http://localhost:8501`

## Usage

1. **Login**: Click the Login button and authenticate with Google
2. **Upload Slate**: Navigate to Substrate Slate or Fish Invert Slate page
3. **Process Image**: Upload a photo of your reef survey slate
4. **Review Data**: Edit the AI-extracted data in the interactive table
5. **Save**: Enter a filename and click Save to upload to cloud storage
6. **Download**: Download the generated Excel file for your records

## Admin Panel

Accessible only to users listed in `ADMIN_USERS`. Displays:
- Daily upload trends
- Uploads by user
- Recent upload history with links to files

## License

MIT
README.md
Displaying README.md.