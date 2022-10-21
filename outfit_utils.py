
import streamlit as st
from typing import Dict, List

from category_constants import OCCASIONS, SEASONS


def is_statement_item(item: str, item_tags) -> bool:
    return item_tags['style'] == 'Statement'


def filter_basic_items(items: List[str], items_tags: dict) -> List[str]:
    return [
        item for item in items if not is_statement_item(item, items_tags[item])
    ]


def filter_statement_items(items: List[str], items_tags: dict) -> List[str]:
    return [
        item for item in items if is_statement_item(item, items_tags[item])
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


def filter_category_of_items(cat_items, cat_items_tags, seasons, occasions, is_user_closet=False):
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
    items: Dict[str, list],
    items_tags: Dict[str, dict],
    seasons: List[str],
    occasions: List[str],
    is_user_closet: bool = False
) -> Dict[str, list]:
    """Filter dictionary of items.

    Parameters
    ----------
    items : Dict[str, list]
        The key is the category (eg 'tops', 'bottoms', etc) and the values are
        the list of items.
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
            items[cat],
            items_tags[cat],
            seasons,
            occasions,
            is_user_closet=is_user_closet
        ) for cat in items if items[cat]  # if nonempty category
    }


def filter_appropriate_outfits(
    outfits: list, seasons: list, occasions: list
) -> list:
    return [
        outfit for outfit in outfits if (
            any(season in outfit['tags']['season'] for season in seasons)
            and any(occsn in outfit['tags']['occasion'] for occsn in occasions)
        )
    ]


def filter_outfits_on_item(outfits, cat, item):
    return [outfit for outfit in outfits if outfit[cat] == item]
