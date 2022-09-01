import json
import streamlit as st

from typing import Dict, List, Tuple

from info_material import tagging_session_info
from tagging import display_icon_key

from category_constants import ALL_CATEGORIES, TAGS


def upload_items() -> List[str]:
    uploaded_items = {}
    for cat in ALL_CATEGORIES:
        uploaded_items[cat] = st.file_uploader(
            f'Please select all {cat} items',
            key=cat,
            accept_multiple_files=True,
        ) 
    return uploaded_items


def get_next_cat_i(items, cats, ss):
    """Get the next category index with items available.

    Parameters
    ----------
    items : Dict[str, list]
    cats : List[str]
        The categories in `items`.
    ss : int
        The session state. Used to keep track of `cat_i` increments.

    Returns
    -------
    int
    """
    ss.cat_i += 1

    # return null if `cat_i` is greater than number of categories
    if ss.cat_i == len(cats):
        ss.cat_i = None
        return

    # skip category if it includes no items
    if len(items[cats[ss.cat_i]]) == 0:
        get_next_cat_i(items, cats, ss)

    return ss.cat_i


def select_article_tags() -> Tuple[int, Dict[str, List[str]]]:
    form = st.form('tags')
    style = form.selectbox('Style?', list(TAGS['style'].keys()))
    seasons = form.multiselect('Season?', list(TAGS['season'].keys()))
    occasions = form.multiselect('Occasion?', list(TAGS['occasion'].keys()))

    if form.form_submit_button('Finished Adding Tags'):
        return {
            'style': style,
            'season': seasons,
            'occasion': occasions,
        }


def get_cat_and_item_inds(ss, cats, items):
    cat = cats[ss.cat_i]
    # continue to next non-empty category if end of items in current category
    if ss.item_i == len(items[cat]):
        ss.cat_i = get_next_cat_i(items, cats, ss)
        ss.item_i = 0

    # exit function if finished scrolling through all categories
    if ss.cat_i is None:
        ss.is_item_tag_session = False
        ss.finished_tag_session = True

    return ss


def download_json(label, info_to_save, filename):
    json_string = json.dumps(info_to_save)
    st.download_button(
        label=label, data=json_string, mime="application/json", file_name=filename
    )


def tag_items(ss, items: Dict[str, list]) -> Dict[str, list]:
    """Add tags to items missing tags.

    Returns `items_tags` with tags included where they were previously missing.

    Parameters
    ----------
    ss : session_state
    items : Dict[str, list]

    Returns
    -------
    Dict[str, List[Dict[str, List[str]]]]
        example: {
                'tops': [
                    {'style': [...], 'occasion': [...], 'weather': [...]},
                    ...
                ],
                'bottoms': [{...}, {...}, ...],
                ...
            }
            items_tags[cat] --> item_tags --> item_tag_type_tags
    """
    display_icon_key()

    cats = list(items.keys())

    ss = get_cat_and_item_inds(ss, cats, items)
    if ss.cat_i is None:
        return ss
      
    # create image placeholder and display tagging form
    placeholder = st.container()
    ss.current_tags = select_article_tags()

    # if user submitted tags, append tags to list and increment item index
    if ss.current_tags:
        cat = cats[ss.cat_i]
        ss.items_tags[cat] = ss.items_tags.get(cat, []) + [ss.current_tags]
        ss.item_i += 1

    # need this here again
    ss = get_cat_and_item_inds(ss, cats, items)
    if ss.cat_i is None:
        return ss

    # display header, info and image
    cat = cats[ss.cat_i]
    if not ss.finished_tag_session:
        tagging_session_info(placeholder, cat)

    placeholder.image(items[cat][ss.item_i], width=300)

    return ss
