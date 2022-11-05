from typing import Dict, List, Union

_occasion_tags = {
    'Casual': 'ca_',
    'Work': 'wo_',
    'Dinner/Bar': 'bar_',
    'Club/Fancy': 'f_',
}

_season_tags = {
    'Summer': 'su_',
    'Fall': 'fa_',
    'Winter': 'wi_',
    'Spring': 'sp_',
}

_style_tags = {
    'Basic': 'bas_',
    'Statement': 'st_',
}

TAGS = {
    'season': _season_tags,
    'occasion': _occasion_tags,
    'style': _style_tags,
}


def extract_tag_markers(item: str) -> Dict[str, Union[list, str]]:
    """Extract tag markers from `item`.

    Example: extract_tag_markers('black_top_bas_ca_su_sp_') will return
            {
                'style': 'Basic',
                'season': ['Summer', 'Spring'],
                'occasion': ['Casual']
            }

    Parameters
    ----------
    item : str
        The item name.

    Returns
    -------
    Dict[str, Union[list, str]]
    """
    item_tags = {}
    for tag_type in TAGS:
        item_tags[tag_type] = [
            tag for tag, tag_flag in TAGS[tag_type].items() if tag_flag in item
        ]
        if tag_type == 'style':
            # if item tag flag exists in item filename
            if item_tags[tag_type]:
                item_tags[tag_type] = item_tags[tag_type][0]
    return item_tags


def create_items_tags(items: Dict[str, List[str]]):
    """
    Parameters
    ----------
    items : Dict[str, List[str]]
        The key is the category (eg 'tops', 'bottoms', etc) and the values are
        the list of items.

    Returns
    -------
    Dict[str, Dict[str, Union[list, str]]]
    """
    return {
        cat: {
            item: extract_tag_markers(item) for item in items[cat]
        } for cat in items
    }
