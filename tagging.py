import os
import streamlit as st

from category_constants import TAGS


# to map article season types to weather icon filenames
_style_icon_filenames = {
    'Basic': 'basic.png',
    'Statement': 'statement.png',
}

_season_icon_filenames = {
    'Summer': 'sunny.png',
    'Fall': 'cloudy.png',
    'Winter': 'cold.png',
    'Spring': 'partly_cloudy.png',
}

_occasion_icon_filenames = {
    'Casual': 'casual.png',
    'Work': 'work.png',
    'Dinner/Bar': 'bar.png',
    'Club/Fancy': 'party.png',
}

FILENAME_MAPPINGS = {
    'style': _style_icon_filenames,
    'season': _season_icon_filenames,
    'occasion': _occasion_icon_filenames
}


# includes icon paths
ICON_PATHS = {}
for icon_type, filenames in FILENAME_MAPPINGS.items():
    ICON_PATHS[icon_type] = {}
    for description, filename in filenames.items():
        ICON_PATHS[icon_type][description] = f'icons/{icon_type}/{filename}'

ICON_IMAGE_WIDTH = 40


def display_icon_key():
    """Display all icon descriptions and icon images for all categories.

    Icon categories include 'style', 'season', and 'occasion'.
    """
    st.subheader('Key')
    cols = st.columns(6)

    i = 0
    for _, icon_paths in ICON_PATHS.items():
        for k in sorted(icon_paths.keys()):
            cols[i].text(k)
            cols[i].text(' ')
            cols[i+1].image(icon_paths[k], width=ICON_IMAGE_WIDTH)
        i += 2

    st.markdown("""---""")


def display_article_tags_for_item(col, item):
    """Display item image with tags below.
    """
    col.image(item, width=150)
    for icon_type, icon_paths in ICON_PATHS.items():
        icons = []
        for k in sorted(icon_paths.keys()):
            if TAGS[icon_type][k] in item:
                icons.append(icon_paths[k])

        col.image(icons, width=ICON_IMAGE_WIDTH)


def display_article_tags(items):
    display_icon_key()

    num_cols = 3
    for cat in items:
        st.subheader(cat)
        st.markdown("""---""")

        cols = st.columns(num_cols)
        col_i = 0
        for item in items[cat]:
            display_article_tags_for_item(cols[col_i], item)

            if col_i == num_cols - 1:
                col_i = 0
            else:
                col_i += 1

            cols[col_i].markdown("""---""")


def choose_filename_to_update(filepaths):
    image_filenames = []
    for cat in filepaths:
        image_filenames += [x for x in filepaths[cat]]

    missing_tags = [
        x for x in image_filenames if (
            not any(tag in x for tag in TAGS['style'].values())
            or not any(tag in x for tag in TAGS['season'].values())
            or not any(tag in x for tag in TAGS['occasion'].values())
        )
    ]
    if missing_tags:
        info = (
            f"These {len(missing_tags)} clothing articles have not been tagged"
            "with a style, season, or occasion type yet:"
        )

        return st.sidebar.selectbox(info, missing_tags)


def update_article_tags(filepath):
    cols = st.columns(3)
    display_article_tags_for_item(cols[0], filepath)

    form = st.form('tags')
    style = form.selectbox('Style?', list(TAGS['style'].keys()))
    seasons = form.multiselect('Season?', list(TAGS['season'].keys()))
    occasions = form.multiselect('Occasion?', list(TAGS['occasion'].keys()))

    filename_parts = filepath.split('.')

    if form.form_submit_button('Finished Adding Tags'):
        tag = TAGS['style'][style]
        for season in seasons:
            tag += TAGS['season'][season]
        for occasion in occasions:
            tag += TAGS['occasion'][occasion]

        os.rename(
            filepath, f'{filename_parts[0]}_{tag}.{filename_parts[1]}'
        )
