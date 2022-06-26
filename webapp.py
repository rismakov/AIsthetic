import json
import os
import numpy as np
import requests
import streamlit as st
import SessionState

from tensorflow.keras.models import load_model

from ProductSearch import ProductSearch, ProductCategories
from closet_creater import Closet
from count_closet import count_item_info, count_outfits
from image_processing import image_processing
from matching_utils import get_viable_matches
from outfit_calendar import (
    choose_outfit, 
    filter_appropriate_outfits,
    get_outfit_plan_for_all_occasions,
    get_weather_info_for_outfitplans,
    display_outfit_pieces, 
    display_outfit_plan, 
)
from outfit_utils import filter_items_in_all_categories
from tagging import (
    choose_filename_to_update, display_article_tags, update_article_tags
)
from utils import (
    get_all_image_filenames, get_filenames_in_dir, get_key_of_value, 
)

from category_constants import TAGS

# References:
# https://daleonai.com/social-media-fashion-ai

INSPO_DIR = 'inspo/'

OUTFITS = Closet().get_outfits()

PLURAL_TO_SINGULAR_MAPPING = {
    'tops': 'top',
    'bottoms': 'bottom', 
    'dresses': 'dress',   
}


def init_category_display(images_per_row):
    placeholders = {}
    cols_info = {}
    col_inds = {}
    for cat in [
        'Tops', 'Bottoms', 'Dresses/Sets', 'Outerwear', 'Shoes', 'Bags', 'Unknown'
    ]:
        st.subheader(cat)
        placeholders[cat] = st.container()
        cols_info[cat] = placeholders[cat].columns(images_per_row)
        col_inds[cat] = 0

    return cols_info, col_inds


def get_final_label_from_labels(labels):
    """Get the final label from a list of labels.

    Parameters
    ----------
    labels : list 

    Returns
    -------
    str
    """
    category_mapping = {
        'Tops': {'Top', 'Shirt'},
        'Bottoms': {'Skirt', 'Shorts', 'Pants', 'Jeans'},
        'Dresses/Sets': {'Dress'},
        'Outerwear': {'Outerwear', 'Coat'},
        'Shoes': {'Shoe', 'High heels', 'Footwear'},
        'Bags': {'Bag'},
    }

    if len(set(labels)) == 1:
        return get_key_of_value(category_mapping, labels[0])
    if any(label in category_mapping['Outerwear'] for label in labels):
        return 'Outerwear'
    if any(label in category_mapping['Tops'] for label in labels):
        return 'Tops'

    labels = [
        x for x in labels
        if get_key_of_value(category_mapping, x) not in ('Shoes', 'Bags')
    ]
    if len(set(labels)) == 1:
        return get_key_of_value(category_mapping, labels[0])

    print(f"Unknown labels: {labels}") 
    return 'Unknown'


def categorize_wardrobe_style(items):
    st.subheader('About')
    st.write(
        "Items here are separated into 'Basic' pieces (i.e. items that are "
        "simple, solid colored, and able to match to many other items) and "
        "'Statement' pieces (items that are colorful, patterned, and not likely"
        " to match to many other items). \n \n"                
        "In order to limit manual user oversight and prevent user fatigue, a "
        "CNN Image Classification model was trained on 15000+ labeled images "
        "and was used to predict the appropriate category an item should fall "
        "into. The algorithm then uses this information to determine how to "
        "style clothing articles together. \n \n"
        "Keep in mind however, that the model may fail at times to categorize " 
        "properly; in such a case, the user has the option to update the tags " 
        "manually."
    )

    pattern_model = load_model('model.hdf5')

    images = []
    images_processed = []
    for cat in items:
        for item in items[cat]: 
            print('Processing image...')
            images.append(item)
            images_processed.append(image_processing(item))

    X = np.array(images_processed) / 255
    img_rows, img_cols = 100, 100

    X = X.reshape(X.shape[0], img_rows, img_cols, 1)
    print('Predicting style of item...')
    preds = pattern_model.predict(X)

    styles = {}
    for image, pred in zip(images, preds):
        cat_pred = np.argmax(pred)
        if cat_pred == 8:
            cat_pred = 'Basic'
        else:
            cat_pred = 'Statement'

        styles[cat_pred] = styles.get(cat_pred, []) + [image]

    for style in styles:
        st.subheader(f'{style} Pieces')
        st.image(styles[style], width=150)


