from typing import List

from category_constants import OCCASIONS, SEASONS, TAGS


def is_statement_item(item: str) -> bool:
    return TAGS['style']['Statement'] in item


def filter_basic_items(items: List[str]) -> List[str]:
    return [item for item in items if not is_statement_item(item)]


def filter_statement_items(items: List[str]) -> List[str]:
    return [item for item in items if is_statement_item(item)]


def filter_category_of_items(
    items: list, seasons: list = SEASONS, occasions: list = OCCASIONS
) -> list:
    """Filter list to only include items with specfic tags.

    Items in list must include at least one of the `seasons` tags AND at least
    one of the `occasions` tags.

    Parameters
    ----------
    items : list
    seasons : list
    occasions : list

    Returns
    list
        Returns filepaths that have at least one of the `seasons` tags and one
        of the `occasions` tags.
    """
    season_tags = [TAGS['season'][season] for season in seasons]
    occasion_tags = [TAGS['occasion'][occasion] for occasion in occasions]

    return [
        item for item in items if (
            any(tag in item for tag in season_tags)
            and any(tag in item for tag in occasion_tags)
        )
    ]


def filter_appropriate_outfits(
    outfits: list, seasons: list, occasions: list
) -> list:
    return [
        outfit for outfit in outfits if (
            any(season in outfit['tags']['season'] for season in seasons)
            and any(occsn in outfit['tags']['occasion'] for occsn in occasions)
        )
    ]


def filter_appropriate_items(
    items: dict, seasons: list, occasions: list
) -> dict:
    return {
        cat: filter_category_of_items(items[cat], seasons, occasions)
        for cat in items
    }


def filter_outfits_on_item(outfits, cat, item):
    return [outfit for outfit in outfits if outfit[cat] == item]
