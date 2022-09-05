import json
import streamlit as st

from typing import Dict, List, Tuple

from info_material import finished_tagging_info, tagging_session_info
from tagging import display_icon_key

from category_constants import OCCASIONS, SEASONS


def is_end_of_category(cat_items: list, item_i: int) -> bool:
    return item_i == len(cat_items)


def update_cat_and_item_inds(
    cats: List[str], cat_i: int, item_i: int
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
    items = st.session_state['items'][cats[cat_i]]
    if is_end_of_category(items, max(0, item_i)):
        return update_cat_and_item_inds(cats, cat_i + 1, -1)

    return cat_i, item_i + 1


def append_tags(cat: str):
    """Append item tags to full list of items tags.

    Add `current_tags` to session state `items_tags` dict under the item_name
    key.

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


def update_post_item_tag_state(cats):
    """Append item tags to full list and increment category and item indexes.
    """
    cat = cats[st.session_state['cat_i']]
    append_tags(cat)
    cat_i, item_i = st.session_state['cat_i'], st.session_state['item_i']
    st.session_state['cat_i'], st.session_state['item_i'] = (
        update_cat_and_item_inds(cats, cat_i, item_i)
    )


def select_article_tags(cats) -> Tuple[int, Dict[str, List[str]]]:
    form = st.form('tags')
    style = form.selectbox('Style?', ['Basic', 'Statement'])
    seasons = form.multiselect('Season?', SEASONS)
    occasions = form.multiselect('Occasion?', OCCASIONS)

    if form.form_submit_button(
        'Finished Adding Tags',
        on_click=update_post_item_tag_state,
        args=(cats,)
    ):
        return {
            'style': style,
            'season': seasons,
            'occasion': occasions,
        }


def download_json(object_to_download, download_filename: str, button_text: str):
    return st.download_button(
        label=button_text,
        data=json.dumps(object_to_download),
        file_name=download_filename,
        mime="application/json",
    )


def display_download_tags_option():
    st.session_state['is_item_tag_session'] = False
    finished_tagging_info()
    if download_json(
        st.session_state['items_tags'],
        'aisthetic_tags.json',
        'Download Tags'
    ):
        st.session_state['finished_all_uploads'] = True


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
        return

    items = st.session_state['items']
    cats = list(items.keys())

    cat = cats[st.session_state['cat_i']]

    # when the first category is empty, get next non-empty category index
    if is_end_of_category(items[cat], st.session_state['item_i']):
        st.session_state['cat_i'], st.session_state['item_i'] = (
            update_cat_and_item_inds(
                cats,
                st.session_state['cat_i'],
                st.session_state['item_i'],
            )
        )

    # if end of categories, exit function
    if not st.session_state['cat_i']:
        display_download_tags_option()
        return

    st.header('Tag Items')
    display_icon_key()
    cat = cats[st.session_state['cat_i']]

    # display tagging form
    tagging_session_info(cat)
    st.image(items[cat][st.session_state['item_i']], width=300)
    st.session_state['current_tags'] = select_article_tags(cats)
