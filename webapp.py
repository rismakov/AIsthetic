import os
import numpy as np
import requests
import streamlit as st
import SessionState

from tensorflow.keras.models import load_model

from ProductSearch import ProductSearch, ProductCategories
from get_weather import get_projected_weather
from image_processing import image_processing
from matching_utils import get_viable_matches
from outfit_calendar import (
    choose_outfit, get_outfit_plan, display_outfit_pieces, display_outfit_plan, 
)
from outfit_utils import (
    filter_basic_items,
    filter_items_based_on_amount, 
    filter_items_in_all_categories,
    filter_statement_items,
)
from tagging import (
    choose_filename_to_update, display_article_tags, update_article_tags
)
from utils import get_filesnames_in_dir, get_key_of_value

from category_constants import (
    ALL_CATEGORIES, SEASON_TAGS, STYLE_TAGS, OCCASION_TAGS, WEATHER_TO_SEASON_MAPPINGS
)
from utils_constants import PATH_CLOSET

DAYS_IN_WEEK = {
    'Casual': 7,
    'Dinner/Bar': 7,
    'Club/Fancy': 7,
    'Work': 5,
}

# References:
# https://daleonai.com/social-media-fashion-ai

INSPO_DIR = 'inspo/'

INDENT = '&nbsp;&nbsp;&nbsp;&nbsp;'

IMAGE_SIZE = (96, 96) # (224, 224)

OUTFIT_COLS = [0, 2, 4, 0, 2, 4]


def get_all_image_filenames() -> dict:
    filepaths = {}
    for cat in ALL_CATEGORIES:
        directory = f'{PATH_CLOSET}/{cat}'
        filepaths[cat] = [
            f'{directory}/{fn}' for fn in get_filesnames_in_dir(directory)
        ]
    return filepaths


def get_basics_and_statements(filepaths):
    count = 0
    basics = []
    statements = []
    for cat in filepaths:
        count += len(filepaths[cat])
        for path in filepaths[cat]:
            if STYLE_TAGS['Basic'] in path: 
                basics.append(path)
            elif STYLE_TAGS['Statement'] in path: 
                statements.append(path)
    return count, basics, statements


def count_items(filepaths, info_placeholder):
    count, basics, statements = get_basics_and_statements(filepaths)

    combo_count = (
        # basic tops + basic bottoms
        (
            len(filter_basic_items(filepaths['tops'])) 
            * len(filter_basic_items(filepaths['bottoms']))
        )
        # basic tops + statement bottoms
        + (
            len(filter_statement_items(filepaths['tops'])) 
            * len(filter_basic_items(filepaths['bottoms']))
        ) 
        # statement tops + basic bottoms
        + (
            len(filter_basic_items(filepaths['tops'])) 
            * len(filter_statement_items(filepaths['bottoms']))
        )
        # dresses + sets
        + len(filepaths['dresses'])
    )

    info_placeholder.write(
        f'You have {count} items in your closet and {combo_count} unique '
        'top/bottom outfit combinations.'
    )

    basic_count, statement_count = len(basics), len(statements)
    total = basic_count + statement_count
    info_placeholder.write(
        f'- This includes {basic_count} basic pieces '
        f'({basic_count * 100 / total:.2f}%) and {statement_count} statement '
        f'pieces ({statement_count * 100 / total:.2f}%).'
    )
    info = '- '
    for cat in ALL_CATEGORIES:
        info += f'{len(filepaths[cat])} {cat}, '
    
    info_placeholder.write(f'{info[:-2]}.')


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


def categorize_wardrobe_style(filepaths):
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
    for cat in filepaths:
        for filepath in filepaths[cat]: 
            print('Processing image...')
            images.append(filepath)
            images_processed.append(image_processing(filepath))

    X = np.array(images_processed) / 255
    img_rows, img_cols = 100, 100
    input_shape = (img_rows, img_cols, 1)

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

