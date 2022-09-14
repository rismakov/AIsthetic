import streamlit as st

from closet_creater import Closet
from display_closet import display_outfit_pieces


def _get_next_item_in_scrollthrough(session_state, cat=None):
    item, outfit = None, None
    if cat:
        item = session_state.items_filtered[cat][session_state.i]
    else:
        outfit = session_state.outfits_filtered[session_state.i]
        outfit = {cat: item for cat, item in outfit.items() if cat != 'tags'}
    return item, outfit


def _get_outfits_including_item(outfits, cat, item):
    return [outfit for outfit in outfits if outfit.get(cat, '') == item]


def remove_outfits_including_item(outfits, cat, item):
    st.write(f'This clothing article has been removed from your closet.')

    if cat in ['tops', 'bottoms', 'dresses', 'outerwear']:
        outfits_to_remove = _get_outfits_including_item(outfits, cat, item)
        cnt = len(outfits_to_remove)
        st.write(
            f"{cnt} outfits that include this item have also been removed."
        )
        for outfit in outfits_to_remove:
            Closet().remove_outfit(outfit)


def scroll_through_items(
    session_state, cols, image_placeholder, outfits, i_end, cat=None,
):
    # if `cat` is non-Null, means it is an item, not an outfit
    if cat:
        remove_button_text = 'Remove'
    else:
        remove_button_text = "This doesn't match together."

    item, outfit = _get_next_item_in_scrollthrough(session_state, cat)

    to_remove = cols[0].button(remove_button_text)
    to_continue = cols[1].button('Next')

    if to_continue:
        session_state.i += 1
        item, outfit = _get_next_item_in_scrollthrough(session_state, cat)

    if session_state.i == i_end:
        session_state.scroll_items = False
        session_state.i = 0
    else:
        if cat:
            image_placeholder.image(item, width=450)
        else:
            with image_placeholder:
                display_outfit_pieces(outfit)

    if to_remove:
        if cat:
            remove_outfits_including_item(outfits, cat, item)
            Closet().remove_item(outfit_cat, item)
        else:
            Closet().remove_outfit(outfit)
            st.write("Outfit items have been unmatched.")
        session_state.scroll_items = False
