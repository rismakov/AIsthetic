import io
import os
import numpy as np
import pandas as pd
import random
import streamlit as st
import streamlit.components.v1 as components

from numpy import asarray
from PIL import Image

from clothing_nodes import MATCHES
from constants import GCP_PROJECTID, CREDS, CLOSET_SET, LOCATION
from get_weather import get_projected_weather
from matching_utils import get_viable_matches
from match_constants import CATEGORIES, MATCH_GROUPS
from category_constants import (
    ACCESSORIES, MAIN_CATEGORIES, OCCASION_TAGS, STYLE_TAGS, WEATHER_ICON_MAPPING
)
from utils import get_filesnames_in_dir
from utils_constants import PATH_CLOSET

# References:
# https://daleonai.com/social-media-fashion-ai

IMAGE_SIZE = (96, 96) # (224, 224)

OUTFIT_COLS = [0, 2, 4, 0, 2, 4]

}


def choose_outfit_type(include_accessories=True) -> list:
    """Choose outfit combination type and return outfit categories.

    Can either choose top + bottom combo, or dress/set combo.

    Returns
    -------
    List(str)
    """
    choice = random.randint(1, 5)  # determine this value

    additional_categories = ACCESSORIES if include_accessories else []

    if choice != 1:
        categories = [x for x in MAIN_CATEGORIES if x not in ('dresses')]
        return categories + additional_categories

    categories = [x for x in MAIN_CATEGORIES if x not in ('tops', 'bottoms')]
    return categories + additional_categories


def choose_outfit(
    weather, 
    occasion, 
    include_accessories=True,
    exclude_items={},
):
    """
    Returns
    -------
    dict
    """
    categories = choose_outfit_type(include_accessories)

    outfit_pieces = {}
    for cat in categories:
        directory = f'{PATH_CLOSET}/{cat}'
        options = sorted(get_filesnames_in_dir(directory))
        ind_options = [
            i for i, x in enumerate(options) 
            if f'{directory}/{x}' not in exclude_items.get(cat, [])
        ]
        
        if cat == 'bottoms':
            # get possible options from the matches for the chosen `top` choice
            ind_options = [
                i for i in ind_options if i + 1 in MATCHES[choice_int + 1]
            ]
        elif cat == 'shoes':
            ind_options = [
                i for i, x in enumerate(options) 
                if OCCASION_TAGS[occasion] in x.split('.')[0]
            ]
        elif cat == 'outerwear' and weather in ('Hot', 'Warm'):
            continue

        choice_int = random.choice(ind_options)
        
        filename = f'{directory}/{options[choice_int]}'
        outfit_pieces[cat] = filename

    return outfit_pieces


def display_outfit_pieces(outfit_pieces: dict):
    cols = st.beta_columns(6)
    for i, filename in zip(OUTFIT_COLS, outfit_pieces.values()):
        cols[i].image(filename, width=250)
    st.button("This doesn't match together.")


def get_weather_icon_filename(weather_type, weather):
    if weather_type == 'Really Cold':
        return WEATHER_ICON_MAPPING['Really Cold']
    if weather_type == 'Rainy':
        return WEATHER_ICON_MAPPING['Rainy']
    return WEATHER_ICON_MAPPING.get(weather, 'cloudy.png')


def init_most_recently_worn():
    categories = ['tops', 'bottoms', 'dresses', 'outerwear']
    return {cat: [] for cat in categories} 


def update_most_recently_worn(outfit_pieces, recently_worn):
    categories = ['tops', 'bottoms', 'dresses', 'outerwear']
    cadences = [5, 5, 9, 1]
    for cat, cadence in zip(categories, cadences):
        recently_worn[cat] = (
            [outfit_pieces.get(cat, '')] + recently_worn[cat]
        )[:cadence]
    return recently_worn

def display_outfit_plan(
    weather_info, occasion, num_days, amount, include_accessories, days_in_week=7
):   
    num_cols = 3

    recently_worn = init_most_recently_worn()
    for n in range(num_days):
        if n % days_in_week == 0:
            st.header(f'Week {int((n / days_in_week)) + 1}')
            cols = st.beta_columns(num_cols)
            col_i = 0
        
        temp, weather, weather_type = (x[n] for x in weather_info)

        outfit_pieces = choose_outfit(
            weather_type, 
            occasion, 
            include_accessories, 
            exclude_items=recently_worn,
        ) 
        recently_worn = update_most_recently_worn(outfit_pieces, recently_worn)

        cols[col_i].subheader(f'Day {n + 1}')
        weather_text = f'{weather} - {temp}° ({weather_type})'
        weather_icon_filename = get_weather_icon_filename(weather_type, weather)

        cols[col_i].image(f'icons/weather/{weather_icon_filename}', width=30)
        cols[col_i].text(weather_text)
        cols[col_i].image([v for _, v in outfit_pieces.items()], width=70)

        cols[col_i].markdown("""---""")

        if col_i in list(range(num_cols - 1)):
            col_i += 1
        else:
            col_i = 0
