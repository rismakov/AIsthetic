import streamlit as st
import os

from typing import Any, List, Tuple

from closet_creater import Closet
from count_closet import count_outfits
from get_weather import get_projected_weather
from info_material import about_info, finished_tagging_info, select_filters_info
from outfit_calendar_display import display_outfit_plan
from outfit_calendar import OutfitCalendars
from outfit_utils import (
    filter_outfits_on_item,
    filter_appropriate_outfits,
    filter_appropriate_items,
)
from category_constants import DOWS, MAIN_CATEGORIES, SEASONS, OCCASIONS


INSPO_DIR = 'inspo/'

WEATHERS = ['Hot', 'Warm', 'Mild', 'Chilly', 'Cold', 'Rainy']
YES_OR_NO = ['Yes', 'No']
YES_NO_MAPPING = {'Yes': True, 'No': False}
AMOUNTS = [
    'small carry-on suitcase',
    'medium suitcase',
    'large suitcase',
    'entire closet',
]


def get_choose_outfit_responses() -> Tuple[str, str, str]:
    st.header("Select a random outfit")
    cols = st.columns(3)
    options = {
        'season': SEASONS,
        'weather today': WEATHERS,
        'occasion': OCCASIONS,
    }
    return [
        cols[i].selectbox(
            f'What is the {k}?', v
        ) for i, (k, v) in enumerate(options.items())
    ]


def get_outfit_plan_question_responses():
    st.header('Trip Planner')
    with st.form(key='Plan'):
        col1, col2 = st.columns(2)

        with col1:
            occasions = st.multiselect(
                "What occasions are you planning for?", OCCASIONS
            )
            work_dow = st.multiselect(
                "If you chose work, what days are you in the office?", DOWS,
            )
            include = st.selectbox(
                "Would you like to include accessories?", YES_OR_NO
            )
            amount = st.selectbox("How much are you looking to bring?", AMOUNTS)

        with col2:
            city = st.text_input("Which city are you traveling to?").lower().strip()
            country = st.text_input("Country?").lower().strip()
            start_date = st.date_input("When are you starting your trip?")
            end_date = st.date_input("When are you ending your trip?")

        include = YES_NO_MAPPING[include]

        if st.form_submit_button("Create Outfit Plan"):
            if end_date < start_date:
                st.error("ERROR: end date cannot be before start date.")
                return [], None, None, None, None, None, None
            if 'Work' in occasions and not work_dow:
                st.error("ERROR: you must specific the work days of the week.")

            return occasions, include, amount, city, country, start_date, end_date, work_dow

    return [], None, None, None, None, None, None, None


def get_and_display_outfit_plans(closet):
    occasions, include, amount, city, country, start_date, end_date, work_dow = (
        get_outfit_plan_question_responses()
    )

    # if above responses were received
    if occasions:
        outfit_calendars = OutfitCalendars(
            closet,
            start_date,
            end_date,
            city,
            country,
            occasions,
            amount,
            include,
            work_dow,
        )

        # st.session_state['outfit_plans'] = outfit_plans
        for plan in outfit_calendars.plans:
            st.header(f'{plan.occasion}')
            st.markdown("""---""")

            days_in_week = 7
            if plan.occasion == 'Work':
                days_in_week = len(work_dow)

            display_outfit_plan(
                plan.outfit_plan['dates'],
                plan.outfit_plan['outfits'],
                outfit_calendars.weather_info,
                days_in_week
            )

        # st.session_state.outfit_plans = plans
        return outfit_calendars.plans
    return []


def choose_inspo_file():
    st.header("Select outfit from inspo")
    cols = st.columns(2)
    options = ['Select an example inspo file', 'Input my own inspo photo URL']
    option = cols[0].radio(
        'How would you like to select your inspo photo?', options
    )

    if option == options[0]:
        filenames = [x for x in os.listdir(INSPO_DIR) if x != '.DS_Store']
        filename = cols[0].selectbox(options[0], filenames)
        return os.path.join(INSPO_DIR, filename), 'filepath'
    else:
        return cols[0].text_input(options[1]), 'uri'


def select_filters():
    select_filters_info()
    with st.form('Tags'):
        cols = st.columns(2)
        seasons = cols[0].multiselect('Seasons', SEASONS)
        occasions = cols[1].multiselect('Occasions', OCCASIONS)

        if st.form_submit_button('Add Filters'):
            if not occasions or not seasons:
                st.error('Please select occasion and/or season types first.')
                return None, None
    return seasons, occasions


def select_and_apply_filters(info_placeholder, is_user_closet=False):
    seasons, occasions = select_filters()

    if seasons and occasions:
        st.success('Filters selected.')

        st.session_state['items_filtered'] = filter_appropriate_items(
            st.session_state['closet'], seasons, occasions,
        )
        st.session_state['outfits_filtered'] = filter_appropriate_outfits(
            st.session_state['closet'].outfits, seasons, occasions,
        )

        # info_placeholder.subheader('Post Filter')
        # count_outfits(
        #    info_placeholder,
        #    st.session_state['outfits_filtered'],
        #    st.session_state['items_tags'],
        #    st.session_state['items_filtered'],
        # )
    else:
        st.warning(
            "NOTE: No filters selected. Please select filters above and click "
            "'Add Filters'."
        )

    return seasons, occasions


def confirm_filters_added(seasons, occasions):
    if not seasons or not occasions:
        st.error('Please add filters first.')
        return False
    return True
