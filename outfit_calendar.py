import json
import random
import streamlit as st

from datetime import date

from count_closet import count_outfits
from get_weather import get_projected_weather
from outfit_utils import (
    filter_appropriate_outfits, filter_category_of_items, filter_basic_items,
)
from utils import daterange, get_filenames_in_dir, increment_i

from category_constants import (
    ACCESSORIES,
    CADENCES,
    MAIN_CATEGORIES,
    OUTFIT_AMOUNT,
    WEATHER_ICON_MAPPING,
    WEATHER_TO_SEASON_MAPPINGS,
)
from utils_constants import CLOSET_PATH

# References:
# https://daleonai.com/social-media-fashion-ai

WEEKDAY_MAPPING = ['Mon', 'Tues', 'Weds', 'Thurs', 'Fri', 'Sat', 'Sun']


def is_any_exclude_item_in_outfit(outfit: dict, recently_worn: dict) -> bool:
    """Check if any items from `recently_worn` are in `outfit`.

    Checks for all categories in `outfit` and `recently_worn`.

    Parameters
    ----------
    outfit : Dict[str]
    recently_worn : Dict[List[str]]

    Returns
    -------
    bool
    """
    # any exclude item in any of the categories
    return any(
        any(
            exclude_item == item for exclude_item in recently_worn.get(cat, [])
        ) for cat, item in outfit.items()
    )


def get_non_recently_worn_options(options: list, recently_worn: dict):
    """Remove outfits from `options` that include recently-worn items.

    If all options were recently-worn, keep recursively removing a day from
    the recently-worn items (i.e. if 'recently' is defined as 3 days, check 2
    days, then 1 day).
    """
    filtered_options = [
        outfit for outfit in options
        if not is_any_exclude_item_in_outfit(outfit, recently_worn)
    ]
    if filtered_options:
        return filtered_options

    recently_worn = {cat: items[:-1] for cat, items in recently_worn.items()}
    return get_non_recently_worn_options(options, recently_worn)


def choose_outfit(
    outfits: list,
    weather_type: str,
    occasion: str,
    include_accessories: bool = True,
    recently_worn: dict = {},
):
    """
    Parameters
    ----------
    recently_worn : Dict[List[str]]

    Returns
    -------
    dict
    """
    season = WEATHER_TO_SEASON_MAPPINGS[weather_type]

    # Get clothing items that are the proper occasion and season type
    appropriate_outfits = filter_appropriate_outfits(
        outfits, [season], [occasion],
    )

    if not appropriate_outfits:
        print(f"NO APPROPRIATE OPTIONS FOR THE WEATHER AND OCCASION.")
        return {}

    options = get_non_recently_worn_options(appropriate_outfits, recently_worn)

    # create deep copy
    choose_from = [{k: v for k, v in option.items()} for option in options]
    random_ind = random.randint(0, len(options) - 1)
    choice = choose_from[random_ind]

    # add shoes and accessories to outfit
    cats = ['shoes']
    if include_accessories:
        cats += ACCESSORIES

    for cat in cats:
        item_options = get_filenames_in_dir(f'{CLOSET_PATH}/{cat}')
        item_options = filter_category_of_items(item_options, [season], [occasion])

        if choice['tags']['is_statement']:
            item_options = filter_basic_items(item_options)
        if item_options:
            choice[cat] = random.choice(item_options)

    del choice['tags']

    return choice


def get_season_types_from_weather_info(weather_types):
    """Return season types based on scraped weather.

    Parameters
    ----------
    weather_info

    Returns
    -------
    set
    """
    weather_type_set = set(weather_types)
    season_types = set([
        WEATHER_TO_SEASON_MAPPINGS[weather_type] 
        for weather_type in weather_type_set
    ])

    st.write(
        "This trip requires planning for the following season types"
        f": {', '.join(season_types)}."
    )

    return season_types


def get_weather_info_for_outfitplans(city, country, start_date, end_date):
    weather_info = get_projected_weather(city, country, start_date, end_date)

    if not weather_info['temps']:
        st.error(
            "ERROR: Weather information not found. Confirm that city and "
            "country names are filled in and spelled correctly."
        )
        return
    return weather_info


def get_outfit_plan_for_all_occasions(
    outfits,
    occasions,
    work_dow,
    weather_types,
    start_date,
    end_date,
    amount,
    include,
):
    seasons = get_season_types_from_weather_info(weather_types)

    # Make sure items of all necessary season types are available,
    # depending on set of all weather types of trip
    appropriate_outfits = filter_appropriate_outfits(
        outfits, seasons, occasions,
    )

    st.subheader('Options Available')
    info_placeholder = st.container()           
    count_outfits(info_placeholder, appropriate_outfits)

    outfit_plan = {}
    for occasion in occasions:
        outfit_plan[occasion] = []
        outfit_plan[occasion] = get_outfit_plan(
            appropriate_outfits,
            weather_types,
            occasion,
            work_dow,
            start_date,
            end_date,
            amount,
            include,
        )

    # save_outfit_plan(outfit_plan, city, start_date, end_date)
    return outfit_plan


def get_weather_icon_filename(weather_type, weather):
    if weather_type == 'Really Cold':
        return WEATHER_ICON_MAPPING['Really Cold']
    if weather_type == 'Rainy':
        return WEATHER_ICON_MAPPING['Rainy']
    return WEATHER_ICON_MAPPING.get(weather, 'cloudy.png')


def init_most_recently_worn():
    categories = ['top', 'bottom', 'dress', 'outerwear']
    return {cat: [] for cat in categories}


def update_most_recently_worn(
    outfit: dict, amount: str, recently_worn: dict
) -> dict:
    for cat, cadence in CADENCES[amount].items():
        if outfit.get(cat):
            recently_worn[cat] = (
                [outfit[cat]] + recently_worn[cat]
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
    for i, outfit_date, outfit in zip(range(len(dates)), dates, outfits):
        # display week number
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

        cols[col_i].image(f'icons/season/{weather_icon_filename}', width=30)
        cols[col_i].text(weather_text)
        cols[col_i].image(list(outfit.values()), width=70)

        cols[col_i].markdown("""---""")

        col_i = increment_i(col_i, num_cols - 1)


def save_outfit_plan(outfits, city, start_date, end_date):
    path = f'outfit_plans/{city}_{start_date}_{end_date}.json'
    with open(path, 'w') as f:
        json.dump(outfits, f)


def get_outfit_plan(
    outfits: list,
    weather_types: list,
    occasion: str,
    work_dow,
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
    occasion_outfit_plan = {
        'dates': [],
        'outfits': [],
    }
    recently_worn = init_most_recently_worn()
    for weather_type, outfit_date in zip(
        weather_types, daterange(start_date, end_date)
    ):
        # Don't add outfit for `occasion`='Work' if its a non-work day
        work_dow_ints = [
            i for i, day in enumerate(WEEKDAY_MAPPING) if day in work_dow
        ]
        if outfit_date.weekday() not in work_dow_ints and occasion == 'Work':
            continue

        occasion_outfit_plan['dates'].append(outfit_date)
        outfit = choose_outfit(
            outfits,
            weather_type,
            occasion,
            include_accessories,
            recently_worn=recently_worn,
        )
        occasion_outfit_plan['outfits'].append(outfit)

        recently_worn = update_most_recently_worn(outfit, amount, recently_worn)

    return occasion_outfit_plan
