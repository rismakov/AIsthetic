import random

from category_constants import TAGS

CARRY_ON = {
    'outerwear': 2,
    'shoes': 2,
}

SUITCASE = {
    'outerwear': 3,
    'shoes': 3,
}

AMOUNT_MAPPINGS = {
    'small carry-on suitcase': CARRY_ON,
    'medium suitcase': SUITCASE,
    'entire closet': {},
}

def is_statement_item(item):
    return TAGS['style']['Statement'] in item


def filter_basic_items(items):
    return [item for item in items if not is_statement_item(item)]


def filter_statement_items(items):
    return [item for item in items if is_statement_item(item)]


def add_to_chosen_basic_items(filepaths, basic_items, cat, occasion, season):
    season_occasion_items = filter_items(
        filepaths[cat], occasions=[occasion], seasons=[season],
    )
    season_occasion_basic_items = filter_basic_items(season_occasion_items)

    if season_occasion_basic_items:
        basic_items += [random.choice(season_occasion_basic_items)]
    
    return basic_items


def filter_items_based_on_amount(
    filepaths: dict, amount: str, occasions: list, seasons:list
):
    """Choose only a specific amount of possible items from options.

    Make sure at least one basic item is available for each cateogry type.
    Also, make sure at least one item is available for each occation type.

    Parameters
    ----------
    filepaths : dict
    amount : str
    occasions : list
    seasons : list

    Returns
    -------
    dict
    """
    for cat, k in AMOUNT_MAPPINGS[amount].items():
        # Add basic item to each season/occasion pair - so at least one item is
        # able to match to everything:
        basic_items = []
        for occasion in occasions:
            for season in seasons:
                # If no basic item included for this season/occasion pair, add 
                # one in:
                if not filter_items(
                    basic_items, occasions=[occasion], seasons=[season],
                ):
                    basic_items = add_to_chosen_basic_items(
                        filepaths, basic_items, cat, occasion, season
                    )

        subset = basic_items 

        # Add as many more items as allowed for amount type:
        options = [x for x in filepaths[cat] if x not in basic_items]
        items_left = max(0, k - len(basic_items))
        if options:
            subset += random.choices(options, k=items_left)

        filepaths[cat] = subset
    return filepaths


def filter_items(
    items: list, 
    seasons: list=list(TAGS['season'].keys()), 
    occasions: list=list(TAGS['occasion'].keys())
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

def filter_appropriate_outfits(outfits, seasons, occasions):
    return [
        outfit for outfit in outfits if (
            any(season in outfit['tags']['season'] for season in seasons)
            and any(occsn in outfit['tags']['occasion'] for occsn in occasions)
        )
    ]

def filter_items_in_all_categories(
    filepaths: dict, seasons: list, occasions: list
) -> dict:
    return {
        cat: filter_items(filepaths[cat], seasons, occasions) 
        for cat in filepaths
    } 
