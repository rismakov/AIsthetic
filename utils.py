import json
import os
import streamlit as st
from datetime import timedelta

from ProductSearch import ProductSearch
from category_constants import ALL_CATEGORIES

plt.style.use('fivethirtyeight')


def get_filenames_in_dir(dir):
    return [
        f'{dir}/{name}' for name in os.listdir(dir) 
        if os.path.isfile(os.path.join(dir, name)) and name != '.DS_Store'
    ]


def get_all_image_filenames(path) -> dict:
    return {
        cat: get_filenames_in_dir(f'{path}/{cat}')
        for cat in ALL_CATEGORIES
    }


def get_key_of_value(d: dict, v: str) -> str:
    """
    Parameters
    ----------
    d: dict
    v: str or int

    Returns
    -------
    str or int
    """
    for k in d:
        if v in d[k]:
            return k


def increment_i(i: int, max_i: int, increment_by=1) -> int:
    """Add one to `col_i`. If `col_i` is at max, return 0.
    """
    if i == max_i:
        return 0
    return i + increment_by


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)


def get_product_search():
    return ProductSearch(
        st.secrets['GCP_PROJECTID'],
        st.secrets['CREDS'],
        st.secrets['CLOSET_SET'],
        st.secrets['gcp_service_account'],
    )

