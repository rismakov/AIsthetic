import os
import streamlit as st
import SessionState

from constants import GCP_PROJECTID, CREDS, CLOSET_SET, LOCATION
from category_constants import ALL_CATEGORIES

from ProductSearch import ProductSearch, ProductCategories
from get_weather import get_projected_weather
from matching_utils import get_viable_matches
from outfit_calendar import (
    choose_outfit, display_outfit_pieces, display_outfit_plan, 
)
from tagging import (
    choose_filename_to_update, display_article_tags, update_article_tags
)
from utils import get_filesnames_in_dir, get_key_of_value

from category_constants import SEASON_TAGS, STYLE_TAGS, OCCASION_TAGS
from utils_constants import PATH_CLOSET

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


def filter_basic_items(items):
    return [x for x in items if STYLE_TAGS['Basic'] in x]


def filter_statement_items(items):
    return [x for x in items if STYLE_TAGS['Statement'] in x]


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


def init_category_display(images_per_row):
    placeholders = {}
    cols_info = {}
    col_inds = {}
    for cat in [
        'Tops', 'Bottoms', 'Dresses/Sets', 'Outerwear', 'Shoes', 'Bags', 'Unknown'
    ]:
        st.subheader(cat)
        placeholders[cat] = st.beta_container()
        cols_info[cat] = placeholders[cat].beta_columns(images_per_row)
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


def categorize_wardrode():
    ps = ProductSearch(GCP_PROJECTID, CREDS, CLOSET_SET)
    product_set = ps.getProductSet(CLOSET_SET)

    images_per_row = 10
    cols_info, col_inds = init_category_display(images_per_row)
    for cat in ALL_CATEGORIES:
        directory = f'{PATH_CLOSET}/{cat}'
        for filename in get_filesnames_in_dir(directory):
            file_path = os.path.join(directory, filename)
            response = product_set.search("apparel", file_path=file_path)
            labels = [x['label'] for x in response]
            
            label = get_final_label_from_labels(labels)

            cols_info[label][col_inds[label]].image(file_path)
            col_inds[label] += 1

            # restart column count after it reachs end of row
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


def option_three_questions():
    side = st.sidebar

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

    options = ['Yes', 'No']
    include = side.selectbox("Would you like to include accessories?", options)

    options = ['small carry-on suitcase', 'medium suitcase', 'entire closet']
    amount = side.selectbox("How much are you looking to bring?", options)

    city = side.text_input("Which city are you traveling to?").lower().strip()
    country = side.text_input("Country?").lower().strip()

    start_date = st.sidebar.date_input("When are you starting your trip?")
    end_date = side.date_input("When are you ending your trip?")
    if end_date < start_date:
        st.sidebar.error("ERROR: end date cannot be before start date.")

    return (
        city,
        country,
        occasions, 
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


def filter_items(
    filepaths, 
    seasons=list(SEASON_TAGS.keys()), 
    occasions=list(OCCASION_TAGS.keys())
):
    season_tags = [SEASON_TAGS[season] for season in seasons] 
    occasion_tags = [OCCASION_TAGS[occasion] for occasion in occasions]
    
    filepaths_filtered = {}
    for cat in filepaths:
        filepaths_filtered[cat] = [
            x for x in filepaths[cat] if (
                any(tag in x for tag in season_tags)
                and any(tag in x for tag in occasion_tags)
            )
        ]
    return filepaths_filtered

######################################
######################################
# Main Screen ########################
######################################
######################################
st.title("AIsthetic Wardrobe Algorithm")
st.write('')

filepaths = get_all_image_filenames()

st.header('Closet Information')
info_placeholder = st.beta_container()
print('Counting items...')
info_placeholder.subheader('Entire Wardrobe')
count_items(filepaths, info_placeholder)

st.header('AIsthetic Algorithm')
st.write("What would you like to do?")
st.write(
    """   
    1. See all clothing articles in closet.
    2. Select a random outfit combination from closet.
    3. Select an outfit based on an inspo-photo.
    4. Plan a set of outfits for the next weeks.
    """
)

options = [1, 2, 3, 4]
option = st.selectbox("Choose an option:", options)

######################################
######################################
# Side Bar ###########################
######################################
######################################

session_state = SessionState.get(
    filepath="", button_clicked=False, filepaths_filtered=[],
)

st.sidebar.header("Options")
if option == 1:
    form = st.sidebar.form('Tags')
    seasons = form.multiselect('Seasons', list(SEASON_TAGS.keys()))
    occasions = form.multiselect('Occasions', list(OCCASION_TAGS.keys()))

    if form.form_submit_button('Add Filters'):
        session_state.filepaths_filtered = filter_items(filepaths, seasons, occasions)
        info_placeholder.subheader('Post Filter')
        count_items(session_state.filepaths_filtered, info_placeholder)

    if st.sidebar.button('Show Wardrode Info'):
        print('Printing wardrobe info...')
        categorize_wardrode()
    if st.sidebar.button('Display Article Tags'):
        display_article_tags(session_state.filepaths_filtered)

    form = st.sidebar.form('Choose Filename')
    session_state.filepath = choose_filename_to_update(filepaths)
    button_clicked = st.sidebar.button('Update Article Tags')
    if button_clicked:
        session_state.button_clicked = True
    
    if session_state.button_clicked:
        update_article_tags(session_state.filepath)
        
elif option == 2:
    season, weather, occasion = option_one_questions()
    if st.sidebar.button('Select Random Outfit'):
        st.header('Selected Outfit')
        outfit_pieces = choose_outfit(filepaths, weather, occasion)
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
        city,
        country,
        occasions, 
        include_accessories,
        amount,
        start_date, 
        end_date,
    ) = option_three_questions()

    weather_info = get_projected_weather(city, country, start_date, end_date)
    # filepaths_filtered = filter_items(filepaths, occasions=occasions)

    if st.sidebar.button("Create Outfit Plan"):
        for occasion in occasions:
            st.header(f'{occasion}')
            st.markdown("""---""")
            display_outfit_plan(
                filepaths, weather_info, occasion, (end_date - start_date).days, amount, include_accessories
            )
