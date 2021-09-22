import io
import os
import numpy as np
import pandas as pd
import random
import streamlit as st
import streamlit.components.v1 as components

from google.api_core.protobuf_helpers import get_messages
from google.cloud import storage
from google.cloud import vision
from google.cloud.vision import types
# from pyvisionproductsearch import ProductSearch, ProductCategories

from numpy import asarray
from PIL import Image

from ProductSearch import ProductSearch, ProductCategories

from clothing_nodes import MATCHES
from constants import GCP_PROJECTID, CREDS, CLOSET_SET, LOCATION
from get_weather import get_projected_weather
from matching_utils import get_viable_matches
from match_constants import CATEGORIES, MATCH_GROUPS
from utils import detectLabels

# References:
# https://daleonai.com/social-media-fashion-ai

INSPO_DIR = 'inspo/'

ALL_CATEGORIES = [
    'tops', 'bottoms', 'dresses', 'hats', 'shoes', 'outerwear', 'bags', 
]
CATEGORIES_1 = [x for x in ALL_CATEGORIES if x not in ('dresses')]
CATEGORIES_2 = [x for x in ALL_CATEGORIES if x not in ('tops', 'bottoms')]
ACCESSORIES = ['bags', 'hats'] 

OCCASION_KEYS = {
    'Casual': 'ca',
    'Work': 'w',
    'Dinner/Bar': 'b',
    'Club/Fancy': 'f',
}

WEATHER_KEYS = {
    'Hot': 'h',
    'Warm': 'h',
    'Mild': 'm',
    'Chilly': 'ch',
    'Cold': 'cl',
}

INDENT = '&nbsp;&nbsp;&nbsp;&nbsp;'

IMAGE_SIZE = (96, 96) # (224, 224)

OUTFIT_COLS = [0, 2, 4, 0, 2, 4]

def get_filesnames_in_dir(dir):
    return [
        name for name in os.listdir(dir) 
        if os.path.isfile(os.path.join(dir, name)) and name != '.DS_Store'
    ]

def count_items():
    item_counts = []
    for cat in ALL_CATEGORIES:
        item_counts.append(len(get_filesnames_in_dir(f'closet/{cat}')))
    
    combo_count = sum(len(v) for k, v in MATCHES.items())
    st.text(
        f'You have {sum(item_counts)} items in your closet and {combo_count} '
        'unique outfit combinations.'
    )

def init_category_display(images_per_row):
    placeholders = {}
    cols_info = {}
    col_inds = {}
    for cat in [
        'Tops', 'Bottoms', 'Dresses/Sets', 'Outerwear', 'Shoes', 'Bags', 'Unknown'
    ]:
        st.subheader(cat)
        placeholders[cat] = st.empty()
        cols_info[cat] = placeholders[cat].beta_columns(images_per_row)
        col_inds[cat] = 0

    return cols_info, col_inds


def get_final_label_from_labels_list(labels):
    """Get the final label from a list of labels.

    Parameters
    ----------
    labels : list 

    Returns
    -------
    str
    """
    category_mapping = {
        'Top': 'Tops',
        'Shirt': 'Tops',
        'Skirt': 'Bottoms',
        'Shorts': 'Bottoms',
        'Pants': 'Bottoms',
        'Jeans': 'Bottoms',
        'Dress': 'Dresses/Sets',
        'Outerwear': 'Outerwear',
        'Coat': 'Outerwear',
        'Shoe': 'Shoes',
        'Bag': 'Bags',
    }
    if len(set(labels)) == 1:
        return category_mapping[labels[0]]
    if any(category_mapping[label] == 'Outerwear' for label in labels):
        return 'Outerwear'
    if any(category_mapping[label] == 'Tops' for label in labels):
        return 'Tops'
    
    labels = [x for x in labels if x not in ('Shoe', 'Bag')]
    if len(set(labels)) == 1:
        return category_mapping[labels[0]]
          
    return 'Unknown'


