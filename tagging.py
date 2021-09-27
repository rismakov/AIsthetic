import os
import streamlit as st

from category_constants import ALL_CATEGORIES, OCCASION_TAGS, STYLE_TAGS, SEASON_TAGS
from utils_constants import PATH_CLOSET

from utils import get_filesnames_in_dir


STYLE_ICON_PATH = 'icons/style'
WEATHER_ICON_PATH = 'icons/weather'
OCCASION_ICON_PATH = 'icons/occasion'

# to map article season tags to weather icon filenames
SEASON_ICON_MAPPING = {
    'Summer': 'sunny.png',
    'Fall': 'cloudy.png',
    'Winter': 'cold.png',
    'Spring': 'partly_cloudy.png',
}

OCCASION_ICON_MAPPING = {
    'Casual': 'casual.png',
    'Work': 'work.png',
    'Dinner/Bar': 'bar.png',
    'Club/Fancy': 'party.png',
}

ICON_IMAGE_WIDTH = 40

def display_style_tag(col, image_filename):
    for style in ['Basic', 'Statement']:
        if STYLE_TAGS[style] in image_filename:
            icon_filename = f'{STYLE_ICON_PATH}/{style.lower()}.png'
            col.image(icon_filename, width=ICON_IMAGE_WIDTH)


def display_tags(col, image_filename, icon_image_mapping, tags, icon_path):
    icons = []
    for k in sorted(icon_image_mapping.keys()):
        if tags[k] in image_filename:
            icon_filename = f'{icon_path}/{icon_image_mapping[k]}'
            icons.append(icon_filename)
    
    col.image(icons, width=ICON_IMAGE_WIDTH)


def add_later():
    for button in buttons:
        
        style = form.selectbox('Style?', ['Basic', 'Statement'])
        seasons = form.multiselect('Season?', SEASON_ICON_MAPPING.keys())
        occasions = form.multiselect('Occasion?', ['Casual', 'Work'])

        if form.form_submit_button(f'{i}'):
            tag = f'{STYLE_TAGS[style]}'
            for season in seasons:
                tag += SEASON_TAGS[season]
            for occasion in occasions:
                tag += OCCASION_TAGS[occasion]
            
            os.path.rename(filename, f'{filename}_{tag}')


def display_article_tags_for_item(col, image_filename):
    col.image(image_filename, width=150)
    
    display_style_tag(col, image_filename)
    display_tags(
        col, 
        image_filename, 
        SEASON_ICON_MAPPING, 
        SEASON_TAGS, 
        WEATHER_ICON_PATH,
    )
    display_tags(
        col, 
        image_filename, 
        OCCASION_ICON_MAPPING, 
        OCCASION_TAGS, 
        OCCASION_ICON_PATH,
    )


def display_article_tags(filepaths):
    num_cols = 3
    cols = st.beta_columns(num_cols)

    for cat in filepaths:
        st.subheader(cat)
        st.markdown("""---""")

        col_i = 0
        for i, image_filename in enumerate(filepaths[cat]):
            col = cols[col_i]
            display_article_tags_for_item(col, image_filename)

            if col_i == num_cols - 1:
                col_i = 0
            else:
                col_i += 1
        
            col.markdown("""---""")
 
def choose_filename_to_update(filepaths):
    image_filenames = []
    for cat in filepaths:
        image_filenames += [x for x in filepaths[cat]]

    missing_tags = [
        x for x in image_filenames if (
            not any(tag in x for tag in STYLE_TAGS.values()) 
            or not any(tag in x for tag in SEASON_TAGS.values()) 
            or not any(tag in x for tag in OCCASION_TAGS.values()) 
        )
    ]
    info = (
        f'These {len(missing_tags)} clothing articles have not been tagged with'
        ' a style, season, or occasion type yet:'
    )

    return st.sidebar.selectbox(info, missing_tags)

def update_article_tags(filepath):
    cols = st.beta_columns(3)
    display_article_tags_for_item(cols[0], filepath)

    form = st.form('tags')
    style = form.selectbox('Style?', list(STYLE_TAGS.keys()))
    seasons = form.multiselect('Season?', list(SEASON_TAGS.keys()))
    occasions = form.multiselect('Occasion?', list(OCCASION_TAGS.keys()))
    
    filename_parts = filepath.split('.')
        
    if form.form_submit_button('Finished Adding Tags'):
        tag = STYLE_TAGS[style]
        for season in seasons:
            tag += SEASON_TAGS[season]
        for occasion in occasions:
            tag += OCCASION_TAGS[occasion]
        
        os.rename(
            filepath, f'{filename_parts[0]}_{tag}.{filename_parts[1]}'
        )
