import streamlit as st
import json
from typing import Dict, List, Tuple

from info_material import items_tags_upload_success_info, upload_tags_info
from setup_tags import is_end_of_category
from state_updates import update_upload_state
from tagging import display_icon_key

from category_constants import ALL_CATEGORIES


def upload_items() -> dict:
    """Get file uploaders to upload user-specified closet items.
    """
    st.subheader('Upload Closet Items')
    for cat in ALL_CATEGORIES:
        st.session_state['items'][cat] = st.file_uploader(
            f'Please select all {cat} items',
            key=cat,
            accept_multiple_files=True,
        )


def upload_closet_setup_items():
    """Prompt user to upload closet tags, closet items, and closet outfits.
    """
    st.header('Upload Closet')

    upload_tags_info()
    items_tags = st.file_uploader('Please select your closet tags json file')
    if items_tags:
        st.session_state['items_tags'] = json.load(items_tags)
        items_tags_upload_success_info(st.session_state['items_tags'])

    upload_items()
    st.button('Finished uploading items and tags', on_click=update_upload_state)
