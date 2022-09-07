import json
import os
import numpy as np
import streamlit as st
import SessionState

from typing import Tuple

from categorize_wardrobe import categorize_wardrobe_style
from closet_creater import Closet
from count_closet import count_outfits
from display_closet import display_outfit_pieces
from info_material import about_info, finished_tagging_info, select_filters_info
from inspo_finder import get_outfit_match_from_inspo
from outfit_calendar import (
    choose_outfit,
    get_outfit_plan_for_all_occasions,
    get_weather_info_for_outfitplans,
    display_outfit_plan,
)
from outfit_utils import (
    filter_outfits_on_item,
    filter_appropriate_outfits,
    filter_appropriate_items,
)
from setup_closet import upload_closet_setup_items, upload_items
from setup_tags import tag_items
from tagging import display_article_tags
from utils import check_if_url_valid, get_all_image_filenames

from category_constants import MAIN_CATEGORIES, SEASONS, OCCASIONS
from utils_constants import CLOSET_PATH

# References:
# https://daleonai.com/social-media-fashion-ai

# Set up tkinter
# root = tk.Tk()
# root.withdraw()

# Make folder picker dialog appear on top of other windows
# root.wm_attributes('-topmost', 1)

INSPO_DIR = 'inspo/'

OUTFITS = Closet().get_outfits()

WEATHERS = ['Hot', 'Warm', 'Mild', 'Chilly', 'Cold', 'Rainy']
DOWS = ['Sun', 'Mon', 'Tues', 'Weds', 'Thurs', 'Fri', 'Sat']
YES_OR_NO = ['Yes', 'No']
YES_NO_MAPPING = {'Yes': True, 'No': False}
AMOUNTS = [
    'small carry-on suitcase',
    'medium suitcase',
    'large suitcase',
    'entire closet',
]


def option_one_questions() -> Tuple[str, str, str]:
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
    side = st.sidebar
    form = side.form('Plan')

    occasions = form.multiselect(
        "What occasions are you planning for?", OCCASIONS
    )

    work_dow = form.multiselect(
        "If you chose work above, what days of the week are you in the office?", 
        DOWS,
    )

    include = form.selectbox(
        "Would you like to include accessories?", YES_OR_NO
    )
    include = YES_NO_MAPPING[include]

    amount = form.selectbox("How much are you looking to bring?", AMOUNTS)

    city = form.text_input("Which city are you traveling to?").lower().strip()
    country = form.text_input("Country?").lower().strip()

    start_date = form.date_input("When are you starting your trip?")
    end_date = form.date_input("When are you ending your trip?")

    if form.form_submit_button("Create Outfit Plan"):
        if end_date < start_date:
            form.error("ERROR: end date cannot be before start date.")
            return [], None, None, None, None, None, None
        if 'Work' in occasions and not work_dow:
            form.error("ERROR: you must specific the work days of the week.")

        return occasions, include, amount, city, country, start_date, end_date, work_dow

    return [], None, None, None, None, None, None, None


def get_and_display_outfit_plan():
    occasions, include, amount, city, country, start_date, end_date, work_dow = (
        get_outfit_plan_question_responses()
    )

    # if above responses were received
    if occasions:
        weather_info = get_weather_info_for_outfitplans(
            city, country, start_date, end_date
        )

        outfit_plans = get_outfit_plan_for_all_occasions(
            OUTFITS,
            occasions,
            work_dow,
            weather_info['weather_types'],
            start_date,
            end_date,
            amount,
            include,
        )

        st.session_state['outfit_plans'] = outfit_plans
        for occasion, outfit_plan in outfit_plans.items():
            st.header(f'{occasion}')
            st.markdown("""---""")

            days_in_week = 7
            if occasion == 'Work':
                days_in_week = len(work_dow)

            dates = outfit_plan['dates']
            outfits = outfit_plan['outfits']
            display_outfit_plan(dates, outfits, weather_info, days_in_week)

        st.session_state.outfit_plans = outfit_plans
        return st.session_state.outfit_plans
    return st.session_state.outfit_plans


def choose_inspo_file():
    options = ['Select an example inspo file', 'Input my own inspo photo URL']
    option = st.sidebar.radio(
        'How would you like to select your inspo photo?', options
    )

    if option == options[0]:
        filenames = [x for x in os.listdir(INSPO_DIR) if x != '.DS_Store']
        filename = st.sidebar.selectbox(options[0], filenames)
        return os.path.join(INSPO_DIR, filename), 'filepath'
    else:
        return st.sidebar.text_input(options[1]), 'uri'


def get_and_add_filters():
    select_filters_info()
    form = st.sidebar.form('Tags')
    seasons = form.multiselect('Seasons', SEASONS)
    occasions = form.multiselect('Occasions', OCCASIONS)

    if form.form_submit_button('Add Filters'):
        if not occasions or not seasons:
            st.error('Please select occasion and/or season types first.')
        else:
            st.session_state['items_filtered'] = filter_appropriate_items(
                st.session_state['items'], seasons, occasions
            )
            st.session_state['outfits_filtered'] = filter_appropriate_outfits(
                OUTFITS, seasons, occasions,
            )

        info_placeholder.subheader('Post Filter')
        count_outfits(
            info_placeholder,
            st.session_state['outfits_filtered'],
            st.session_state['items_filtered'],
        )

    if not seasons or not occasions:
        st.sidebar.warning(
            "NOTE: No filters selected. Please select filters above and click "
            "'Add Filters'."
        )
    else:
        st.sidebar.success('Filters selected.')

    return seasons, occasions


