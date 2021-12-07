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
    pattern_model = load_model('model.hdf5')
    
    images = []
    images_processed = []
    for cat in filepaths:
        for filepath in filepaths[cat]: 
            print('Processing image...')
            images.append(filepath)
            images_processed.append(image_processing(filepath))
            # processed_image = image_processing()
            # st.header(processed_image.shape)

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
        st.header(f'{style} Pieces')
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

    options = ['Work', 'Casual', 'Dinner/Bar', 'Club/Fancy']
    occasion = st.sidebar.selectbox("What is the occasion?", options)

    return season, weather, occasion


def get_and_display_outfit_plan():
    side = st.sidebar
    form = side.form('Plan')

    options = ['Work', 'Casual', 'Dinner/Bar', 'Club/Fancy']
    q = "What occasions are you planning for?"
    occasions = form.multiselect(q, options)

    accessories_mapping = {
        'Yes': True,
        'No': False,
    }

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
                city, country, start_date, end_date,
            )
            if not weather_info['temps']:
                st.error(
                    'ERROR: Weather information not found. Confirm that city '
                    'and country names are filled in and spelled correctly.'
                )

            else:
                weather_type_set = set(weather_info['weather_types'])
                season_types = set([
                    WEATHER_TO_SEASON_MAPPINGS[weather_type] 
                    for weather_type in weather_type_set
                ])

                st.write(
                    "This trip requires planning for the following season types"
                    f": {', '.join(season_types)}."
                )

                # Make sure items of all necessary season types are available, depending
                # on set of all weather types of trip
                filepaths_filtered = filter_items_in_all_categories(
                    filepaths, seasons=season_types, occasions=occasions
                )

                st.subheader('Options Available')
                info_placeholder = st.container()           
                count_items(filepaths_filtered, info_placeholder)

                filepaths_filtered = filter_items_based_on_amount(
                    filepaths_filtered, amount, occasions,
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


def choose_inspo_file():
    filenames = os.listdir(INSPO_DIR)
    return st.sidebar.selectbox('Select your inspo file', filenames)


def get_product_search():
    return ProductSearch(
        st.secrets['GCP_PROJECTID'], 
        st.secrets['CREDS'], 
        st.secrets['CLOSET_SET'],
        st.secrets['gcp_service_account'],
    )


def get_outfit_match_from_inspo(filepath):
    ps = get_product_search()
    product_set = ps.getProductSet(st.secrets['CLOSET_SET'])

    print(product_set)

    response = product_set.search("apparel", file_path=filepath)
    url_path = 'https://storage.googleapis.com/closet_set/'

    match_scores = []
    image_filenames = set()
    score_header = st.empty()
    cols = st.columns(6)
    i = 0
    for item in response:
        st.write(item)
        st.write([match['product'].labels['type'] for match in item['matches']])
        for match in get_viable_matches(item['label'], item['matches']):
            category_label = match['product'].labels['type']
            filename = match['image'].split('/')[-1]
            filepath = f"{category_label}/{filename}"
            print(filepath)

            if match['image'] not in image_filenames:
                print(f"{url_path}{match['image'].split('/')[-1]}")
                # filename = f"{url_path}{match['image'].split('/')[-1]}"
                try:
                    st.write(filepath)
                    cols[i].image(filepath, width=200)
                except:
                    print(f'{filepath} doesnt exist.')
                image_filenames.add(filepath)  # match['image'])

                i += 2
                if i > 4:
                    i = 0

            match_scores.append(match['score'])
    
    if match_scores:
        outfit_match_score = sum(match_scores) * 100 / len(match_scores)
        score_header.subheader(f'Match Score: {outfit_match_score:.2f}')
    else:
        score_header.subheader('No matches found in closet.')

######################################
######################################
# Main Screen ########################
######################################
######################################
st.title("AIsthetic Wardrobe Algorithm")
st.write('')

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
    "Plan a set of outfits for the next weeks.",
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
    filename = choose_inspo_file()
    if st.sidebar.button("Select Inspo-Based Outfit"):
        filepath = os.path.join(INSPO_DIR, filename)
        st.header('Inspiration Match')
        st.text(f'You selected the following image as your inspiration outfit:')
        st.image(filepath, width=300)
        get_outfit_match_from_inspo(filepath)
else:
    st.sidebar.header("Options")
    get_and_display_outfit_plan()   