def categorize_wardrode():
    ps = ProductSearch(GCP_PROJECTID, CREDS, CLOSET_SET)
    product_set = ps.getProductSet(CLOSET_SET)

    images_per_row = 10
    cols_info, col_inds = init_category_display(images_per_row)
    for cat in ALL_CATEGORIES:
        directory = f'closet/{cat}'
        for filename in get_filesnames_in_dir(directory):
            file_path = os.path.join(directory, filename)
            response = product_set.search("apparel", file_path=file_path)
            labels = [x['label'] for x in response]
            
            label = get_final_label_from_labels_list(labels)

            if label == 'Unknown':
                print(labels)

            cols_info[label][col_inds[label]].image(file_path)
            col_inds[label] += 1

            # restart column count after it reachs end of row
            if col_inds[label] >= images_per_row:
                col_inds[label] = 0


def choose_outfit_type(include_accessories=True):
    choice = random.randint(1, 5)
    if choice == 1:
        if include_accessories:
            return CATEGORIES_2
        return [x for x in CATEGORIES_2 if x not in ACCESSORIES]

    if include_accessories:
        return CATEGORIES_1
    return [x for x in CATEGORIES_1 if x not in ACCESSORIES]


def choose_outfit(
    season, 
    weather, 
    occasion, 
    include_accessories=True,
    exclude_items=[],
):
    categories = choose_outfit_type(include_accessories)

    outfit_pieces = []

    for cat in categories:
        directory = f'closet/{cat}'
        options = sorted(get_filesnames_in_dir(directory))
        ind_options = [
            i for i, x in enumerate(options) 
            if f'{directory}/{x}' not in exclude_items
        ]
        
        if cat == 'bottoms':
            # get possible options from the matches for the chosen `top` choice
            ind_options = [
                i for i in ind_options if i + 1 in MATCHES[choice_int + 1]
            ]
        elif cat == 'shoes':
            ind_options = [
                i for i, x in enumerate(options) 
                if OCCASION_KEYS[occasion] in x.split('.')[0]
            ]
        elif cat == 'outerwear' and weather in ('Hot', 'Warm'):
            continue

        choice_int = random.choice(ind_options)
        
        filename = f'{directory}/{options[choice_int]}'
        outfit_pieces.append(filename)

    return outfit_pieces


def option_one_questions():
    options = ['Summer', 'Autumn', 'Winter', 'Spring']
    season = st.sidebar.selectbox("What's the season?", options)

    options = ['Hot', 'Warm', 'Mild', 'Chilly', 'Cold', 'Rainy']
    weather = st.sidebar.selectbox("What is the weather today?", options)

    options = ['Work', 'Casual', 'Dinner/Bar', 'Club/Fancy']
    occasion = st.sidebar.selectbox("What is the occasion?", options)

    return season, weather, occasion


def option_three_questions():
    side = st.sidebar

    options = ['Hot', 'Warm', 'Mild', 'Chilly', 'Cold', 'Rainy']
    weather = side.selectbox("What is the weather today?", options)

    options = ['Work', 'Casual', 'Dinner/Bar', 'Club/Fancy']
    q = "What occasions are you planning for?"
    occasions = side.multiselect(q, options)

    length_mapping = {
        'one week': 7,
        'two weeks': 14,
        'one month': 30,
    }
    accessories_mapping = {
        'Yes': True,
        'No': False,
    }
    options = ['one week', 'two weeks', 'one month']
    length = side.selectbox("How long is the trip?", options)

    options = ['Yes', 'No']
    include = side.selectbox("Would you like to include accessories?", options)

    options = ['small carry-on suitcase', 'medium suitcase', 'entire closet']
    amount = side.selectbox("How much are you looking to bring?", options)

    options = ['Tel Aviv', 'Palo Alto', 'London', 'New York']
    city = side.selectbox("Which city are you traveling to?", options)

    start_date = st.sidebar.date_input("When are you starting your trip?")
    end_date = side.date_input("When are you ending your trip?")

    get_projected_weather(city, start_date, end_date)

    return (
        weather,
        occasions, 
        length_mapping[length], 
        accessories_mapping[include], 
        amount,
        start_date,
        end_date,
    )

def choose_inspo_file():
    filenames = os.listdir(INSPO_DIR)
    return st.sidebar.selectbox('Select your inspo file', filenames)

