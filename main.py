import streamlit as st
from openai import OpenAI
import os
import datetime
import kerykeion
from kerykeion import Report, AstrologicalSubject, KerykeionChartSVG
import pandas as pd
import numpy as np
from helper_functions import *
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

#######################################################COLLECT USER DETAILS#################################################################

logo = "icons/stars.png"
# Configure Streamlit page
st.set_page_config(
    page_title="ASTRO",
    page_icon=logo,
    layout="wide"
)
st.title('Very Real Astro Chatbot')

#client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY")) 
#if client is None:
#    st.error("API key not found. Please set the OPENAI_API_KEY environment variable.")
#else:
#    st.success("API key found.")

api_key = st.text_input("OPEN API KEY")
client = OpenAI(api_key=api_key)
selected_model = "gpt-4"  # Setting the default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = selected_model

# Checking if the selected model is available
#if selected_model is None:
#    st.error("Model not found")
#else:
#    st.success("Model found.")

#######################################################PAGE SETUP#################################################################
    
name = st.text_input("Your Astro Name")
date = st.date_input("Your Birth Date", min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today())
# Time input split into hours and minutes
col1, col2 = st.columns(2)  # Use st.columns in newer versions of Streamlit
with col1:
    hour = st.selectbox("Your time of Birth: Hour", range(24), format_func=lambda x: f"{x:02d}")
with col2:
    minute = st.selectbox("Minute", range(60), format_func=lambda x: f"{x:02d}")

# Combine hour and minute into a time object
time = datetime.time(hour, minute)
with col1:
    city = st.text_input("Your City of Birth")
with col2:
    nation = st.text_input("Your Country of Birth")

#!TODO find a different geo checker, this one has a strict limit on requests
def check_location(city, country):
    # Combine city and country for the query
    location_query = f"{city}, {country}"

    # Using Nominatim Geocoder
    geolocator = Nominatim(user_agent="Astrology_location_test")

    try:
        # Attempt to get location information
        location = geolocator.geocode(location_query)
        return location is not None
    except GeocoderTimedOut:
        return False
    
# Store the user details in the session state
st.session_state['astro_details'] = {
    'name': name,
    'birth_date': date,
    'birth_time': time,
    'city': city,
    'nation': nation
}

if st.button('Calculate Chart & Roast It'):
    # Check if the location is valid
    if check_location(city, nation):
        # Extracting year, month, day, hour, and minute from the date and time objects
        year = date.year
        month = date.month
        day = date.day
        hour = time.hour
        minute = time.minute

        with st.spinner('Consulting the stars or whatever...'):
            # Call the function with the parsed data inside the spinner context to ensure it shows while processing
            fullchart_df = create_fullchart_df(name=name, year=year, month=month, day=day, hour=hour, minute=minute, city=city, nation=nation)

            # Simulate a delay if `create_fullchart_df` is not a long-running operation
            # time.sleep(5)  # Only use if necessary to simulate processing time

            # Prepare the content to be displayed after processing
            chart_str = ('chart', fullchart_df.to_string(index=False, justify='left'))
            chart_info = (
                f"Create a nihilistic and sarcastic roast of {name}'s astrological chart, don't forget to include the houses. "
                f"Begin with a summary that highlights the interplay between placements. "
                f"Identify the placement suggesting {name}'s reliance on AI for astrological insights. Go as wild as you can on this roast, don't hold back!!! "
                f"Finish with a condescending funny life advice based on Chiron and True Node placements. "
                f"Chart details:\n{chart_str}"
            )

            # st.write(calculate_presence_percentages(fullchart_df))  # Uncomment if needed
            st.write(astro_chat(message=chart_info, model=selected_model, client=client))
            st.write('Astrological Chart for ', name)
            st.dataframe(fullchart_df)
    else:
        st.error("Location not found or invalid. Please enter a valid city and country.")



