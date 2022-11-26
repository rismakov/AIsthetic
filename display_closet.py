import streamlit as st

from utils import increment_i


def display_outfits(outfits: list):
    num_cols = 3
    cols = st.columns(num_cols)
    i = 0
    for outfit in outfits:
        outfit = {cat: item for cat, item in outfit.items() if cat != 'tags'}
        cols[i].image(list(outfit.values()), width=70)
        cols[i].markdown("""---""")

        i = increment_i(i, num_cols - 1)


def display_outfit_pieces(outfit_items: list):
    """Display outfit pieces.

    Parameters
    ----------
    outfit_items : list
    """
    cols = st.columns(6)
    i = 0
    for item in outfit_items:
        cols[i].image(item, width=250)

        i = increment_i(i, 4, increment_by=2)
