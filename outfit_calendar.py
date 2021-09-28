import random
import streamlit as st

from category_constants import (
    ACCESSORIES, 
    MAIN_CATEGORIES, 
    OCCASION_TAGS, 
    SEASON_TAGS, 
    STYLE_TAGS, 
    WEATHER_ICON_MAPPING,
)
from utils_constants import PATH_CLOSET

from outfit_utils import filter_items

# References:
# https://daleonai.com/social-media-fashion-ai

OUTFIT_COLS = [0, 2, 4, 0, 2, 4]

WEATHER_TO_SEASON_MAPPINGS = {
    'Hot': 'Summer',
    'Warm': 'Summer',
    'Mild': 'Spring',
    'Chilly': 'Fall',
    'Rainy': 'Fall',
    'Cold': 'Winter',
    'Really Cold': 'Winter',
}


def choose_outfit_type(ratio, include_accessories=True) -> list:
    """Choose outfit combination type and return outfit categories.

    Can either choose top + bottom combo, or dress/set combo.

    Returns
    -------
    List(str)
    """
    choice = random.randint(1, ratio)

    additional_categories = ACCESSORIES if include_accessories else []

    if choice != 1:
        categories = [x for x in MAIN_CATEGORIES if x not in ('dresses')]
        return categories + additional_categories

    categories = [x for x in MAIN_CATEGORIES if x not in ('tops', 'bottoms')]
    return categories + additional_categories


def choose_outfit(
    filepaths,
    weather_type, 
    occasion,
    include_accessories=True,
    exclude_items={},
):
    """
    Returns
    -------
    dict
    """
    season = WEATHER_TO_SEASON_MAPPINGS[weather_type]

    tops_count = len(filter_items(filepaths['tops'], [season], [occasion]))
    bottoms_count = len(filter_items(filepaths['bottoms'], [season], [occasion]))
    dresses_count = len(filter_items(filepaths['dresses'], [season], [occasion]))
    ratio = round(((tops_count + bottoms_count) / 2) / dresses_count)
    categories = choose_outfit_type(ratio, include_accessories)

    outfit_pieces = {}
    is_statement = False
    for cat in categories:
        # get clothing items that are the proper occasion and season type 
        # and that have not been recently worn
        options = [
            x for x in filepaths[cat] if (
                (OCCASION_TAGS[occasion] in x)
                and (SEASON_TAGS[season] in x) 
                and (x not in exclude_items.get(cat, []))
            )
        ]
        
        if (cat == 'outerwear') and (weather_type in ('Hot')):
            continue
        
        if not options:
            print(f"NO MATCHING OPTIONS FOR CATEGORY '{cat}'.")
            continue
        
        # if previous item was 'statement' piece, only choose from 'basics'
        if is_statement:
            options = [
                x for x in options if STYLE_TAGS['Statement'] not in x
            ]

        choice = random.choice(options)
        outfit_pieces[cat] = choice
        
        # if this item or any of the previous items were 'statement' pieces
        is_statement = (STYLE_TAGS['Statement'] in choice) or is_statement

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
    filepaths, weather_info, occasion, num_days, amount, include_accessories, days_in_week=7
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
            filepaths,
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
