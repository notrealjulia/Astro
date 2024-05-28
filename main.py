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
st.write(":violet[__Believe in astrology? Me neither... yet here we are, letting Zazatron dissect our astral fates as if the Universe and AI had nothing better to do than throw shade at our bad decisions.__] \n\n :blue[_None of your data is stored, it goes 'poof' as soon as you close the browser_]")
st.write(" ")
st.write(" ")

#Change to True to use the system variable OPENAI_API_KEY
client = initialize_openai_client(use_env_variable=True)

selected_model = "gpt-4o"  # Setting the default model
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

name_relationship = None
date_relationship = None

st.session_state['astro_details_relationship'] = {
    'name_relationship': name_relationship,
    'date_relationship': date_relationship
}

#Page setup
chart, roast, relationships, questions, = st.columns(4)

if "tab_selected" not in st.session_state:
    st.session_state["tab_selected"] = None

with chart:
    st.button(":violet[Reveal Your Astrological Chart]", use_container_width=True, key="Chart", on_click=lambda: 
              st.session_state.update({"tab_selected": "Chart"}), type="primary" if st.session_state["tab_selected"] == "Chart" else "secondary")        
with roast:
    st.button(":violet[Roast My Chart]", use_container_width=True, key="Roast", on_click=lambda: 
              st.session_state.update({"tab_selected": "Roast"}), type="primary" if st.session_state["tab_selected"] == "Roast" else "secondary")
with relationships:
    st.button(":violet[Compatibility Calculator]", use_container_width=True, key="Compatibility", on_click=lambda: 
              st.session_state.update({"tab_selected": "Compatibility"}) , type="primary" if st.session_state["tab_selected"] == "Compatibility" else "secondary")
with questions:
    st.button(":violet[Ask Zazatron a Question]", use_container_width=True, key="Question", on_click=lambda: 
              st.session_state.update({"tab_selected": "Question"}), type="primary" if st.session_state["tab_selected"] == "Question" else "secondary") 
 

#TAB SELECTION 1
if st.session_state["tab_selected"] == "Chart":
    st.subheader(f"{name}'s Astrological Chart")
    if 'chart_output' not in st.session_state or \
       (name, date, time, city, nation) != st.session_state.get('last_astro_details', (None, None, None, None, None)):

        # Generate the astrological chart and save it to the session state
        fullchart_df = create_fullchart_df(name=name, date=date, time=time, city=city, nation=nation)
        st.session_state['chart_output'] = fullchart_df

        # Update the last known user details in the session state
        st.session_state['last_astro_details'] = (name, date, time, city, nation)

    # Display the astrological chart from the session state
    st.write(st.session_state['chart_output'])

#TAB SELECTION 2
if st.session_state["tab_selected"] == "Roast":
     # Display a message if the astrological chart is not yet generated
    if 'chart_output' not in st.session_state or \
       (name, date, time, city, nation) != st.session_state.get('last_astro_details', (None, None, None, None, None)):

        # Generate the astrological chart and save it to the session state
        fullchart_df = create_fullchart_df(name=name, date=date, time=time, city=city, nation=nation)
        st.session_state['chart_output'] = fullchart_df

        # Update the last known user details in the session state
        st.session_state['last_astro_details'] = (name, date, time, city, nation)
    else:
        # Only generate and save the roast if it hasn't been done yet or if user details have changed
        if 'chart_roast' not in st.session_state or \
           (name, date, time, city, nation) != st.session_state.get('last_astro_details', (None, None, None, None, None)):
            
            # Generate the roast and save it to the session state
            roast = roast_chart(chart_str=st.session_state['chart_output'], name=name, model=selected_model, client=client)
            st.session_state['chart_roast'] = roast

        # Display the roast from the session state
        st.write(st.session_state['chart_roast'])

#TAB SELECTION 3
if st.session_state["tab_selected"] == "Compatibility":
    if 'chart_output' not in st.session_state or \
       (name, date, time, city, nation) != st.session_state.get('last_astro_details', (None, None, None, None, None)):

        # Generate the astrological chart and save it to the session state
        fullchart_df = create_fullchart_df(name=name, date=date, time=time, city=city, nation=nation)
        st.session_state['chart_output'] = fullchart_df

        # Update the last known user details in the session state
        st.session_state['last_astro_details'] = (name, date, time, city, nation)

    st.subheader("Can the stars explain my relationships?")
    # User Input
    col00, col01 = st.columns(2)
    with col00:
        name_relationship = st.text_input("Describe who this person is to you: _parent, sibling, friend, partner, lover, crush, tinder match, enemy, boss, minion, pet, etc._", key="relationship_name")
    with col01:
        date_relationship = st.date_input("When is their birthday?", key="relationship_date", min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today())

    # Define a key to identify the current relationship uniquely
    current_relationship_key = (name_relationship, str(date_relationship))

    # Generate and display the relationship report when the button is clicked
    # and input details have changed or the report does not exist
    if st.button(":violet[Calculate Compatibility]"):
        if 'last_relationship_key' not in st.session_state or \
           st.session_state['last_relationship_key'] != current_relationship_key or \
           'relationship_report' not in st.session_state:
            
            fullchart_relationship = create_fullchart_df(name=name_relationship, date=date_relationship, time=datetime.time(12, 00), city='London', nation='UK')
            # Assuming the necessary adjustment for the DataFrame is handled within `create_fullchart_df`
            fullchart_relationship = fullchart_relationship.drop(index=[9], columns=['house']) #drop the assendant row and houses
            relationship_report = create_relationship_report(name=name, chart=st.session_state['chart_output'], relationship=name_relationship, relationship_chart=fullchart_relationship, model=selected_model, client=client)
            
            st.session_state['relationship_report'] = relationship_report
            st.session_state['last_relationship_key'] = current_relationship_key


    # Display the saved relationship report if it exists
    if 'relationship_report' in st.session_state:
        st.write(st.session_state['relationship_report'])

#TAB SELECTION 4
if st.session_state["tab_selected"] == "Question":
    if 'chart_output' not in st.session_state or \
       (name, date, time, city, nation) != st.session_state.get('last_astro_details', (None, None, None, None, None)):

        # Generate the astrological chart and save it to the session state
        fullchart_df = create_fullchart_df(name=name, date=date, time=time, city=city, nation=nation)
        st.session_state['chart_output'] = fullchart_df

        # Update the last known user details in the session state
        st.session_state['last_astro_details'] = (name, date, time, city, nation)    

    user_question = st.text_input(" ", placeholder="Your Question for the AI Clairvoyant")

    # Check if the 'Ask the Question' button is clicked
    if st.button(":violet[Ask the Question]"):
        if 'chart_output' not in st.session_state:
            st.subheader(":orange[Please reveal your Astrological Chart before Zazatron amswer your questions.]")
        # Check if the question has changed from the last one or if it's the first question being asked
        if 'last_question' not in st.session_state or user_question != st.session_state['last_question']:
            # Call the function to get the AI's answer for the new question
            ai_answer = ask_question(user_question, model=selected_model, client=client, chart_str=st.session_state['chart_output'])
            
            # Save the new question and its answer to the session state
            st.session_state['last_question'] = user_question
            st.session_state['last_answer'] = ai_answer
        else:
            # If the question hasn't changed, use the last saved answer
            ai_answer = st.session_state['last_answer']
        
        # Display the answer (either newly generated or fetched from the session state)
        st.write(ai_answer)
    elif 'last_answer' in st.session_state:
        # If there's a stored answer but the button wasn't clicked, display the last answer
        st.write(st.session_state['last_answer'])
