import streamlit as st
import os

from db_utils import get_recent_records
from visualization import display_upload_analytics
import pandas as pd

# Set page configuration
st.set_page_config(
    page_title="ReefCheck Admin",
    page_icon="📊",
    layout="wide"
)

# enivironment variables
os.environ["ENV"] = st.secrets["aws"]["ENV"]

# environment variables
admin_users = st.secrets["admin"]["ADMIN_USERS"]
DB_TABLE_NAME = f"{os.environ['ENV']}-reefcheck"

# Authentication
if not st.experimental_user.is_logged_in:
    st.error("🔒 Please log in to access this page.")
    st.stop()

if st.experimental_user['email'] not in admin_users:
    st.error("⛔ You are not authorized to access this page.")
    st.stop()

# Sidebar with filters
with st.sidebar:
    st.title("Admin Controls")
    st.write(f"Welcome, {st.experimental_user['name']} 👋")
    days_to_show = st.slider(
        "Show data for last (days):",
        min_value=7,
        max_value=90,
        value=30,
        step=7
    )
    st.markdown("---")
    st.caption(f"Logged in as: {st.experimental_user['email']}")

# Main content
st.title("ReefCheck Admin Dashboard")

# Get recent records
with st.spinner("Loading upload data..."):
    recent_records = get_recent_records(DB_TABLE_NAME, days=days_to_show)
if recent_records['success']:
    if recent_records['data'] is not None and not recent_records['data'].empty:
        st.toast("✅ Data loaded successfully")
        # Display the analytics dashboard
        display_upload_analytics(recent_records['data'], days=days_to_show)
    else:
        st.info("ℹ️ No recent uploads found in the selected date range.")
else:
    st.error(f"❌ Failed to load data: {recent_records['message']}")

# Add some custom CSS for better appearance
st.markdown("""
<style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0 0;
        gap: 1rem;
        padding: 0.5rem 1rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e6f0ff;
    }
</style>
""", unsafe_allow_html=True)
