from match_constants import CATEGORIES, MATCH_GROUPS

def is_match_in_same_category(inspo_label, closet_label):
    for category in CATEGORIES[closet_label.lower()]:
        if inspo_label.lower() in MATCH_GROUPS[category]:
            return True
    return False
        

def get_viable_matches(label, matches):
    """Return only matches that are the same label as the clothing item.

    Parameters
    ----------
    label : str
        The clothing item label.
    matches : list
        The found matches for the clothing item.
    
    Returns
    -------
    list
    """
    print([match['product'].labels['type'] for match in matches])
    return [
        match for match in matches if is_match_in_same_category(
            label, match['product'].labels['type']
        )
    ]


def get_best_match(search_response):
    label = search_response['label']
    matches = search_response['matches']
    viable_matches = [
        match for match in matches if any(
            is_same_match_type(label, match['product'].labels['type'])
        )
    ]
    return max(
        viable_matches, 
        key=lambda x: x['score'] if len(viable_matches) else None
    )