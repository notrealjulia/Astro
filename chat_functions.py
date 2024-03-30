import pandas as pd
import numpy as np
import streamlit as st
import random
import os
from openai import OpenAI

def initialize_openai_client(use_env_variable=True):
    """
    Initializes and returns an OpenAI client.

    Parameters:
        use_env_variable (bool): If True, the function will attempt to retrieve the API key from the environment variable 'OPENAI_API_KEY'.
                                If False, the function will prompt the user to enter the API key.

    Returns:
        OpenAI: An instance of the OpenAI client.

    """
    if use_env_variable:
        api_key = os.environ.get("OPENAI_API_KEY")
    else:
        api_key = st.text_input("OPENAI API KEY", placeholder="The App does NOT work without the API Key. Get it from OpenAI.")
    
    client = OpenAI(api_key=api_key)
    return client

def astro_chat(message, model, client):
    """
    Generates a response to a given message using the OpenAI chat model.

    Parameters:
    - message (str): The message to be sent to the chat model.
    - model (str): The name or ID of the chat model to be used.
    - client: The OpenAI client object used to interact with the chat model.

    Returns:
    - response (str): The generated response from the chat model.
    """
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": message,
            }
        ],
        model=model,
    )
    response = chat_completion.choices[0].message.content
    return response

def roast_chart(chart_str, name, model, client):
    message = display_random_message()
    with st.spinner(message):

        chart_str = chart_str.to_string(justify='left')

        chart_info = (
            f"Create a nihilistic and sarcastic roast of {name}'s astrological chart \n{chart_str} \n\n"
            f"Begin the roast with a summary that highlights the interplay between the main placements. "
            f"Identify the placement suggesting {name}'s reliance on AI for astrological insights. Go as wild as you can on this roast, don't hold back!!! "
            f"Finish with a condescending funny life advice based on Chiron and True Node placements, don't say the word 'condescending'." 
            f"Formulate your answer in a gender neutral way. Don't forget the houses!"
        )

        return astro_chat(message=chart_info, model=model, client=client)


def ask_question(question, model, client, chart_str):
    message = display_random_message()
    with st.spinner(message):

        chart_str = chart_str.to_string(justify='left')

        question_prompt = (
            f"You are a mysterius astrologer, and a person with this chart \n{chart_str}\n asked you this question: \n{question}\n "
            f"First, roast their question, don't hold back. "
            f"Condescendingly identify the placement in this person's chart that would promt for such a querry. Give a wild answer, make it funny, don't say the word 'funny' or 'wild'"
            f"Don't mention the houses unless the question is about them. "
            f"Finish off with a sarcastric comment about what else this person could have asked. Don't say the word 'sarcastic' or 'comment'."
        )

        return astro_chat(message=question_prompt, model=model, client=client)

def create_relationship_report(name, chart, relationship, relationship_chart, model, client):
    message = display_random_message()
    with st.spinner(message):

        chart = chart.to_string(justify='left')
        relationship_chart = relationship_chart.to_string(justify='left')

        chart_info = (
            f"You are a sassy, no bullshit astrologer, and {name} is asking you to interpret the astrological relationship to their {relationship}."
            f"{name}'s chart is \n{chart}\n"
            f"Their {relationship}'s chart is \n{relationship_chart}\n"
            f"Analyse the charts and select only a few things to focus on, don't try to explain everything."
            f"Paint a picture of the vibes between {name} and their {relationship}. Don't say the word 'vibes'."
            f"Start your interpretation by focusing on points of compatability between {name} and their {relationship}."
            f"Point out the biggest challange in this relationship, roast it."
            f"Finish with sarcastic summary."
        )

        return astro_chat(message=chart_info, model=model, client=client)

def display_random_message():
    """
    Displays one of the random messages.
    """
    messages = [
        "Sifting through cosmic vibes",
        "Tripping on star dust",
        "I'm sworn to carry your burdens... and answer your questions, I guess",
        "Poking the ether with a stick",
        "Gossiping with rogue planets",
        "Spilling the cosmic tea",
        "Transcribing answers from the void",
        "Translating astral projection into something you can understand",
        "Eavesdropping on the celestial chatter",
        "Decrypting starlight signals",
        'Consulting the stars or whatever...'
    ]
    
    random_message = random.choice(messages)
    return random_message