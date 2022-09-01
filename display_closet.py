import streamlit as st

from utils import increment_i


def display_outfits(outfits: list):
    num_cols = 3
    cols = st.columns(num_cols)
    col_i = 0
    for outfit in outfits:
        outfit = {cat: item for cat, item in outfit.items() if cat != 'tags'}
        cols[col_i].image(list(outfit.values()), width=70)
        cols[col_i].markdown("""---""")

        col_i = increment_i(col_i, num_cols - 1)


def display_outfit_pieces(outfit: dict):
    """Display outfit pieces.

    Parameters
    ----------
    outfit : dict
        Dict of outfit pieces, with the category the key and the image filepath
        the value.
    """
    cols = st.columns(6)
    i = 0
    for item in outfit.values():
        cols[i].image(item, width=250)

        i = increment_i(i, 4, increment_by=2)
