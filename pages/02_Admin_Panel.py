import streamlit as st
import os
from datetime import time
from db_utils import getting_records




# set up page configuration
st.set_page_config(
    page_title="Admin Page",
    layout="wide",
    page_icon="📊"
)

# creating environment
os.environ['ENV'] = st.secrets["aws"]["ENV"]
# database table name
DB_TABLE_NAME = f"{os.environ['ENV']}-reefcheck"
admin_users = st.secrets["admin"]["ADMIN_USERS"]


# check authentication
if not st.user.is_logged_in:
    st.error("Please log in.")
    st.stop()

if st.user.email not in admin_users:
    st.error("Please enter an email.")
    st.stop()

# selecting by week to display data
with st.sidebar:
    st.title("Admin Panel")
    st.header(f"Welcome, {st.user['name']}")
    week_slider = st.slider(
        "Please select the number of days to show the data:",
        min_value = 7,
        max_value = 90,
        value = 30,
        step = 7
        )
    st.markdown("---")
    st.caption(f"Logged in as: {st.user['email']}")

st.title("ReefCheck Admin Dashboard")

with st.spinner("Loading..."):
    data_records = getting_records(DB_TABLE_NAME, days=week_slider)

if data_records["success"]: 
    if data_records["data"] is not None and not data_records["data"].empty:
        st.toast("✅ Data has been saved")
        # display analytics dashboard
        # displaying_loaded_analytics()
    else:
        st.error("❌ No recent uploads found in the given range.")
else:
    st.error(f"Data has failed to load: {data_records['message']}")

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
            