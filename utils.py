import json
import os
import requests
import streamlit as st
from datetime import timedelta

from typing import Dict, List

from ProductSearch import ProductSearch
from category_constants import ALL_CATEGORIES


def get_filenames_in_dir(dir: str) -> List[str]:
    """Get all filenames in directory `dir`.

    Parameters
    ----------
    dir : str
        The directory of filenames.

    Returns
    -------
    List[str]
        The list of filenames in the directory.
    """
    return [
        f'{dir}/{name}' for name in os.listdir(dir)
        if os.path.isfile(os.path.join(dir, name)) and name != '.DS_Store'
    ]


def get_all_image_filenames(dir: str) -> Dict[str, List[str]]:
    """Return all filenames in `path` by category subfolders.

    Parameters
    ----------
    dir : str
        The directory. Should include subfolders of categories.

    Returns
    -------
    Dict[str, List[str]]
        The key is the category and the values are the list of filenames in the
        category subfolder directory.
    """
    return {cat: get_filenames_in_dir(f'{dir}/{cat}') for cat in ALL_CATEGORIES}


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
    """Generate range from `start_date` to `end_date`.

    Parameters
    ----------
    start_date : datetime.datetime
    end_date : datetime.datetime
    """
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)


def check_if_url_valid(url: str):
    """Raise error if `url` is an invalid url.
    """
    try:
        requests.get(url)
        st.sidebar.success("URL is valid and exists on the internet.")
        return True
    except requests.ConnectionError as exception:
        st.sidebar.error("ERROR: URL is not a valid link.")
    except requests.exceptions.MissingSchema:
        st.sidebar.error("ERROR: URL is not a valid link.")


def get_product_search():
    return ProductSearch(
        st.secrets['GCP_PROJECTID'],
        st.secrets['CREDS'],
        st.secrets['CLOSET_SET'],
        st.secrets['gcp_service_account'],
    )

def update_keys(d, mapping):
    return {mapping.get(k, k): v for k, v in d.items()}