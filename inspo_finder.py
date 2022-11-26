import streamlit as st

from display_closet import display_outfit_pieces
from utils import get_product_search

from inspo_match_constants import CATEGORIES, MATCH_GROUPS


def _is_match_in_same_category(inspo_label, closet_label):
    for category in CATEGORIES[closet_label.lower()]:
        if inspo_label.lower() in MATCH_GROUPS[category]:
            return True
    return False


def _get_viable_matches(label, matches):
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
    return [
        match for match in matches if _is_match_in_same_category(
            label, match['product'].labels['type']
        )
    ]


def display_found_match(outfit_items, outfit_match_score):
    st.subheader('Outfit Match')
    st.write(
        "These are the items in your closet that most closely resemble the "
        "above outfit."
    )
    st.write(f'Match Score: {outfit_match_score:.2f}')
    display_outfit_pieces(outfit_items)
    st.button("This doesn't match together.")


def get_outfit_match(items, filepath=None, uri=None, content=None):
    ps = get_product_search()
    product_set = ps.getProductSet(st.secrets['CLOSET_SET'])
    # `response` returns matches for every detected clothing item in image
    response = product_set.search("apparel", file_path=filepath, image_uri=uri, content=content)
    # url_path = 'https://storage.googleapis.com/closet_set/'

    match_scores = []
    outfit_items = []
    for item in response:
        for match in _get_viable_matches(item['label'], item['matches']):
            category = match['product'].labels['type']
            filename = match['image'].split('/')[-1]
            filepath = f"closet/{category}/{filename}"

            # Add if item exists in closet set
            if filepath in items[category]:
                outfit_items.append(filepath)  # match['image'])
                match_scores.append(match['score'])
    
    return outfit_items, match_scores


def get_outfit_match_from_camera_input(
    items, content=None
):
    outfit_items, match_scores = get_outfit_match(items, content=content)
    if match_scores:
        st.write(
            "Before purchasing this item, consider these similar items that "
            "are already in your closet:"
        )
        display_outfit_pieces(outfit_items)

        st.write("""
            Fast fashion makes shopping for clothes more affordable, but it
            comes at an environmental cost. The fashion industry produces 10%
            of ALL humanity's carbon emissions, and accounts for more greenhouse
            gasses than international flights and maritime shipping combined.
        """)
    else:
        st.write("No similar items found in closet.")


def get_outfit_match_from_inspo(items, filepath=None, uri=None):
    outfit_items, match_scores = get_outfit_match(items, filepath, uri)

    if match_scores:
        outfit_match_score = sum(match_scores) * 100 / len(match_scores)
        display_found_match(outfit_items, outfit_match_score)
    else:
        st.subheader('No matches found in closet.')
