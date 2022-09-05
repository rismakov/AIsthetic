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

from info_material import upload_tags_info
from setup_tags import is_end_of_category, update_cat_and_item_inds
from tagging import display_icon_key

from category_constants import ALL_CATEGORIES, TAGS


def update_upload_state():
    """Update session state from 'is_closet_upload' to 'is_item_tag_session'.
    """
    st.session_state['is_closet_upload'] = False
    st.session_state['is_finished_upload'] = True
    st.session_state['is_item_tag_session'] = True


def upload_items() -> List[str]:
    st.header('Upload Closet')

    for cat in ALL_CATEGORIES:
        st.session_state['items'][cat] = st.file_uploader(
            f'Please select all {cat} items',
            key=cat,
            accept_multiple_files=True,
        )
    st.button('Finished uploading closet.', on_click=update_upload_state)


def upload_closet_setup_items():
    """Prompt user to upload closet tags, closet items, and closet outfits.
    """
    upload_tags_info()
    if st.file_uploader('Please select your closet tags json file'):
        st.session_state['finished_uploading_tags'] = True

    upload_items()
    print(st.session_state['items'])
