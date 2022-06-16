import json
import os
from datetime import timedelta

from category_constants import ALL_CATEGORIES
from utils_constants import PATH_CLOSET

def load_outfits():
    with open('outfits', 'r') as f:
        return json.load(f)


def get_filenames_in_dir(dir):
    return [
        f'{dir}/{name}' for name in os.listdir(dir) 
        if os.path.isfile(os.path.join(dir, name)) and name != '.DS_Store'
    ]


def get_all_image_filenames() -> dict:
    return {
        cat: get_filenames_in_dir(f'{PATH_CLOSET}/{cat}') 
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


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)
