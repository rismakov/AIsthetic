import random

from category_constants import OCCASION_TAGS, SEASON_TAGS, STYLE_TAGS

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


def filter_basic_items(items):
    return [x for x in items if STYLE_TAGS['Basic'] in x]


def filter_statement_items(items):
    return [x for x in items if STYLE_TAGS['Statement'] in x]


def filter_items_based_on_amount(filepaths: dict, amount: str, occasions: list):
    """Choose only a specific amount of possible items from options.

    Make sure at least one basic item is available for each cateogry type.
    Also, make sure at least one item is available for each occation type.

    Parameters
    ----------
    filepaths : dict
    amount : str
    occasions : list

    Returns
    -------
    dict
    """
    for cat, k in AMOUNT_MAPPINGS[amount].items():
        # Add basic item - so at least one item will match to statement item
        basic_item = random.choice(filter_basic_items(filepaths[cat]))
        # Add as many more items as allowed for amount type
        options = [x for x in filepaths[cat] if x != basic_item]
        subset = [basic_item] + random.choices(options, k=k-1)

        # If basic item was not chosen for all occasion types, add one basic 
        # item to missing occasion type:
        for occasion in occasions:  
            if not any(
                OCCASION_TAGS[occasion] in x for x in filter_basic_items(subset)
            ):
                # Get all basic items of occasion type `occasion`
                options = [
                    x for x in filter_basic_items(filepaths[cat])
                    if OCCASION_TAGS[occasion] in x
                ]
                # If options exist:
                if options:
                    subset += [random.choice(options)]
        filepaths[cat] = subset
    return filepaths


def filter_items(
    filepaths: list, 
    seasons: list=list(SEASON_TAGS.keys()), 
    occasions: list=list(OCCASION_TAGS.keys())
) -> list:
    season_tags = [SEASON_TAGS[season] for season in seasons] 
    occasion_tags = [OCCASION_TAGS[occasion] for occasion in occasions]
    
    return [
        x for x in filepaths if (
            any(tag in x for tag in season_tags)
            and any(tag in x for tag in occasion_tags)
        )
    ]


def filter_items_in_all_categories(
    filepaths: dict, seasons: list, occasions: list
) -> dict:
    return {
        cat: filter_items(filepaths[cat], seasons, occasions) 
        for cat in filepaths
    } 
