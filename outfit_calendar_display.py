import streamlit as st

from utils import increment_i
from category_constants import (
    DOWS,
    HISTORICAL_WEATHER_AVG_TITLE,
    WEATHER_ICON_MAPPING,
    WEATHER_TO_SEASON_MAPPINGS,
)


def select_weather_icon_filename(weather_type, weather=None):
    """Gets weather icon based either on `weather_type`, `weather` or `temp`.

    Parameters
    ----------
    weather_type : str
      Either 'Really Cold', 'Cold', 'Chilly', 'Mild', 'Warm', or 'Hot'
    weather : str
      Weather description (e.g. 'Mostly clear')

    Returns
    -------
    str
      Filename to weather icon image.
    """
    if weather_type in ['Really Cold', 'Rainy']:
        return WEATHER_ICON_MAPPING[weather_type]

    # If the Historical Average is used, weather description information isn't
    # provided; so `weather_type` instead of `weather` should be used to select
    # the appropriate icon.
    if weather != HISTORICAL_WEATHER_AVG_TITLE:
        return WEATHER_ICON_MAPPING.get(weather, 'cloudy.png')

    if weather_type in ['Cold', 'Chilly']:
        return WEATHER_ICON_MAPPING['Cloudy']
    if weather_type in ['Warm', 'Hot']:
        return WEATHER_ICON_MAPPING['Clear']
    return WEATHER_ICON_MAPPING['Partly cloudy']


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

        dow = DOWS[outfit_date.weekday()]
        month_day = f'{outfit_date.month}/{outfit_date.day}'
        cols[col_i].subheader(f'Day {i + 1} - {dow} - {month_day}')

        weather_text = f'{weathers[i]} - {temps[i]}° ({weather_types[i]})'
        weather_icon_filename = select_weather_icon_filename(
            weather_types[i], weathers[i]
        )

        cols[col_i].image(f'icons/season/{weather_icon_filename}', width=30)
        cols[col_i].text(weather_text)
        cols[col_i].image(list(outfit.values()), width=70)

        cols[col_i].markdown("""---""")

        col_i = increment_i(col_i, num_cols - 1)
