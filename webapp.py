import json
import numpy as np
import streamlit as st

from webapp_widgets import (
    choose_inspo_file,
    confirm_filters_added,
    select_and_apply_filters,
    get_and_display_outfit_plans,
    get_choose_outfit_responses,
)

from categorize_wardrobe import categorize_wardrobe_style
from closet_creater import Closet
from display_closet import display_outfit_pieces
from email_scraper import extract_items_from_email
from extract_tags import create_items_tags
from info_material import about_info
from inspo_finder import (
    get_outfit_match_from_camera_input, get_outfit_match_from_inspo
)
from outfit_calendar import choose_outfit
from organize_closet import ClosetAnalyzer
from outfit_selection_utils import choose_outfit
from setup_closet import upload_closet_setup_items, upload_items
from setup_tags import tag_items
from state_updates import init_session_state
from tagging import display_article_tags
from utils import check_if_url_valid, get_all_image_filenames, update_keys

from category_constants import MAIN_CATEGORIES, SEASONS, OCCASIONS
from utils_constants import CLOSET_PATH, OUTFIT_PATH
from webapp_constants import (
    CAMERA_OPTION, INSPO_OPTION, OPTIONS, RANDOM_OPTION, TRIP_OPTION, VIEW_OPTION,
)

SINGULAR_TO_PLURAL = {
    'dress': 'dresses',
    'top': 'tops',
    'bottom': 'bottoms'
}

# References:
# https://daleonai.com/social-media-fashion-ai


# ------------------------------------
# Header -----------------------------
# ------------------------------------

st.image('header_white.jpeg')
about_info()

# run this only once
if 'is_start' not in st.session_state:
    init_session_state(overwrite=False)
    st.session_state['is_start'] = False


def print_states():
    states = {k: v for k, v in st.session_state.items() if k.startswith('is_')}
    print(f'session state info: {states}')
    print(f"session state items: {len(st.session_state['items'])}")
    print(f"session state items tags: {len(st.session_state['items_tags'])}")
    print(f"session state outfits: {len(st.session_state['outfits'])}")


# ------------------------------------
# Closet Option ----------------------
# ------------------------------------


st.header('App Options')
cols = st.columns(2)

cols[0].subheader('Closet Option')
MOCK_OPTION = 'Use mock closet data for testing'
UPLOAD_OPTION = 'Manually upload own personal closet'
IMPORT_OPTION = 'Import closet from email receipts'
CLOSET_OPTIONS = [MOCK_OPTION, UPLOAD_OPTION]  # , IMPORT_OPTION]

closet_option = cols[0].radio(
    "Which closet would you like to use?",
    CLOSET_OPTIONS,
    on_change=init_session_state
)

if closet_option == MOCK_OPTION:
    is_user_closet = False

    items = get_all_image_filenames(CLOSET_PATH)
    items_tags = create_items_tags(items)
    st.session_state['closet'] = Closet(
        items=items,
        items_tags=items_tags,
        is_user_closet=is_user_closet,
    )

elif closet_option == UPLOAD_OPTION:
    is_user_closet = True

    # to not reset to state 'is_closet_upload' after user finishes upload
    if not st.session_state['is_finished_upload']:
        st.session_state['is_closet_upload'] = True

    if st.session_state['is_closet_upload']:
        upload_closet_setup_items()

    if st.session_state['is_item_tag_session']:
        tag_items()

    if st.session_state['is_create_outfits_state']:
        print_states()
        st.session_state['closet'] = Closet(
            items=st.session_state['items'],
            items_tags=st.session_state['items_tags'],
            is_user_closet=is_user_closet,
            outfits=[],
        )
        print('Number of outfits created:', len(st.session_state['closet'].outfits))

        # ClosetAnalyzer(st.session_state['closet']).count_amounts()

    if st.session_state['outfits']:
        st.session_state['finished_all_uploads'] = True

elif closet_option == IMPORT_OPTION:
    extract_items_from_email()

# ------------------------------------
# ------------------------------------

if st.session_state['finished_all_uploads'] or closet_option == MOCK_OPTION:
    cols[1].subheader('Feature Option')
    option = cols[1].radio("What would you like to do?", OPTIONS)

    # ------------------------------------
    # View Closet ------------------------
    # ------------------------------------

    if option == VIEW_OPTION:
        st.header("View Entire Closet")
        info_placeholder = st.container()
        seasons, occasions = select_and_apply_filters(
            info_placeholder, is_user_closet=is_user_closet
        )

        st.subheader("Options")
        if st.button('Show Wardrode Info'):
            if confirm_filters_added(seasons, occasions):
                print('Printing wardrobe info...')
                categorize_wardrobe_style()

        if st.button('View Clothing Tags'):
            if confirm_filters_added(seasons, occasions):
                display_article_tags(st.session_state['items_filtered'])

    # ------------------------------------
    # Analyze Closet ---------------------
    # ------------------------------------

    elif option == "Analyze closet":
        ClosetAnalyzer().count_amounts()

    # ------------------------------------
    # Random Outfit ----------------------
    # ------------------------------------

    elif option == RANDOM_OPTION:
        season, weather, occasion = get_choose_outfit_responses()
        if st.button('Select Random Outfit'):
            st.header('Selected Outfit')
            outfit = choose_outfit(
                st.session_state['closet'],
                weather,
                occasion,
            )
            if outfit:
                display_outfit_pieces(outfit.values())
                if st.button("This doesn't match together."):
                    Closet().remove_outfit(outfit)
                    st.write("Outfit items have been unmatched.")
            else:
                st.text("NO APPROPRIATE OPTIONS FOR THE WEATHER AND OCCASION.")

    # ------------------------------------
    # Inspo Outfit -----------------------
    # ------------------------------------

    elif option == INSPO_OPTION:
        image, image_type = choose_inspo_file()
        if st.button("Select Inspo-Based Outfit"):
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
                    get_outfit_match_from_inspo(
                        st.session_state['closet'].items, filepath=image
                    )
                else:
                    get_outfit_match_from_inspo(
                        st.session_state['closet'].items, uri=image
                    )

    # ------------------------------------
    # Trip Outfits -----------------------
    # ------------------------------------

    elif option == TRIP_OPTION:
        st.session_state.outfit_plans = {}
        st.session_state.outfit_plans = get_and_display_outfit_plans(
            st.session_state['closet']
        )

        if st.session_state.outfit_plans:
            if st.button('Save Outfit Plan'):
                with open('outfit_plans', 'w') as f:
                    json.dump(st.session_state.outfit_plans, f)
                print('Outfit Plan saved to file.')

    # ------------------------------------
    # Camera Option ----------------------
    # ------------------------------------

    elif option == CAMERA_OPTION:
        camera_input = st.camera_input("Snap image of clothing item")

        if camera_input:
            bytes_data = camera_input.getvalue()
            get_outfit_match_from_camera_input(st.session_state['closet'].items, content=bytes_data)

