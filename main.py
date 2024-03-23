import streamlit as st
from openai import OpenAI
import os
import datetime
import kerykeion
from kerykeion import Report, AstrologicalSubject, KerykeionChartSVG
import pandas as pd
import numpy as np
from astro_functions import *
from chat_functions import *
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

#Page setup
logo = "icons/stars.png"

st.set_page_config(
    page_title="ASTRO",
    page_icon=logo,
    layout="wide"
)
st.title(':violet[Zazatron]')
st.write(":violet[__Embrace Saturn's Shade and Talk to the AI-Cosmos When Humans r 2 smol__] \n\n :blue[_None of your data is stored, it goes 'poof' as soon as you close the browser_]")
st.write(" ")
st.write(" ")

#Change to True to use the system variable OPENAI_API_KEY
client = initialize_openai_client(use_env_variable=False)

selected_model = "gpt-4"  # Setting the default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = selected_model

#User Input
col00, col01 = st.columns(2)
with col00:
    name = st.text_input("Your Astro Name")
with col01:
    date = st.date_input("Your Birth Date", min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today())

col1, col2, col3, col4 = st.columns(4)  # Use st.columns in newer versions of Streamlit
with col1:
    hour = st.selectbox("Your time of Birth: Hour", range(24), format_func=lambda x: f"{x:02d}")
with col2:
    minute = st.selectbox("Minute", range(60), format_func=lambda x: f"{x:02d}")
with col3:
    city = st.text_input("Your City of Birth")
with col4:
    nation = st.text_input("Your Country of Birth")

time = datetime.time(hour, minute)
    
# Store the user details in the session state
st.session_state['astro_details'] = {
    'name': name,
    'date': date,
    'time': time,
    'city': city,
    'nation': nation
}

# Initialize the session state for the Buttons
if 'chart_button' not in st.session_state:
    st.session_state['chart_button'] = False
if 'roast_button' not in st.session_state:
    st.session_state['roast_button'] = False
if 'question_button' not in st.session_state:
    st.session_state['question_button'] = False

# Initialize the session state for the out from Zazatron
if 'chart_output' not in st.session_state:
    st.session_state['chart_output'] = None
if 'chart_roast' not in st.session_state:
    st.session_state['chart_roast'] = None

# Sequential buttons

# Calculate the astrological chart when the "Reveal Astrological Chart" button is clicked
if st.button(':violet[Reveal Your Astrological Chart]'):
    st.session_state['chart_button'] = True
    fullchart_df = create_fullchart_df(name=name, date=date, time=time, city=city, nation=nation)
    st.session_state['chart_output'] = fullchart_df

# Display the astrological chart and enable the "Roast My Chart" button
if st.session_state['chart_output'] is not None:
    st.write('Astrological Chart for ', name)
    st.write(st.session_state['chart_output'])

# "Roast My Chart" button is pressed and the roast is saved in the session state
if st.session_state['chart_button']:
    st.session_state['roast_button'] = True
    if st.button(":violet[This doesn't look like anything to me... Roast My Chart!]"):
        #print(st.session_state['chart_output'])
        roast = roast_chart(chart_str=st.session_state['chart_output'], name=name, model=selected_model, client=client)
        st.session_state['chart_roast'] = roast

# When the roast is displayed  enable the "Ask the Question" button
if st.session_state['chart_roast'] is not None:
    st.write(st.session_state['chart_roast'])
    st.session_state['question_button'] = True
    user_question = st.text_input(" ", placeholder="Your question for the AI Clairvoyant")
    if st.button(":violet[Ask the Question]"):
        ai_answer = ask_question(user_question, model=selected_model, client=client, chart_str=st.session_state['chart_output'])
        st.write(ai_answer)