def get_and_display_outfit_plan():
    side = st.sidebar
    form = side.form('Plan')

    options = ['Work', 'Casual', 'Dinner/Bar', 'Club/Fancy']
    q = "What occasions are you planning for?"
    occasions = form.multiselect(q, options)

    accessories_mapping = {'Yes': True, 'No': False}

    options = ['Yes', 'No']
    include = form.selectbox("Would you like to include accessories?", options)

    options = ['small carry-on suitcase', 'medium suitcase', 'entire closet']
    amount = form.selectbox("How much are you looking to bring?", options)

    city = form.text_input("Which city are you traveling to?").lower().strip()
    country = form.text_input("Country?").lower().strip()

    start_date = form.date_input("When are you starting your trip?")
    end_date = form.date_input("When are you ending your trip?")

    if form.form_submit_button("Create Outfit Plan"):
        if end_date < start_date:
            form.error("ERROR: end date cannot be before start date.")
        else:
            weather_info = get_projected_weather(
                city, country, start_date, end_date
            )
            if not weather_info['temps']:
                st.error(
                    "ERROR: Weather information not found. Confirm that city "
                    "and country names are filled in and spelled correctly."
                )
            else:
                seasons = get_season_types_from_weather_info(
                    weather_info['weather_types']
                )

                # Make sure items of all necessary season types are available, 
                # depending on set of all weather types of trip
                filepaths_filtered = filter_items_in_all_categories(
                    filepaths, seasons=seasons, occasions=occasions
                )

                st.subheader('Options Available')
                info_placeholder = st.container()           
                count_items(filepaths_filtered, info_placeholder)

                filepaths_filtered = filter_items_based_on_amount(
                    filepaths_filtered, amount, occasions, seasons,
                )

                for occasion in occasions:
                    st.header(f'{occasion}')
                    st.markdown("""---""")
                    days_in_week = DAYS_IN_WEEK[occasion]
                    dates, outfits = get_outfit_plan(
                        filepaths_filtered, 
                        weather_info['weather_types'], 
                        occasion,
                        city, 
                        start_date, 
                        end_date,
                        amount, 
                        accessories_mapping[include],
                    )

                    display_outfit_plan(dates, outfits, weather_info, days_in_week)


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


def get_outfit_match_from_inspo(filepath=None, uri=None):
    ps = get_product_search()
    product_set = ps.getProductSet(st.secrets['CLOSET_SET'])
    # `response` returns matches for every detected clothing item in image
    response = product_set.search("apparel", file_path=filepath, image_uri=uri)
    # url_path = 'https://storage.googleapis.com/closet_set/'

    filepaths = get_all_image_filenames()

    match_scores = []
    outfit_pieces = {}
    for item in response:
        for match in get_viable_matches(item['label'], item['matches']):
            category = match['product'].labels['type']
            filename = match['image'].split('/')[-1]
            filepath = f"closet/{category}/{filename}"

            # Add if item exists in closet set
            if filepath in filepaths[category]:
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
    else:
        st.subheader('No matches found in closet.')

######################################
######################################
# Main Screen ########################
######################################
######################################
st.image('header4.jpeg')

st.title("AIsthetic: Wardrobe App")
st.write('')

st.write(
    "*This application is currently running on demo data (i.e. my personal "
    "closet). If there will be a need, it can be updated to intake and run on "
    "other users' individual wardrobe data."
)

filepaths = get_all_image_filenames()

st.header('Closet Information')
info_placeholder = st.container()
print('Counting items...')
info_placeholder.subheader('Entire Wardrobe')
count_items(filepaths, info_placeholder)

st.header('AIsthetic Algorithm')
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

session_state = SessionState.get(
    filepath="", button_clicked=False, filepaths_filtered=[],
)

if option == options[0]:
    st.sidebar.header("Filters")
    form = st.sidebar.form('Tags')
    seasons = form.multiselect('Seasons', list(SEASON_TAGS.keys()))
    occasions = form.multiselect('Occasions', list(OCCASION_TAGS.keys()))

    if form.form_submit_button('Add Filters'):
        if not occasions:
            st.error('Please select occasion types above first.')
        else: 
            session_state.filepaths_filtered = filter_items_in_all_categories(
                filepaths, seasons, occasions
            )
            info_placeholder.subheader('Post Filter')
            count_items(session_state.filepaths_filtered, info_placeholder)
    
    st.sidebar.header("Options")
    if not seasons or not occasions:
        st.sidebar.write(
            "NOTE: No filters selected. Please select filters above and click " 
            "'Add Filters'."
        )
    else:
        st.sidebar.write('Filters selected.')

    if st.sidebar.button('Show Wardrode Info'):
        if not seasons or not occasions:
            st.sidebar.error('Please add filters first.')
        else:
            print('Printing wardrobe info...')
            categorize_wardrobe_style(session_state.filepaths_filtered)

    if st.sidebar.button('Display Clothing Tags'):
        if not seasons or not occasions:
            st.sidebar.error('Please add filters first.')
        else:
            display_article_tags(session_state.filepaths_filtered)

    form = st.sidebar.form('Choose Filename')
    session_state.filepath = choose_filename_to_update(filepaths)

    # If there are items that are untagged, include options to review
    if session_state.filepath:
        button_clicked = st.sidebar.button('Review Article Tags')
        if button_clicked:
            session_state.button_clicked = True
        
        if session_state.button_clicked:
            update_article_tags(session_state.filepath)
    else:
        st.sidebar.write('All items have been tagged.')
elif option == options[1]:
    st.sidebar.header("Options")
    season, weather, occasion = option_one_questions()
    if st.sidebar.button('Select Random Outfit'):
        st.header('Selected Outfit')
        outfit_pieces = choose_outfit(filepaths, weather, occasion)
        display_outfit_pieces(outfit_pieces)
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
                get_outfit_match_from_inspo(filepath=image)
            else:
                get_outfit_match_from_inspo(uri=image)
else:
    st.sidebar.header("Options")
    get_and_display_outfit_plan()   