def categorize_wardrode(filepaths):
    ps = get_product_search()
    product_set = ps.getProductSet(st.secrets['CLOSET_SET'])

    # with open('model.hdf5', 'rb') as f:
    #    pattern_model = pickle.load(f)

    images_per_row = 10
    cols_info, col_inds = init_category_display(images_per_row)

    all_paths = []
    for cat in filepaths:
        all_paths += filepaths[cat]

    for filepath in all_paths:
        response = product_set.search("apparel", file_path=filepath)
        labels = [x['label'] for x in response]

        label = get_final_label_from_labels(labels)
        cols_info[label][col_inds[label]].image(filepath)

        # Add one to column indices count
        # Restart column count after it reachs end of row
        col_inds[label] += 1
        if col_inds[label] >= images_per_row:
            col_inds[label] = 0


def option_one_questions():
    options = ['Summer', 'Autumn', 'Winter', 'Spring']
    season = st.sidebar.selectbox("What's the season?", options)

    options = ['Hot', 'Warm', 'Mild', 'Chilly', 'Cold', 'Rainy']
    weather = st.sidebar.selectbox("What is the weather today?", options)

    options = ['Casual', 'Work', 'Dinner/Bar', 'Club/Fancy']
    occasion = st.sidebar.selectbox("What is the occasion?", options)

    return season, weather, occasion


def get_outfit_plan_question_responses():
    side = st.sidebar
    form = side.form('Plan')

    options = ['Work', 'Casual', 'Dinner/Bar', 'Club/Fancy']
    q = "What occasions are you planning for?"
    occasions = form.multiselect(q, options)

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


def get_product_search():
    return ProductSearch(
        st.secrets['GCP_PROJECTID'], 
        st.secrets['CREDS'], 
        st.secrets['CLOSET_SET'],
        st.secrets['gcp_service_account'],
    )


def get_outfit_match_from_inspo(items, filepath=None, uri=None):
    ps = get_product_search()
    product_set = ps.getProductSet(st.secrets['CLOSET_SET'])
    # `response` returns matches for every detected clothing item in image
    response = product_set.search("apparel", file_path=filepath, image_uri=uri)
    # url_path = 'https://storage.googleapis.com/closet_set/'

    match_scores = []
    outfit_pieces = {}
    for item in response:
        st.write(item)
        for match in get_viable_matches(item['label'], item['matches']):
            category = match['product'].labels['type']
            filename = match['image'].split('/')[-1]
            filepath = f"closet/{category}/{filename}"

            # Add if item exists in closet set
            if filepath in items[category]:
                outfit_pieces[category] = filepath  # match['image'])
                match_scores.append(match['score'])
 
    if match_scores:
        outfit_match_score = sum(match_scores) * 100 / len(match_scores)
        st.subheader('Outfit Match')
        st.write(
            "These are the items in your closet that most closely resemble the "
            "above outfit."
        )
        st.write(f'Match Score: {outfit_match_score:.2f}')
        display_outfit_pieces(outfit_pieces)
        st.button("This doesn't match together.")
    else:
        st.subheader('No matches found in closet.')


def get_and_add_filters(session_state):
    st.sidebar.header("Filters")
    form = st.sidebar.form('Tags')
    seasons = form.multiselect('Seasons', list(TAGS['season'].keys()))
    occasions = form.multiselect('Occasions', list(TAGS['occasion'].keys()))

    if form.form_submit_button('Add Filters'):
        if not occasions:
            st.error('Please select occasion types above first.')
        else:
            session_state.items_filtered = filter_items_in_all_categories(
                items, seasons, occasions
            )
            session_state.outfits_filtered = filter_appropriate_outfits(
                OUTFITS, seasons, occasions,
            )

        info_placeholder.subheader('Post Filter')
        count_outfits(
            info_placeholder,
            session_state.outfits_filtered,
            session_state.items_filtered,
        )

    st.sidebar.header("Options")
    if not seasons or not occasions:
        st.sidebar.warning(
            "NOTE: No filters selected. Please select filters above and click " 
            "'Add Filters'."
        )
    else:
        st.sidebar.success('Filters selected.')

    return session_state, seasons, occasions


