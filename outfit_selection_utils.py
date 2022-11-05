import random
from typing import Dict, List

from outfit_utils import (
    filter_appropriate_outfits, filter_items_by_style, filter_category_of_items
)

from category_constants import ACCESSORIES, WEATHER_TO_SEASON_MAPPINGS


def get_all_exclude_items_in_outfit(
    outfit: dict, recently_worn: Dict[str, list], is_user_closet: bool
) -> list:
    """Check if any items from `recently_worn` are in `outfit`.

    Checks for all categories in `outfit` and `recently_worn`. Returns
    categories of items in outfit that were recently worn.

    Parameters
    ----------
    outfit : Dict[str, Union[str, UploadedFile]]
    recently_worn : Dict[str, List[Union[str, UploadedFile]]
        A dictionary of recently worn items, with the item category as the key.
        Should include keys `tops`, `bottoms`, `dresses` and `outerwear`.
    is_user_closet : bool
        Whether `outfit` and `recently_worn` are user-uploaded data or are mock
        data (user-uploaded vs mock data are stored as different data types).

    Returns
    -------
    bool
    """
    recently_worn_cats = []
    for cat, item in outfit.items():
        if cat == 'tags':
            continue

        for exclude_item in recently_worn.get(cat, []):
            if is_user_closet:
                if item.name == exclude_item.name:
                    recently_worn_cats.append(cat)
            else:
                if item == exclude_item:
                    recently_worn_cats.append(cat)
    return recently_worn_cats


def update_recently_worn_threshold(
    recently_worn: Dict[str, list], recently_worn_cats: List[List[str]]
) -> Dict[str, list]:
    """If no available options, update `recently_worn` to be less strict.

    i.e. if 'recently' is defined at last 3 days, change to last 2 days if all
    items were all already worn in las 3 days.
    """
    # get categories that lead to no available options
    not_enough_cats = set.intersection(*map(set, recently_worn_cats))
    for cat in not_enough_cats:
        recently_worn[cat] = recently_worn[cat][:-1]

    return {k: v for k, v in recently_worn.items() if v}


def get_non_recently_worn_options(
    options: List[dict], recently_worn: dict, is_user_closet: bool
):
    """Remove outfits from `options` that include recently-worn items.

    If all options were recently-worn, keep recursively removing a day from
    the recently-worn items (i.e. if 'recently' is defined as 3 days, check
    2 days, then 1 day).
    """
    print('--')
    print(recently_worn)
    print('--')
    filtered_options = []
    recently_worn_cats = []
    for outfit in options:
        cats = get_all_exclude_items_in_outfit(
            outfit, recently_worn, is_user_closet
        )
        # if none of the items were recently worn, include outfit as option
        if not cats:
            filtered_options.append(outfit)
        else:
            recently_worn_cats.append(cats)

    # return all non-recently worn outfit options
    if filtered_options:
        return filtered_options

    # if no non-recently worn options, update definition of 'recent' by 1 day
    recently_worn = update_recently_worn_threshold(
        recently_worn, recently_worn_cats
    )

    return get_non_recently_worn_options(options, recently_worn, is_user_closet)


def get_outfit_options(closet, season, occasion, recently_worn: dict = {}):
    """Get outfit options based on season and occasion.

    Also, filter out options that were recently worn, unless no other options
    exist.
    """
    # Get clothing items that are the proper occasion and season type
    appropriate_outfits = filter_appropriate_outfits(
        closet.outfits, [season], [occasion],
    )

    if not appropriate_outfits:
        return []

    return get_non_recently_worn_options(
        appropriate_outfits, recently_worn, closet.is_user_closet
    )


def choose_outfit(
    closet,
    weather_type: str,
    occasion: str,
    include_accessories: bool = True,
    recently_worn: dict = {},
):
    """
    Parameters
    ----------
    closet : closet_creater.Closet
    weather_type : str
    occasion : str
    include_accessories : bool
    recently_worn : Dict[List[str]]

    Returns
    -------
    dict
    """
    season = WEATHER_TO_SEASON_MAPPINGS[weather_type]

    options = get_outfit_options(closet, season, occasion, recently_worn)

    if not options:
        return {}

    # create deep copy
    choose_from = [{k: v for k, v in option.items()} for option in options]
    random_ind = random.randint(0, len(options) - 1)
    choice = choose_from[random_ind]

    # add shoes and accessories to outfit
    accessories_cats = ['shoes']
    if include_accessories:
        accessories_cats += ACCESSORIES

    nonempty_cats = [cat for cat in accessories_cats if closet.items.get(cat)]
    for cat in nonempty_cats:
        item_options = closet.items[cat]
        item_options = filter_category_of_items(
            item_options,
            closet.items_tags[cat],
            [season],
            [occasion],
            closet.is_user_closet
        )

        if choice['tags']['is_statement']:
            item_options = filter_items_by_style(
                item_options,
                closet.items_tags[cat],
                closet.is_user_closet,
                'Basic'
            )
        if item_options:
            choice[cat] = random.choice(item_options)

    del choice['tags']

    return choice
