import streamlit as st

from typing import Any, List


def update_upload_state():
    """Update session state from 'is_closet_upload' to 'is_item_tag_session'.
    """
    st.session_state['is_closet_upload'] = False
    st.session_state['is_finished_upload'] = True
    st.session_state['is_item_tag_session'] = True


def _init_starting_values(keys: List[str], init_value: Any, overwrite: bool=True):
    """Initialize all values in `cols` to `init_value` in session state.

    Only initialize if the value doesn't already exist in session state, unless
    `overwrite` is set to True.

    Parameters
    ----------
    keys : List[str]
        The keys to initialize in session state.
    init_value : Any
        The value to set the session state keys to.
    overwrite : bool
        Whether to overwrite existing values.
    """
    for key in keys:
        if overwrite or key not in st.session_state:
            st.session_state[key] = init_value


def init_session_state(overwrite=True):
    """Initialize session state to starting values.

    Parameters
    ----------
    overwrite : bool
        Whether to overwrite existing values.
    """
    cols_init_false = [
        'is_closet_setup',
        'is_closet_upload',
        'is_finished_upload',
        'is_item_tag_session',
        'is_create_outfits_state',
        'finished_all_uploads',
    ]
    cols_init_zero = ['cat_i', 'item_i', 'i']
    cols_init_null = ['current_tags', 'item', 'outfits_filtered']
    cols_init_empty = ['items', 'items_tags', 'items_filtered']

    _init_starting_values(cols_init_false, False, overwrite=True)
    _init_starting_values(cols_init_zero, 0, overwrite=True)
    _init_starting_values(cols_init_null, None, overwrite=True)

    # setting separately because dicts are mutable
    for col in cols_init_empty:
        st.session_state[col] = {}

    st.session_state['outfits'] = []
