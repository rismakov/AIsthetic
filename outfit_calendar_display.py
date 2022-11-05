import streamlit as st

from utils import increment_i
from category_constants import (
    DOWS, WEATHER_ICON_MAPPING, WEATHER_TO_SEASON_MAPPINGS
)


def get_weather_icon_filename(weather_type, weather):
    if weather_type == 'Really Cold':
        return WEATHER_ICON_MAPPING['Really Cold']
    if weather_type == 'Rainy':
        return WEATHER_ICON_MAPPING['Rainy']
    return WEATHER_ICON_MAPPING.get(weather, 'cloudy.png')


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
        weather_icon_filename = get_weather_icon_filename(
            weather_types[i], weathers[i]
        )

        cols[col_i].image(f'icons/season/{weather_icon_filename}', width=30)
        cols[col_i].text(weather_text)
        cols[col_i].image(list(outfit.values()), width=70)

        cols[col_i].markdown("""---""")

        col_i = increment_i(col_i, num_cols - 1)
