import json
import random
import streamlit as st

from datetime import date

from outfit_utils import filter_basic_items, filter_items
from utils import daterange, get_filenames_in_dir

from category_constants import (
    ACCESSORIES, 
    CADENCES,
    MAIN_CATEGORIES, 
    TAGS, 
    WEATHER_ICON_MAPPING,
    WEATHER_TO_SEASON_MAPPINGS,
)
from utils_constants import PATH_CLOSET

# References:
# https://daleonai.com/social-media-fashion-ai

OUTFIT_COLS = [0, 2, 4, 0, 2, 4]

WEEKDAY_MAPPING = ['Mon', 'Tues', 'Weds', 'Thurs', 'Fri', 'Sat', 'Sun']

def _are_tags_in_item(item, season, occasion):
    return TAGS['season'][season] in item and TAGS['occasion'][occasion] in item


def choose_outfit(
    outfits,
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

    # Get clothing items that are the proper occasion and season type
    appropriate_outfits = [
        outfit for outfit in outfits if (
            season in outfit['tags']['season']
            and occasion in outfit['tags']['occasion']
        )
    ]
    # Get clothing items that have not been recently worn
    options = [
        outfit for outfit in appropriate_outfits if all(
            outfit[cat] != item for cat, item in exclude_items.items()
        )
    ]

    if not options:
        print(f"NO APPROPRIATE OPTIONS FOR THE WEATHER AND OCCASION.")
        return

    choice = random.choice(options)
    
    cats = ['shoes']
    if include_accessories:
        cats += ACCESSORIES
    
    for cat in cats:
        item_options = get_filenames_in_dir(f'{PATH_CLOSET}/{cat}')
        item_options = [
            item for item in item_options if _are_tags_in_item(
                item, season, occasion
            )
        ]
        if choice['tags']['is_statement']:
            item_options = [
                option for option in item_options 
                if TAGS['style']['Statement'] not in option
            ]
        if item_options:
            choice[cat] = random.choice(item_options)
    
    del choice['tags']

    return choice


def display_outfit_pieces(outfit_pieces: dict):
    """Display outfit pieces.

    Parameters
    ----------
    outfit_pieces : dict
        Dict of outfit pieces, with the category the key and the image filepath
        the value.
    """
    cols = st.columns(6)
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


def display_outfit_plan(
    dates: list, outfits: list, weather_info: dict, days_in_week: int
):
    temps, weathers, weather_types = (
        weather_info['temps'], 
        weather_info['weathers'], 
        weather_info['weather_types'],
    )
    
    num_cols = 3
    for i, outfit_date, outfit_pieces in zip(range(len(dates)), dates, outfits):
        if i % days_in_week == 0:
            st.header(f'Week {int((i / days_in_week)) + 1}')
            cols = st.columns(num_cols)
            col_i = 0

        dow = WEEKDAY_MAPPING[outfit_date.weekday()]
        month_day = f'{outfit_date.month}/{outfit_date.day}'
        cols[col_i].subheader(f'Day {i + 1} - {dow} - {month_day}')
        
        weather_text = (
            f'{weathers[i]} - {temps[i]}° ({weather_types[i]})'
        )
        weather_icon_filename = get_weather_icon_filename(
            weather_types[i], weathers[i]
        )

        cols[col_i].image(f'icons/weather/{weather_icon_filename}', width=30)
        cols[col_i].text(weather_text)
        cols[col_i].image(list(outfit_pieces.values()), width=70)

        cols[col_i].markdown("""---""")

        if col_i in list(range(num_cols - 1)):
            col_i += 1
        else:
            col_i = 0


def get_outfit_plan(
    filepaths: list, 
    weather_types: list, 
    occasion: str,
    city: str, 
    start_date: date, 
    end_date: date, 
    amount: str, 
    include_accessories: bool,
):   
    """Get outfit plan from `start_date` to `end_date`.

    Parameters
    ----------
    filepaths : list
        The filepaths of the clothing item images.
    weather_types : list
        The weather types (ie 'Hot', 'Warm', 'Chilly') of the days specified.
    occasion : str
        The occasion type (ie 'Casual', 'Dinner/Bar').
    city : str
        The city for the outfit plan.
    start_date : date
        The date when to start the outfit plan.
    end_date : date
        The date when to end the outfit plan.
    amount : str
        The amount to pack for (i.e. 'small carry-on suitcase', 
        'medium suitcase').
    include_accessories : bool
        Whether to add accessories to the outfit plan.

    Returns
    -------
    list
        List of outfits from `start_date` to `end_date`.
    """
    outfits = []
    dates = []
    recently_worn = init_most_recently_worn()
    for weather_type, outfit_date in zip(
        weather_types, daterange(start_date, end_date)
    ):
        # Don't add outfit for `occasion` of type 'Work' if its the weekend 
        if (outfit_date.weekday() in (5, 6)) and (occasion == 'Work'):
            continue

        dates.append(outfit_date)

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
    
    # with open(f'outfit_plans/{city}_{start_date}_{end_date}.json', 'w') as f:
    #    json.dump(outfits , f)

    return dates, outfits
