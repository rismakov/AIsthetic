import streamlit as st


def weather_info_not_found_message():
    st.error(
        "ERROR: Weather information not found. Confirm that city and country "
        "names are filled in and spelled correctly."
    )
