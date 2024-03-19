import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
from kerykeion import Report, AstrologicalSubject
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

def get_compatibility(sign1, sign2, dataframe):
    """
    Returns the compatibility score between two signs.
    
    :param sign1: String, first astrological sign
    :param sign2: String, second astrological sign
    :param dataframe: DataFrame, the DataFrame containing the compatibility scores
    :return: Integer, compatibility score (returns None if not found)
    """
    # Ensure that sign1 and sign2 are in the same order as in the DataFrame
    if (sign1, sign2) not in zip(dataframe["Sign 1"], dataframe["Sign 2"]):
        # If not found, swap the signs
        sign1, sign2 = sign2, sign1
    
    # Query the DataFrame
    score = dataframe[(dataframe["Sign 1"] == sign1) & (dataframe["Sign 2"] == sign2)]["Compatibility Score"].values
    return score[0] if len(score) > 0 else None

def calculate_compatibility(person1_df, person2_df, compatibility_df):
    """
    Calculates the astrological compatibility between two individuals based on selected celestial bodies and a compatibility DataFrame.

    This function compares the astrological signs of the Sun, Moon, Mercury, Venus, and Mars placements from two different persons' 
    astrological charts and calculates the compatibility score for each placement. It then averages these scores to determine an overall compatibility score.

    :param person1_df: DataFrame, containing astrological placements and details for person 1
    :param person2_df: DataFrame, containing astrological placements and details for person 2
    :param compatibility_df: DataFrame, containing the compatibility scores between signs
    :return: Tuple, a DataFrame with individual compatibility scores and an overall compatibility score as a pandas Series
    """

    # Get the list of celestial bodies to compare
    bodies_to_compare = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars']
    
    # Calculate compatibility for each body and store the scores
    scores = []
    for body in bodies_to_compare:
        sign1 = person1_df.loc[person1_df['name'] == body, 'sign'].values[0]
        sign2 = person2_df.loc[person2_df['name'] == body, 'sign'].values[0]
        score = get_compatibility(sign1, sign2, compatibility_df)

        scores.append({
            'Placement': body,
            'Person1_Sign': sign1,
            'Person2_Sign': sign2,
            'Compatibility_Score': score
        })

    # Create a DataFrame for individual scores
    final_scores = pd.DataFrame(scores)
    # Calculate the overall average score
    overall_score = final_scores[['Compatibility_Score']].mean()

    # Return the DataFrame of scores and the overall score
    return final_scores, overall_score


""" # This function retrieves the compatibility score for a pair of signs
def get_compatibility(sign1, sign2, compatibility_data):
    # Find the compatibility score for the combination of sign1 and sign2
    compatibility_row = compatibility_data.loc[
        (compatibility_data['Sign 1'] == sign1) & (compatibility_data['Sign 2'] == sign2)
    ]
    # If the combination does not exist, try the opposite combination
    if compatibility_row.empty:
        compatibility_row = compatibility_data.loc[
            (compatibility_data['Sign 1'] == sign2) & (compatibility_data['Sign 2'] == sign1)
        ]
    # Return the compatibility score
    return compatibility_row['Compatibility Score'].values[0] """


def plot_compatibility_distribution(df, column='Compatibility Score'):
    """
    Plot the distribution of compatibility scores for zodiac sign pairs.

    This function takes a pandas DataFrame and a column name as input. It then plots a histogram 
    showing the distribution of the compatibility scores in the specified column.

    :param df: A pandas DataFrame containing zodiac compatibility data.
    :type df: pandas.DataFrame
    :param column: The name of the column in the DataFrame to plot. Defaults to 'Compatibility Score'.
    :type column: str
    """
    # Plotting the histogram
    plt.figure(figsize=(10, 6))
    plt.hist(df[column], edgecolor='black')
    
    # Adding titles and labels
    plt.title('Compatibility Score Distribution')
    plt.xlabel('Compatibility Score')
    plt.ylabel('Number of Zodiac Sign Pairs')
    
    # Showing the plot
    plt.show() 

