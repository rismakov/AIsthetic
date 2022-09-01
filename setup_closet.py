import base64
import os
import json
import pickle
import uuid
import re

import streamlit as st
import pandas as pd
import streamlit as st

from typing import Dict, List, Tuple

from info_material import tagging_session_info
from tagging import display_icon_key

from category_constants import ALL_CATEGORIES, TAGS


def upload_items() -> List[str]:
    uploaded_items = {}
    for cat in ALL_CATEGORIES:
        uploaded_items[cat] = st.file_uploader(
            f'Please select all {cat} items',
            key=cat,
            accept_multiple_files=True,
        ) 
    return uploaded_items


def get_next_cat_i(items, cats, ss):
    """Get the next category index with items available.

    Parameters
    ----------
    items : Dict[str, list]
    cats : List[str]
        The categories in `items`.
    ss : int
        The session state. Used to keep track of `cat_i` increments.

    Returns
    -------
    int
    """
    ss.cat_i += 1

    # return null if `cat_i` is greater than number of categories
    if ss.cat_i == len(cats):
        ss.cat_i = None
        return

    # skip category if it includes no items
    if len(items[cats[ss.cat_i]]) == 0:
        get_next_cat_i(items, cats, ss)

    return ss.cat_i


def select_article_tags() -> Tuple[int, Dict[str, List[str]]]:
    form = st.form('tags')
    style = form.selectbox('Style?', list(TAGS['style'].keys()))
    seasons = form.multiselect('Season?', list(TAGS['season'].keys()))
    occasions = form.multiselect('Occasion?', list(TAGS['occasion'].keys()))

    if form.form_submit_button('Finished Adding Tags'):
        return {
            'style': style,
            'season': seasons,
            'occasion': occasions,
        }


def get_cat_and_item_inds(ss, cats, items):
    cat = cats[ss.cat_i]
    # continue to next non-empty category if end of items in current category
    if ss.item_i == len(items[cat]):
        ss.cat_i = get_next_cat_i(items, cats, ss)
        ss.item_i = 0

    # exit function if finished scrolling through all categories
    if ss.cat_i is None:
        ss.is_item_tag_session = False
        ss.finished_tag_session = True

    return ss


def download_button(
    object_to_download,
    download_filename: str,
    button_text: str,
    pickle_it=False,
):
    """
    Generates a link to download the given object_to_download.

    Parameters
    ----------
    object_to_download
        The object to be downloaded.
    download_filename : str
        Filename and extension of file. e.g. mydata.csv, some_txt_output.txt
    download_link_text : str
        Text to display for download link.
    button_text : str
        Text to display on download button (e.g. 'click here to download file').
    pickle_it : bool
        If True, pickle file.

    Returns
    -------
    str
        The anchor tag to download object_to_download

    Examples:
    --------
    download_button(your_df, 'YOUR_DF.csv', 'Click to download data!')
    download_button(your_str, 'YOUR_STRING.txt', 'Click to download text!')
    """
    if pickle_it:
        try:
            object_to_download = pickle.dumps(object_to_download)
        except pickle.PicklingError as e:
            st.write(e)
            return None

    else:
        if isinstance(object_to_download, bytes):
            pass

        elif isinstance(object_to_download, pd.DataFrame):
            object_to_download = object_to_download.to_csv(index=False)

        # Try JSON encode for everything else
        else:
            object_to_download = json.dumps(object_to_download)

    try:
        # some strings <-> bytes conversions necessary here
        b64 = base64.b64encode(object_to_download.encode()).decode()

    except AttributeError as e:
        b64 = base64.b64encode(object_to_download).decode()

    button_uuid = str(uuid.uuid4()).replace('-', '')
    button_id = re.sub('\d+', '', button_uuid)

    custom_css = f""" 
        <style>
            #{button_id} {{
                background-color: rgb(255, 255, 255);
                color: rgb(38, 39, 48);
                padding: 0.25em 0.38em;
                position: relative;
                text-decoration: none;
                border-radius: 4px;
                border-width: 1px;
                border-style: solid;
                border-color: rgb(230, 234, 241);
                border-image: initial;
            }} 
            #{button_id}:hover {{
                border-color: rgb(246, 51, 102);
                color: rgb(246, 51, 102);
            }}
            #{button_id}:active {{
                box-shadow: none;
                background-color: rgb(246, 51, 102);
                color: white;
                }}
        </style> """

    dl_html_part = f'<a download="{download_filename}"'
    id_html_part = f'id="{button_id}" href="data:file/txt;base64'
    button_html_part = f',{b64}">{button_text}</a><br></br>'
    dl_link = custom_css + f'{dl_html_part} {id_html_part}{button_html_part}'

    return dl_link


def tag_items(ss, items: Dict[str, list]) -> Dict[str, list]:
    """Add tags to items missing tags.

    Returns `items_tags` with tags included where they were previously missing.

    Parameters
    ----------
    ss : session_state
    items : Dict[str, list]

    Returns
    -------
    Dict[str, List[Dict[str, List[str]]]]
        example: {
                'tops': [
                    {'style': [...], 'occasion': [...], 'weather': [...]},
                    ...
                ],
                'bottoms': [{...}, {...}, ...],
                ...
            }
            items_tags[cat] --> item_tags --> item_tag_type_tags
    """
    display_icon_key()

    cats = list(items.keys())

    ss = get_cat_and_item_inds(ss, cats, items)
    if ss.cat_i is None:
        return ss

    # create image placeholder and display tagging form
    placeholder = st.container()
    ss.current_tags = select_article_tags()

    # if user submitted tags, append tags to list and increment item index
    if ss.current_tags:
        cat = cats[ss.cat_i]
        ss.items_tags[cat] = ss.items_tags.get(cat, []) + [ss.current_tags]
        ss.item_i += 1

    # need this here again
    ss = get_cat_and_item_inds(ss, cats, items)
    if ss.cat_i is None:
        return ss

    # display header, info and image
    cat = cats[ss.cat_i]
    if not ss.finished_tag_session:
        tagging_session_info(placeholder, cat)

    placeholder.image(items[cat][ss.item_i], width=300)

    return ss