def get_outfit_match_from_inspo(filename):
    ps = ProductSearch(GCP_PROJECTID, CREDS, CLOSET_SET)
    product_set = ps.getProductSet(CLOSET_SET)

    response = product_set.search("apparel", file_path=inspo_filename)
    url_path = 'https://storage.googleapis.com/closet_set/'

    match_scores = []
    image_filenames = set()
    score_header = st.empty()
    cols = st.beta_columns(6)
    i = 0
    for item_matches in response:
        for match in get_viable_matches(
            item_matches['label'], item_matches['matches']
        ):  
            if match['image'] not in image_filenames:
                print(f"{url_path}{match['image'].split('/')[-1]}")
                filename = f"{url_path}{match['image'].split('/')[-1]}"
                cols[i].image(filename, width=200)
                image_filenames.add(match['image'])

                i += 2
                if i > 4:
                    i = 0

            match_scores.append(match['score'])
    
    outfit_match_score = sum(match_scores) * 100 / len(match_scores) 
    score_header.subheader(f'Match Score: {outfit_match_score:.2f}')

def display_outfit_pieces(outfit_pieces):
    cols = st.beta_columns(6)
    for i, filename in zip(OUTFIT_COLS, outfit_pieces):
        cols[i].image(filename, width=250)
    st.button("This doesn't match together.")


def display_outfit_plan(
    season, weather, occasion, num_days, amount, include_accessories, days_in_week=7
):   
    num_cols = 3

    recent_tops = []
    recent_bottoms = []
    recent_dresses = []
    for n in range(1, num_days + 1):
        if (n - 1) % days_in_week == 0:
            st.header(f'Week {int(((n - 1) / days_in_week)) + 1}')
            cols = st.beta_columns(num_cols)

            col = 0
        
        outfit_pieces = choose_outfit(
            season, 
            weather, 
            occasion, 
            include_accessories, 
            exclude_items=recent_tops + recent_bottoms + recent_dresses
        )        
        recent_tops = [x for x in outfit_pieces if 'tops/' in x] + recent_tops
        recent_tops = recent_tops[:5]
        recent_bottoms = [x for x in outfit_pieces if 'bottoms/' in x] + recent_bottoms
        recent_bottoms = recent_bottoms[:5]
        recent_dresses = [x for x in outfit_pieces if 'dresses/' in x] + recent_dresses
        recent_dresses = recent_dresses[:5]

        cols[col].subheader(f'Day {n}')
        cols[col].image(outfit_pieces, width=70)

        cols[col].markdown("""---""")

        if col in list(range(num_cols - 1)):
            col += 1
        else:
            col = 0


######################################
######################################
# Main Screen ########################
######################################
######################################
st.title("AIsthetic Wardrobe Algorithm")
st.write('')

st.header('Closet Information')
info_placeholder = st.empty()
print('Counting items...')
count_items()

st.header('AIsthetic Algorithm')
st.write("What would you like to do?")
st.write("1. See all clothing articles in closet.")
st.write("2. Select a random outfit combination from closet.")
st.write("3. Select an outfit based on an inspo-photo.")
st.write("4. Plan a set of outfits for the next weeks.")

options = [1, 2, 3, 4]
option = st.selectbox("Choose an option:", options)

######################################
######################################
# Side Bar ###########################
######################################
######################################

st.sidebar.header("Options")
if option == 1:
    if st.sidebar.button('Show Wardrode Info'):
        print('Printing wardrobe info...')
        categorize_wardrode()
elif option == 2:
    season, weather, occasion = option_one_questions()
    if st.sidebar.button('Select Random Outfit'):
        st.header('Selected Outfit')
        outfit_pieces = choose_outfit(season, weather, occasion)
        display_outfit_pieces(outfit_pieces)
elif option == 3:
    filename = choose_inspo_file()
    if st.sidebar.button("Select Inspo-Based Outfit"):
        inspo_filename = os.path.join(INSPO_DIR, filename)
        st.header('Inspiration Match')
        st.text(f'You selected the following image as your inspiration outfit:')
        st.image(inspo_filename, width=300)
        get_outfit_match_from_inspo(filename)
else:
    (
        weather, 
        occasions, 
        num_days, 
        include_accessories, 
        amount, 
        start_date, 
        end_date,
    ) = option_three_questions()

    season = None
    if st.sidebar.button("Create Outfit Plan"):
        for occasion in occasions:
            st.header(f'{occasion}')
            st.markdown("""---""")
            display_outfit_plan(
                season, weather, occasion, num_days, amount, include_accessories
            )