def init_session_state():
    return SessionState.get(
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


st.image('header4.jpeg')

st.title("AIsthetic: Wardrobe Optimization")
st.write('')

with st.expander("Information on Wardrobe Data"):
    st.write(
        "*This application is currently running on demo data (i.e. my personal "
        "closet). If there will be a need, it can be updated to intake and run "
        "on other users' individual wardrobe data."
    )

items = get_all_image_filenames()

st.header('Closet Information')

info_placeholder = st.container()
print('Counting items...')
info_placeholder.subheader('Entire Wardrobe')
count_outfits(info_placeholder, OUTFITS, items)

st.header('AIsthetic Algorithm')
options = [
    'Use mock data for testing',
    'Upload my own closet',
]

closet_option = st.radio("Which closet would you like to use?", options)

if closet_option == options[1]:
    st.write(
        "The app currently runs on demo data only. If you would like to upload "
        "and run on your personal wardrobe data, please have some investors "
        "send over funding in order for me to continue developing this "
        "further;) \n\n Or if you would really like to use this app for "
        "personal use, let me know and I can send over the beta version for you"
        " to test out (as long as you don't mind a few bugs and potential "
        "tweaks that will need to be made)."
    )

options = [
    "See all clothing articles in closet.",
    "Select a random outfit combination from closet.",
    "Select an outfit based on an inspo-photo.",
    "Plan a set of outfits for a trip.",
]

option = st.radio("What would you like to do?", options)


######################################
######################################
# Side Bar ###########################
######################################
######################################


if option == options[0]:
    session_state = init_session_state()
    session_state, seasons, occasions = get_and_add_filters(session_state)

    if st.sidebar.button('Show Wardrode Info'):
        if not seasons or not occasions:
            st.sidebar.error('Please add filters first.')
        else:
            print('Printing wardrobe info...')
            categorize_wardrobe_style(session_state.items_filtered)

    if st.sidebar.button('Display Clothing Tags'):
        if not seasons or not occasions:
            st.sidebar.error('Please add filters first.')
        else:
            display_article_tags(session_state.items_filtered)

    form = st.sidebar.form('Choose Filename')
    session_state.item = choose_filename_to_update(items)

    # If there are items that are untagged, include options to review
    if session_state.item:
        button_clicked = st.sidebar.button('Review Article Tags')
        if button_clicked:
            session_state.button_clicked = True

        if session_state.button_clicked:
            update_article_tags(session_state.item)
    else:
        st.sidebar.write('All items have been tagged.')
elif option == options[1]:
    st.sidebar.header("Options")
    season, weather, occasion = option_one_questions()
    if st.sidebar.button('Select Random Outfit'):
        st.header('Selected Outfit')
        outfit = choose_outfit(OUTFITS, weather, occasion)
        if outfit:
            display_outfit_pieces(outfit)
            st.button("This doesn't match together.")
        else:
            st.text("NO APPROPRIATE OPTIONS FOR THE WEATHER AND OCCASION.")
elif option == options[2]:
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
                get_outfit_match_from_inspo(items, filepath=image)
            else:
                get_outfit_match_from_inspo(items, uri=image)
else:
    st.sidebar.header("Options")
    st.session_state.outfit_plans = {}
    st.session_state.outfit_plans = get_and_display_outfit_plan() 

    if st.session_state.outfit_plans:
        if st.button('Save Outfit Plan'):
            with open('outfit_plans', 'w') as f:
                json.dump(st.session_state.outfit_plans, f)

            print('Outfit Plan saved to file.')
