import streamlit as st

def init_slate_information():
    '''
    Initializes the slate record information
    '''
    if "slate_information" not in st.session_state:
        st.session_state.slate_information = {
            "site_name": "",
            "country_island": "",
            "team_leader": "",
            "data_recorded_by": "",
            "depth": "",
            "date": "",
            "time": ""
        }