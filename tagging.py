import os
import streamlit as st

from typing import Dict, List, Tuple

from utils import increment_i

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

ICON_PATHS = {}
for tag_type, icons in FILENAME_MAPPINGS.items():
    ICON_PATHS[tag_type] = {
        k: f'icons/{tag_type}/{v}' for k, v in icons.items()
    }

ICON_IMAGE_WIDTH = 40


def display_icon_key():
    """Display all icon descriptions and icon images for all categories.

    Icon categories include 'style', 'season', and 'occasion'.

    Used within 'View all clothing articles' view.
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


def display_article_tags_for_item(col, item_name: str, item_tags):
    """Display item image with tags below.

    Used within 'View all clothing articles' view and within 'Update tags' view.
    """
    col.image(item_name, width=150)
    for tag_type in item_tags:
        icons = []
        # `style` will contain a str
        if tag_type == 'style':
            tag = item_tags[tag_type]
            icons.append(ICON_PATHS[tag_type][tag])
        # `season` and `occasion` will contain lists
        else:
            for tag in item_tags[tag_type]:
                icons.append(ICON_PATHS[tag_type][tag])

        col.image(icons, width=ICON_IMAGE_WIDTH)


def display_article_tags():
    """Display article tags.

    If `item_tags` is null, takes tags information from item filenames.
    """
    display_icon_key()

    num_cols = 3
    for cat in st.session_state['items_filtered']:
        st.subheader(cat)
        st.markdown("""---""")

        cols = st.columns(num_cols)
        col_i = 0
        for item in st.session_state['items_filtered'][cat]:
            if isinstance(item, str):
                item_name = item
            else:
                item_name = item.name
            item_tags = st.session_state['items_tags'][cat][item_name]

            display_article_tags_for_item(cols[col_i], item, item_tags)
            col_i = increment_i(col_i, num_cols - 1)
            cols[col_i].markdown("""---""")
