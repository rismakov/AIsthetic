import numpy as np
import streamlit as st

from tensorflow.keras.models import load_model

from info_material import categorize_wardrobe_info
from image_processing import image_processing
from utils import get_key_of_value, get_product_search, increment_i

IMAGES_PER_ROW = 10


def _init_category_display():
    placeholders = {}
    cols_info = {}
    col_inds = {}
    for cat in [
        'Tops', 'Bottoms', 'Dresses/Sets', 'Outerwear', 'Shoes', 'Bags', 'Unknown'
    ]:
        st.subheader(cat)
        placeholders[cat] = st.container()
        cols_info[cat] = placeholders[cat].columns(IMAGES_PER_ROW)
        col_inds[cat] = 0

    return cols_info, col_inds


def _get_final_label_from_labels(labels):
    """Get the final label from a list of labels.

    Parameters
    ----------
    labels : list

    Returns
    -------
    str
    """
    category_mapping = {
        'Tops': {'Top', 'Shirt'},
        'Bottoms': {'Skirt', 'Shorts', 'Pants', 'Jeans'},
        'Dresses/Sets': {'Dress'},
        'Outerwear': {'Outerwear', 'Coat'},
        'Shoes': {'Shoe', 'High heels', 'Footwear'},
        'Bags': {'Bag'},
    }

    if len(set(labels)) == 1:
        return get_key_of_value(category_mapping, labels[0])
    if any(label in category_mapping['Outerwear'] for label in labels):
        return 'Outerwear'
    if any(label in category_mapping['Tops'] for label in labels):
        return 'Tops'

    labels = [
        x for x in labels
        if get_key_of_value(category_mapping, x) not in ('Shoes', 'Bags')
    ]
    if len(set(labels)) == 1:
        return get_key_of_value(category_mapping, labels[0])

    print(f"Unknown labels: {labels}")
    return 'Unknown'


def categorize_wardrode(filepaths):
    ps = get_product_search()
    product_set = ps.getProductSet(st.secrets['CLOSET_SET'])

    cols_info, col_inds = _init_category_display()

    all_paths = []
    for cat in filepaths:
        all_paths += filepaths[cat]

    for filepath in all_paths:
        response = product_set.search("apparel", file_path=filepath)
        labels = [x['label'] for x in response]

        label = _get_final_label_from_labels(labels)
        cols_info[label][col_inds[label]].image(filepath)

        # Add one to column indices count
        # Restart column count after it reachs end of row
        col_inds[label] = increment_i(col_inds[label], IMAGES_PER_ROW - 1)


def categorize_wardrobe_style():
    """Categorizes session state `items` as Basic pieces or Statement pieces.

    Based on pre-trained model.
    """
    categorize_wardrobe_info()

    pattern_model = load_model('model.hdf5')

    items = st.session_state['items_filtered']

    images = []
    images_processed = []
    for cat in items:
        for item in items[cat]:
            print('Processing image...')
            images.append(item)
            images_processed.append(image_processing(item))

    X = np.array(images_processed) / 255
    img_rows, img_cols = 100, 100

    X = X.reshape(X.shape[0], img_rows, img_cols, 1)
    with st.spinner('Predicting style of items...'):
        preds = pattern_model.predict(X)

    styles = {}
    for image, pred in zip(images, preds):
        cat_pred = np.argmax(pred)
        if cat_pred == 8:
            cat_pred = 'Basic'
        else:
            cat_pred = 'Statement'

        styles[cat_pred] = styles.get(cat_pred, []) + [image]

    for style in styles:
        st.subheader(f'{style} Pieces')
        st.image(styles[style], width=150)
