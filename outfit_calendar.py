import random
import streamlit as st

from category_constants import (
    ACCESSORIES, 
    CADENCES,
    MAIN_CATEGORIES, 
    OCCASION_TAGS, 
    SEASON_TAGS, 
    STYLE_TAGS, 
    WEATHER_ICON_MAPPING,
    WEATHER_TO_SEASON_MAPPINGS,
)
from utils_constants import PATH_CLOSET

from outfit_utils import filter_basic_items, filter_items
from utils import daterange

# References:
# https://daleonai.com/social-media-fashion-ai

OUTFIT_COLS = [0, 2, 4, 0, 2, 4]

DAYS_IN_WEEK = {
    'Casual': 7,
    'Dinner/Bar': 7,
    'Club/Fancy': 7,
    'Work': 5,
}

WEEKDAY_MAPPING = ['Mon', 'Tues', 'Weds', 'Thurs', 'Fri', 'Sat', 'Sun']

def choose_outfit_type(ratio: int, include_accessories: bool=True) -> list:
    """Choose outfit combination type and return outfit categories.

    Can either choose top + bottom combo, or dress/set combo.

    Parameters
    ----------
    ratio : int
        The number of top-bottom outfit types you want to see for every dresses 
        outfit type. To be used as the weight when randoming choosing between 
        the two outfit combination types.
    include_accessories : bool
        Whether you want to add accessories to the outfit. Default is True.

    Returns
    -------
    List(str)
        The clothing categories for one outfit.
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
    
    # To avoid `division by 0` error
    if dresses_count == 0:
        ratio = 1
    else:
        ratio = round(((tops_count + bottoms_count) / 2) / dresses_count) + 1
    
    categories = choose_outfit_type(ratio, include_accessories)

    outfit_pieces = {}
    is_statement = False
    for cat in categories:
        # Get clothing items that are the proper occasion and season type 
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
        
        # If previous item was 'statement' piece, only choose from 'basics'
        if is_statement:
            options = filter_basic_items(options)
        
        if not options:
            print(f"NO MATCHING OPTIONS FOR CATEGORY '{cat}'.")
            continue

        choice = random.choice(options)
        outfit_pieces[cat] = choice
        
        # If this item or any of the previous items were 'statement' pieces
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


def update_most_recently_worn(
    outfit_pieces: dict, amount: str, recently_worn: dict
) -> dict:
    for cat, cadence in CADENCES[amount].items():
        recently_worn[cat] = (
            [outfit_pieces.get(cat, '')] + recently_worn[cat]
        )[:cadence]
    return recently_worn


def display_outfit_plan(dates: list, outfits: list, weather_info, occasion):
    temps, weathers, weather_types = (
        weather_info['temps'], 
        weather_info['weathers'], 
        weather_info['weather_types'],
    )
    
    num_cols = 3
    day_i = 0
    for outfit_date, outfit_pieces in zip(dates, outfits):
        if day_i % DAYS_IN_WEEK[occasion] == 0:
            st.header(f'Week {int((day_i / DAYS_IN_WEEK[occasion])) + 1}')
            cols = st.beta_columns(num_cols)
            col_i = 0

        dow = WEEKDAY_MAPPING[outfit_date.weekday()]
        month_day = f'{outfit_date.month}-{outfit_date.day}'
        cols[col_i].subheader(f'Day {day_i + 1} - {dow} - {month_day}')
        
        weather_text = (
            f'{weathers[day_i]} - {temps[day_i]}° ({weather_types[day_i]})'
        )
        weather_icon_filename = get_weather_icon_filename(
            weather_types[day_i], weathers[day_i]
        )

        cols[col_i].image(f'icons/weather/{weather_icon_filename}', width=30)
        cols[col_i].text(weather_text)
        cols[col_i].image(list(outfit_pieces.values()), width=70)

        cols[col_i].markdown("""---""")

        if col_i in list(range(num_cols - 1)):
            col_i += 1
        else:
            col_i = 0
        
        day_i += 1
        
        

def get_outfit_plan(
    filepaths, weather_types, occasion, start_date, end_date, amount, include_accessories
):   
    outfits = []
    dates = []
    recently_worn = init_most_recently_worn()
    for weather_type, outfit_date in zip(
        weather_types, daterange(start_date, end_date)
    ):
        dates.append(outfit_date)

        # Don't find outfit for `occasion` of type 'Work' if weekend 
        if (outfit_date.weekday() in (5, 6)) and (occasion == 'Work'):
            outfits.append({})
            continue

        outfit_pieces = choose_outfit(
            filepaths,
            weather_type, 
            occasion, 
            include_accessories, 
            exclude_items=recently_worn,
        )

        outfits.append(outfit_pieces) 
        recently_worn = update_most_recently_worn(
            outfit_pieces, amount, recently_worn
        )
    
    return dates, outfits
