import streamlit as st


st.title("Reefcheck Analyzer")


if not st.user.is_logged_in:
    if st.sidebar.button("Login", type="primary", icon=":material/login:"):
        st.login

else:
    if st.sidebar.button("Log out", type="secondary", icon=":material/logout:"):
        st.logout()
        st.stop()

