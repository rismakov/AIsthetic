
import streamlit as st
from typing import Dict, List, Union

from streamlit.uploaded_file_manager import UploadedFile  # for typing

from category_constants import OCCASIONS, SEASONS


def get_item_name(item: Union[str, UploadedFile], is_user_closet: bool):
    """Get item name depending on whether item is user-uploaded or mock data.

    User-uploaded items are of type `streamlit.UploadedFile`, whereas mock data
    items are of type `str`.

    item : Union[]
    """
    if is_user_closet:
        return item.name
    return item


def is_item_of_type_style(item_tags: Dict[str, List[str]], style: str) -> bool:
    """

    Parameters
    ----------
    item_tags : Dict[str, List[str]]
        Tags of a particular item. For example: {
            'season': ['Summer', 'Spring',
            'occasion': 'Casual'],
            'style': 'Basic',
        }
    style: str
        The style, either 'Basic' or 'Statment'.

    Returns
    -------
    bool
    """
    return style in item_tags['style']


def filter_items_by_style(
    cat_items: list, cat_item_tags, is_user_closet, style: str
) -> List[str]:
    """Filter statement items or basic items.

    Parameters
    ----------
    cat_items : list
        List of items of specific category.
    cat_item_tags:
        List of item tags of specific category
    style : str
        The style to filter on (either 'Basic' or 'Statement.)
    """
    return [
        item for item in cat_items if is_item_of_type_style(
            cat_item_tags[get_item_name(item, is_user_closet)], style)
    ]


def are_tags_in_item(item_tags, seasons, occasions) -> bool:
    """Check if any seasons AND any occasions tags are linked to `item`.

    Items in list must include at least one of the `seasons` tags AND at least
    one of the `occasions` tags.
    """
    return (
        any(season in item_tags['season'] for season in seasons)
        and any(occasion in item_tags['occasion'] for occasion in occasions)
    )


def filter_category_of_items(
    cat_items: list,
    cat_items_tags: list,
    seasons: List[str],
    occasions: List[str],
    is_user_closet: bool = False
):
    filtered_items = []
    for item in cat_items:
        if is_user_closet:
            item_name = item.name
        else:
            item_name = item

        if are_tags_in_item(cat_items_tags[item_name], seasons, occasions):
            filtered_items.append(item)
    return filtered_items


def filter_appropriate_items(
    closet,
    seasons: List[str],
    occasions: List[str],
) -> Dict[str, list]:
    """Filter dictionary of items.

    Parameters
    ----------
    closet : create_closet.Closet()
        The closet, including `items` and `items_tags`.
    seasons : List[str]
        The list of seasons we want to filter on.
    occasions : List[str]
        The list of occasion we want to filter on.

    Returns
    -------
    Dict[str, list]
        The items filtered on those with any of the season tags AND any of the
        occasion tags.
    """
    return {
        cat: filter_category_of_items(
            closet.items[cat],
            closet.items_tags[cat],
            seasons,
            occasions,
            is_user_closet=closet.is_user_closet
        ) for cat in closet.items if closet.items[cat]  # if nonempty category
    }


def filter_appropriate_outfits(
    outfits: List[dict], seasons: List[str], occasions: List[str]
) -> list:
    """Filter `outfits` by those with tags from `seasons` and `occasions`.

    Parameters
    ----------
    outfits : List[dict]
        List of outfits. Should include a `tags` key for each outfit.
    seasons : List[str]
        List of seasons ('Summer', 'Winter', 'Fall', 'Spring').
    occasions : List[str]
        List of occasions.

    Returns
    -------
    List[dict]
    """
    return [
        outfit for outfit in outfits if (
            any(season in outfit['tags']['season'] for season in seasons)
            and any(occsn in outfit['tags']['occasion'] for occsn in occasions)
        )
    ]


def filter_outfits_on_item(outfits, cat, item):
    return [outfit for outfit in outfits if outfit[cat] == item]
