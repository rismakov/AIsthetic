import json
import streamlit as st

from streamlit.uploaded_file_manager import UploadedFile
from typing import Dict, List, Tuple

from info_material import finished_tagging_info, tagging_session_info
from tagging import display_icon_key

from category_constants import OCCASIONS, SEASONS


def is_end_of_category(cat_items: list, item_i: int) -> bool:
    """Check if `item_i` is greater or equal than length of items.

    Parameters
    ----------
    cat_items : list
    item_i : int

    Returns
    -------
    bool
    """
    return item_i >= len(cat_items)


def get_next_cat_and_item_inds(
    items, cats: List[str], cat_i: int, item_i: int
) -> Tuple[int, int]:
    """Update `cat_i` and `item_i`.

    Increment `item_i` by one. Unless end of category list, then reinitialize
    `item_i` to 0 and increment `cat_i` by one.

    If end of list and no more non-empty categories, return None. Update state
    to 'is_item_tag_session' = False.

    Parameters
    ----------
    cats : List[str]
        List of all categories.
    cat_i : int
        The category index.
    item_i : int
        The item index.

    Returns
    -------
    Tuple[int, int]
        The updated `cat_i` and `item_i`.
    """
    if cat_i == len(cats):
        return None, None

    # if end of category list, increment `cat_i` and re-initialize `item_i`
    # if -1 passed in for `item_i` (indicating new category), pass in 0 instead
    if is_end_of_category(items[cats[cat_i]], item_i + 1):
        return get_next_cat_and_item_inds(items, cats, cat_i + 1, -1)

    return cat_i, item_i + 1


def append_tags(cat: str):
    """Append item tags to full list of items tags.

    Add `current_tags` to session state `items_tags` dict under the item_name
    key.

    Uses session states.

    Parameters
    ----------
    cats : List[str]
        The category to append to.
    """
    items = st.session_state['items']
    item_name = items[cat][st.session_state['item_i']].name
    st.session_state['items_tags'][cat] = {
        **st.session_state['items_tags'].get(cat, {}),
        **{item_name: st.session_state['current_tags']}
    }


def update_post_item_tag_state(cats, style, seasons, occasions):
    """Append item tags to full list and increment category and item indexes.

    Uses session states.
    """
    if style and seasons and occasions:
        cat = cats[st.session_state['cat_i']]
        append_tags(cat)
        cat_i, item_i = st.session_state['cat_i'], st.session_state['item_i']
        st.session_state['cat_i'], st.session_state['item_i'] = (
            get_next_cat_and_item_inds(
                st.session_state['items'], cats, cat_i, item_i
            )
        )


def is_item_untagged(items_tags: Dict[str, dict], cat: str, item: UploadedFile):
    return not items_tags.get(cat, {}).get(item.name)


def get_inds_to_tag(
    items: Dict[str, list],
    items_tags: Dict[str, dict],
    cats: List[str],
    cat_i: int,
    item_i: int
) -> Tuple[int, int]:
    """Return `cat_i` and `item_i` if no associated tag with item.

    Else, increment inds by one (either `item_i` or if end of category,
    `cat_i` with reinitialization of `item_i`).

    Repeat recursively until reach an untagged item.

    Parameters
    ----------
    items : Dict[str, list]
    items_tags : Dict[str, dict]
    cats : List[str]
    cat_i : int
    item_i : int

    Returns
    -------
    Tuple[int, int]
    """
    if cat_i is None:
        return None, None

    if not is_end_of_category(items[cats[cat_i]], item_i):
        if is_item_untagged(items_tags, cats[cat_i], items[cats[cat_i]][item_i]):
            return cat_i, item_i

    cat_i, item_i = get_next_cat_and_item_inds(items, cats, cat_i, item_i)
    return get_inds_to_tag(items, items_tags, cats, cat_i, item_i)


def select_article_tags(cats) -> Tuple[int, Dict[str, List[str]]]:
    """Display tag form and update state on click.
    """
    form = st.form('tags')
    style = form.selectbox('Style?', ['Basic', 'Statement'])
    seasons = form.multiselect('Season?', SEASONS)
    occasions = form.multiselect('Occasion?', OCCASIONS)

    # where to print any error messages
    # placeholder = st.container()

    st.session_state['current_tags'] = {
        'style': style, 'season': seasons, 'occasion': occasions,
    }
    if form.form_submit_button('Finished Adding Tags'):
        update_post_item_tag_state(cats, style, seasons, occasions)


def update_post_tagging_state():
    st.session_state['finished_all_uploads'] = True


def download_json(object_to_download, download_filename: str, button_text: str):
    return st.download_button(
        label=button_text,
        data=json.dumps(object_to_download),
        file_name=download_filename,
        mime="application/json",
        on_click=update_post_tagging_state,
    )


def display_download_tags_option():
    """Display the 'download tags' button.

    Updates the session state from `is_item_tag_session` to
    `is_create_outfits_state`.
    """
    st.session_state['is_item_tag_session'] = False
    st.session_state['is_create_outfits_state'] = True
    finished_tagging_info()
    download_json(
        st.session_state['items_tags'],
        'aisthetic_tags.json',
        'Download Tags'
    )


def tag_items():
    """Add tags to items missing tags.

    Updates `items_tags` with tags included where they were previously missing.

    `item_tags` =
    Dict[str, List[Dict[str, List[str]]]]
        example: {
                'tops': [
                    {'style': [...], 'occasion': [...], 'weather': [...]},
                    ...
                ],
                'bottoms': [{...}, {...}, ...],
                ...
            }
            items_tags[cat][item] --> item_tags --> item_tag_type_tags
    """
    # if finished tagging all categories
    if st.session_state['cat_i'] is None:
        st.session_state['is_create_outfits_state'] = True
        return

    items = st.session_state['items']
    cats = list(items.keys())

    # if tag already exists, skip to next non-existing item
    # skip if category is empty to next category
    # if end of categories, return None
    st.session_state['cat_i'], st.session_state['item_i'] = get_inds_to_tag(
        st.session_state['items'],
        st.session_state['items_tags'],
        cats, st.session_state['cat_i'], st.session_state['item_i']
    )

    # if category is empty, get next non-empty category index
    # if is_end_of_category(items[cat], st.session_state['item_i']):
    #    st.session_state['cat_i'], st.session_state['item_i'] = (
    #        get_next_cat_and_item_inds(
    #            st.session_state['items'], cats, cat_i, st.session_state['item_i'],
    #        )
    #    )

    # if end of categories, exit function
    if st.session_state['cat_i'] is None:
        display_download_tags_option()
        st.session_state['is_create_outfits_state'] = True
        return

    st.header('Tag Items')
    display_icon_key()
    cat = cats[st.session_state['cat_i']]

    # display tagging form
    tagging_session_info(cat)
    image_placeholder = st.container()
    select_article_tags(cats)

    # if not end of items
    if not st.session_state['item_i'] is None:
        image_placeholder.image(items[cat][st.session_state['item_i']], width=300)

