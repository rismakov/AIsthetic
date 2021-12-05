#  * Copyright 2020 Google LLC
#  *
#  * Licensed under the Apache License, Version 2.0 (the "License");
#  * you may not use this file except in compliance with the License.
#  * You may obtain a copy of the License at
#  *
#  *      http://www.apache.org/licenses/LICENSE-2.0
#  *
#  * Unless required by applicable law or agreed to in writing, software
#  * distributed under the License is distributed on an "AS IS" BASIS,
#  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  * See the License for the specific language governing permissions and
#  * limitations under the License.

 
import os

# from dotenv import load_dotenv
from collections import Counter

from google.cloud import vision

from constants import CLOSET_DIR
from ProductSearch import ProductSearch, ProductCategories

# load_dotenv()


def get_product_type(ps, label):
    """
    Parameters
    ----------
    ps : ProductSearch object
    label : str

    Returns
    -------
    Product object
    """
    try:
        product = ps.createProduct(label, "apparel", labels={"type": label})
        print(f"Created product type: {label}")
    except:
        product = ps.getProduct(label)
        print(f"Got product type: {label}")
    
    return product


def add_images_to_product_type(product, label):
    img_folder = os.path.join(CLOSET_DIR, label) 
    
    for filename in os.listdir(img_folder):
        if filename != '.DS_Store':
            try:
                product.add_reference_image(os.path.join(img_folder, filename))
                print(f"Added image {img_folder}/{filename} to set")
            except:
                print(f"Couldn't add reference image {img_folder}/{filename}")


if __name__ == "__main__":
    print('Initializing Product Search object...')
    ps_obj = ProductSearch(**st.secrets.product_search)

    try:
        product_set = ps_obj.getProductSet(
            st.secrets.product_search['CLOSET_SET']
        )
        print("Got Product Set.")
    except:
        product_set = ps_obj.createProductSet(
            st.secrets.product_search['CLOSET_SET']
        )
        print("Created Product Set.")

    labels = []
    for label in os.listdir(CLOSET_DIR):
        if label not in '.DS_Store':
            labels.append(label)
            product = get_product_type(ps_obj, label)
        
            add_images_to_product_type(product, label)
            product_set.addProduct(product)
            print(f"Added product {product.display_name} to set")

            num_products_added = len(product_set.list_products())
            print(f"Added {num_products_added} products to set")
    print(Counter(labels))
