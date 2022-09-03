import json
import os
import numpy as np
import requests
import streamlit as st
import SessionState

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
from setup_closet import download_json, tag_items, upload_items
from tagging import display_article_tags
from utils import get_all_image_filenames

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


def option_one_questions():
    season = st.sidebar.selectbox("What's the season?", SEASONS)

    options = ['Hot', 'Warm', 'Mild', 'Chilly', 'Cold', 'Rainy']
    weather = st.sidebar.selectbox("What is the weather today?", options)

    occasion = st.sidebar.selectbox("What is the occasion?", OCCASIONS)

    return season, weather, occasion


def get_outfit_plan_question_responses():
    side = st.sidebar
    form = side.form('Plan')

    q = "What occasions are you planning for?"
    occasions = form.multiselect(q, OCCASIONS)

    options = ['Sun', 'Mon', 'Tues', 'Weds', 'Thurs', 'Fri', 'Sat']
    q = "If you chose work above, what days of the week are you in the office?"
    work_dow = form.multiselect(q, options)

    options = ['Yes', 'No']
    include = form.selectbox("Would you like to include accessories?", options)

    accessories_mapping = {'Yes': True, 'No': False}
    include = accessories_mapping[include]

    options = [
        'small carry-on suitcase',
        'medium suitcase',
        'large suitcase',
        'entire closet',
    ]
    amount = form.selectbox("How much are you looking to bring?", options)

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

    if occasions:  # if above responses were received
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


def check_if_url_valid(url):
    try:
        response = requests.get(url)
        st.sidebar.success("URL is valid and exists on the internet.")
        return True
    except requests.ConnectionError as exception:
        st.sidebar.error("ERROR: URL is not a valid link.")
    except requests.exceptions.MissingSchema:
        st.sidebar.error("ERROR: URL is not a valid link.")

    return False


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


def get_and_add_filters(session_state):
    select_filters_info()
    form = st.sidebar.form('Tags')
    seasons = form.multiselect('Seasons', SEASONS)
    occasions = form.multiselect('Occasions', OCCASIONS)

    if form.form_submit_button('Add Filters'):
        if not occasions or not seasons:
            st.error('Please select occasion and/or season types first.')
        else:
            ss.items_filtered = filter_appropriate_items(
                items, seasons, occasions
            )
            ss.outfits_filtered = filter_appropriate_outfits(
                OUTFITS, seasons, occasions,
            )
            print('# of items:', len(ss.items_filtered))
            print('# of outfits:', len(ss.outfits_filtered))

        info_placeholder.subheader('Post Filter')
        count_outfits(
            info_placeholder,
            ss.outfits_filtered,
            ss.items_filtered,
        )

    if not seasons or not occasions:
        st.sidebar.warning(
            "NOTE: No filters selected. Please select filters above and click "
            "'Add Filters'."
        )
    else:
        st.sidebar.success('Filters selected.')

    return session_state, seasons, occasions


def confirm_filters_added(seasons, occasions):
    if not seasons or not occasions:
        st.sidebar.error('Please add filters first.')
        return False
    return True


def init_session_state():
    return SessionState.get(
        is_closet_upload=False,
        is_item_tag_session=False,
        finished_tag_session=False,
        items=None,
        items_tags=None,
        finished_button_clicked=False,
        cat_i=0,  # for closet setup - tagging
        item_i=0,  # for closet setup - tagging
        current_tags=None,  # for closet setup - tagging
        has_uploaded_closet=False,
        item='',
        button_clicked=False,
        scroll_items=False,
        i=0,
        items_filtered=None,
        outfits_filtered=None,
    )


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
ss = init_session_state()

######################################
# Closet Option ######################
######################################

st.header('App Options')

closet_option = st.radio(
    "Which closet would you like to use?", 
    ['Use mock data for testing', 'Use own personal closet'],
)

if closet_option == 'Use mock data for testing':
    ss.items = get_all_image_filenames(CLOSET_PATH)
elif closet_option == 'Use own personal closet':
    ss.items = None
    has_already_setup = st.radio('Have you set up your closet?', ['Yes', 'Not yet'])
    if has_already_setup == 'Yep':
        ss.is_closet_upload = False
    elif has_already_setup == 'Not yet':
        ss.is_closet_upload = True

    if ss.is_closet_upload:
        if ss.finished_button_clicked:
            ss.is_item_tag_session = True
        else:
            st.subheader('Upload Closet')
            items = upload_items()
            ss.finished_button_clicked = st.button('Finished uploading closet.')
            if ss.finished_button_clicked:
                ss.items = items
    else:
        if not ss.items_tags:
            st.subheader('Upload Closet Item Tags')
            st.write("""
                If you have previously set up your closet, you should have
                your closet item tags (occasion, season, etc.) saved. Please
                upload those tags here.
            """)
            st.file_uploader('Please select your closet tags json file')

        if not ss.items:
            st.subheader('Upload Closet')

            items = upload_items()
            ss.finished_button_clicked = st.button('Finished uploading closet.')
            if ss.finished_button_clicked:
                ss.items = items
                ss.has_uploaded_closet

    # need this twice
    if ss.finished_button_clicked:
        ss.is_item_tag_session = True

    if ss.is_item_tag_session and not ss.finished_tag_session:
        ss.is_closet_upload = False

        ss = tag_items(ss, ss.items)

    if ss.finished_tag_session:
        finished_tagging_info()
        if download_json(ss.items_tags, 'aisthetic_tags.json', 'Download Tags'):
            ss.is_closet_upload = False

print(ss.is_closet_upload, ss.has_uploaded_closet)
######################################
######################################

if ss.has_uploaded_closet or closet_option == "Use mock data for testing":
    options = [
        "Select a random outfit combination from closet",
        "Select an outfit based on an inspo-photo",
        "Plan a set of outfits for a trip",
        "View all clothing articles in closet",
    ]

    option = st.radio("What would you like to do?", options)

    ######################################
    ######################################
    # Side Bar ###########################
    ######################################
    ######################################

    if option == "View all clothing articles in closet":
        ss, seasons, occasions = get_and_add_filters(ss)

        st.sidebar.header("Options")

        if st.sidebar.button('Show Wardrode Info'):
            if confirm_filters_added(seasons, occasions):
                print('Printing wardrobe info...')
                categorize_wardrobe_style(ss.items_filtered)

        if st.sidebar.button('View Clothing Tags'):
            if confirm_filters_added(seasons, occasions):
                display_article_tags(ss.items_filtered)

    elif option == "Analyze closet":
        ClosetAnalyzer().count_amounts()

    elif option == "Select a random outfit combination from closet":
        st.sidebar.header("Options")
        season, weather, occasion = option_one_questions()
        if st.sidebar.button('Select Random Outfit'):
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
                    get_outfit_match_from_inspo(ss.items, filepath=image)
                else:
                    get_outfit_match_from_inspo(ss.items, uri=image)
    elif option == "Plan a set of outfits for a trip":
        st.sidebar.header("Options")
        st.session_state.outfit_plans = {}
        st.session_state.outfit_plans = get_and_display_outfit_plan()

        if st.session_state.outfit_plans:
            if st.button('Save Outfit Plan'):
                with open('outfit_plans', 'w') as f:
                    json.dump(st.session_state.outfit_plans, f)
                print('Outfit Plan saved to file.')