def confirm_filters_added(seasons, occasions):
    if not seasons or not occasions:
        st.sidebar.error('Please add filters first.')
        return False
    return True


def init_starting_values(cols, init_value):
    for col in cols:
        if col not in st.session_state:
            st.session_state[col] = init_value


def init_session_state():
    cols_init_false = [
        'is_closet_setup',
        'is_closet_upload',
        'is_finished_upload',
        'is_item_tag_session',
        'finished_all_uploads',
        'button_clicked',
    ]

    cols_init_empty_dict = ['items', 'items_tags', 'items_filtered']
    cols_init_zero = ['cat_i', 'item_i', 'i']
    cols_init_null = ['current_tags', 'item', 'outfits_filtered']

    init_starting_values(cols_init_false, False)
    init_starting_values(cols_init_empty_dict, {})
    init_starting_values(cols_init_zero, 0)
    init_starting_values(cols_init_null, None)


######################################
######################################
# Main Screen ########################
######################################
######################################

st.image('header_white.jpeg')
about_info()

# st.header('Closet Information')

info_placeholder = st.container()
# print('Counting items...')
# info_placeholder.subheader('Entire Wardrobe')
# count_outfits(info_placeholder, OUTFITS, items)

# st.header('AIsthetic Algorithm')
init_session_state()

print('DEBUG re-start', st.session_state['is_closet_upload'], st.session_state['is_item_tag_session'])

######################################
# Closet Option ######################
######################################

st.header('App Options')
cols = st.columns(2)

cols[0].subheader('Closet Option')
closet_option = cols[0].radio(
    "Which closet would you like to use?",
    ['Use mock data for testing', 'Use own personal closet'],
)

if closet_option == 'Use mock data for testing':
    st.session_state['items'] = get_all_image_filenames(CLOSET_PATH)
elif closet_option == 'Use own personal closet':
    has_already_setup = st.radio('Have you set up your closet?', ['Yes', 'Not yet'])

    # if has already set up closet previously
    if has_already_setup == 'Yes':
        upload_closet_setup_items()
    # if has NOT set up closet yet
    elif has_already_setup == 'Not yet':
        # to not reset to state 'is_closet_upload' after user finishes upload
        if not st.session_state['is_finished_upload']:
            st.session_state['is_closet_upload'] = True

        if st.session_state['is_closet_upload']:
            upload_items()

        if st.session_state['is_item_tag_session']:
            tag_items()

######################################
######################################

if st.session_state['finished_all_uploads'] or closet_option == "Use mock data for testing":
    options = [
        "Select a random outfit combination from closet",
        "Select an outfit based on an inspo-photo",
        "Plan a set of outfits for a trip",
        "View all clothing articles in closet",
    ]

    cols[1].subheader('Feature Option')
    option = cols[1].radio("What would you like to do?", options)

    ######################################
    ######################################
    # View All ###########################
    ######################################
    ######################################

    if option == "View all clothing articles in closet":
        seasons, occasions = get_and_add_filters()

        st.sidebar.header("Options")

        if st.sidebar.button('Show Wardrode Info'):
            if confirm_filters_added(seasons, occasions):
                print('Printing wardrobe info...')
                categorize_wardrobe_style(st.session_state['items_filtered'])

        if st.sidebar.button('View Clothing Tags'):
            if confirm_filters_added(seasons, occasions):
                display_article_tags(st.session_state['items_filtered'])

    elif option == "Analyze closet":
        ClosetAnalyzer().count_amounts()

    ######################################
    ######################################
    # View All ###########################
    ######################################
    ######################################

    elif option == "Select a random outfit combination from closet":
        st.header("Select a random outfit")
        st.subheader("Options")
        season, weather, occasion = option_one_questions()
        if st.button('Select Random Outfit'):
            st.header('Selected Outfit')
            outfit = choose_outfit(OUTFITS, weather, occasion)
            if outfit:
                display_outfit_pieces(outfit)
                if st.button("This doesn't match together."):
                    Closet().remove_outfit(outfit)
                    st.write("Outfit items have been unmatched.")
            else:
                st.text("NO APPROPRIATE OPTIONS FOR THE WEATHER AND OCCASION.")

    elif option == "Select an outfit based on an inspo-photo":
        st.sidebar.header("Options")
        image, image_type = choose_inspo_file()
        if st.sidebar.button("Select Inspo-Based Outfit"):
            st.header('Inspiration Match')

            is_valid = True
            if image_type == 'uri':
                is_valid = check_if_url_valid(image)

            if is_valid:
                st.text(
                    f'You selected the following image as your inspiration outfit:'
                )
                st.image(image, width=300)
                if image_type == 'filepath':
                    get_outfit_match_from_inspo(st.session_state['items'], filepath=image)
                else:
                    get_outfit_match_from_inspo(st.session_state['items'], uri=image)
    elif option == "Plan a set of outfits for a trip":
        st.sidebar.header("Options")
        st.session_state.outfit_plans = {}
        st.session_state.outfit_plans = get_and_display_outfit_plan()

        if st.session_state.outfit_plans:
            if st.button('Save Outfit Plan'):
                with open('outfit_plans', 'w') as f:
                    json.dump(st.session_state.outfit_plans, f)
                print('Outfit Plan saved to file.')