def create_fullchart_df(name, year, month, day, hour, minute, city, nation):
    """
    Create a DataFrame representing the full astrological chart of a person.

    Parameters:
    - name: str - The name of the person.
    - year: int - The year of birth.
    - month: int - The month of birth.
    - day: int - The day of birth.
    - hour: int - The hour of birth.
    - minute: int - The minute of birth.
    - city: str - The city of birth.
    - nation: str - The nation of birth.

    Returns:
    - fullchart_df: DataFrame - A DataFrame with the astrological chart information.
    """
    # Instantiate an AstrologicalSubject object
    person = AstrologicalSubject(name=name, year=year, month=month, day=day, 
                                 hour=hour, minute=minute, city=city, nation=nation)

    # Retrieve the list of planet objects
    fullchart = person.planets_list

    # Convert each object in the list to a dictionary
    list_of_dicts = [
        {attr: getattr(obj, attr) for attr in dir(obj)
         if not attr.startswith('__') and not callable(getattr(obj, attr))}
        for obj in fullchart
    ]

    # Create a DataFrame from the list of dictionaries
    fullchart_df = pd.DataFrame(list_of_dicts)

        # Mapping dictionaries
    sign_elements = {
        'Ari': 'Fire', 'Leo': 'Fire', 'Sag': 'Fire',
        'Tau': 'Earth', 'Vir': 'Earth', 'Cap': 'Earth',
        'Gem': 'Air', 'Lib': 'Air', 'Aqu': 'Air',
        'Can': 'Water', 'Sco': 'Water', 'Pis': 'Water'
    }

    sign_qualities = {
        'Ari': 'Cardinal', 'Can': 'Cardinal', 'Lib': 'Cardinal', 'Cap': 'Cardinal',
        'Tau': 'Fixed', 'Leo': 'Fixed', 'Sco': 'Fixed', 'Aqu': 'Fixed',
        'Gem': 'Mutable', 'Vir': 'Mutable', 'Sag': 'Mutable', 'Pis': 'Mutable'
    }

            # Add the ascendant information as a new row
    ascendant_info = {
        'name': 'Ascendant',
        'sign': person.first_house['sign'],
        'house': 1,  # Ascendant is always associated with the 1st house
        'element': sign_elements.get(person.first_house['sign'], None),  # Retrieve element based on the sign
        'quality': sign_qualities.get(person.first_house['sign'], None),  # Retrieve quality based on the sign
        'position': person.houses_degree_ut[0],  # The degree of the ascendant
        'retrograde': False  # The ascendant is not a planet and thus cannot be retrograde
    }
    fullchart_df = pd.concat([fullchart_df, pd.DataFrame([ascendant_info])], ignore_index=True)
        # Mapping dictionary
    house_to_number = {
        'First_House': 1,
        'Second_House': 2,
        'Third_House': 3,
        'Fourth_House': 4,
        'Fifth_House': 5,
        'Sixth_House': 6,
        'Seventh_House': 7,
        'Eighth_House': 8,
        'Ninth_House': 9,
        'Tenth_House': 10,
        'Eleventh_House': 11,
        'Twelfth_House': 12
    }

    # Replace the string house names with numbers
    fullchart_df['house'] = fullchart_df['house'].replace(house_to_number)
    # Mapping dictionary for zodiac signs
    sign_full_names = {
        'Ari': 'Aries',
        'Tau': 'Taurus',
        'Gem': 'Gemini',
        'Can': 'Cancer',
        'Leo': 'Leo',
        'Vir': 'Virgo',
        'Lib': 'Libra',
        'Sco': 'Scorpio',
        'Sag': 'Sagittarius',
        'Cap': 'Capricorn',
        'Aqu': 'Aquarius',
        'Pis': 'Pisces'
    }

    # Replace the abbreviated sign names with full names
    fullchart_df['sign'] = fullchart_df['sign'].replace(sign_full_names)

    fullchart_df = fullchart_df.drop([7, 8, 9, 10]).reset_index(drop=True)

    #fullchart_df = fullchart_df[['name', 'sign', 'house', 'element', 'quality', 'position', 'retrograde']]
    fullchart_df = fullchart_df[['name', 'sign', 'house']]

    
    return fullchart_df

def calculate_presence_percentages(df):
    """
    Calculates the percentage presence of astrological signs, houses, elements, and qualities in a DataFrame.

    This function analyzes the distribution of astrological characteristics in a given DataFrame and computes 
    the percentage representation of each unique sign, house, element, and quality. 
    It provides insight into the dominance or rarity of these characteristics within the dataset.

    :param df: DataFrame, the DataFrame containing astrological data with columns 'sign', 'house', 'element', and 'quality'
    :return: Dictionary, with keys 'Sign Percentages', 'House Percentages', 'Element Percentages', and 'Quality Percentages' containing rounded percentage values
    
    Note: The house numbers can be mapped to house names if a dictionary with the mapping is provided.
    """

    # Calculate total number of points to get percentages
    total_points = len(df)

    # Calculate percentage presence for signs
    sign_counts = df['sign'].value_counts()
    sign_percentages = (sign_counts / total_points) * 100

    # Calculate percentage presence for houses
    house_counts = df['house'].value_counts()
    house_percentages = (house_counts / total_points) * 100

    # Calculate percentage presence for elements
    element_counts = df['element'].value_counts()
    element_percentages = (element_counts / total_points) * 100

    # Calculate percentage presence for qualities
    quality_counts = df['quality'].value_counts()
    quality_percentages = (quality_counts / total_points) * 100

    # Combine the results into a single dictionary
    percentages = {
        'Sign Percentages': np.round(sign_percentages, decimals=1),
        'House Percentages': np.round(house_percentages, decimals=1),
        'Element Percentages': np.round(element_percentages, decimals=1),
        'Quality Percentages': np.round(quality_percentages, decimals=1)
    }

    for category, series in percentages.items():
        df = pd.DataFrame(series).reset_index()
        df.columns = ['Category', 'Percentage']
        output = print(f"{category}:\n{df.to_string(index=False)}\n")

    return output

def check_location(city, country):
    # Combine city and country for the query
    location_query = f"{city}, {country}"

    # Using Nominatim Geocoder
    geolocator = Nominatim(user_agent="geoapiExercises")

    try:
        # Attempt to get location information
        location = geolocator.geocode(location_query)
        return location is not None
    except GeocoderTimedOut:
        return False

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