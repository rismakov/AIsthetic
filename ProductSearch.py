# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import streamlit as st

from google.cloud import storage
from google.cloud import vision
from uuid import uuid4 as uuid

class ProductCategories:
    HOMEGOODS = "homegoods-v2"
    APPAREL = "apparel-v2"
    TOYS = "toys-v2"
    PACKAGEDGOODS = "packagedgoods-v1"
    GENERAL = "general-v1"


class ProductSearch:
    def __init__(
        self, 
        project_id, 
        creds_file, 
        bucket_name,
        gcp_account,
        location="us-west1", 
        storage_prefix=None
    ):
        """Create a new product search object

        Args:
            project_id (string): GCP project id
            creds_file (string): path to GCP credentials file (i.e. "./key.json")
            bucket_name (string): Google Cloud Storage bucket to store product image files
            location (string, optional): where to process data, i.e. "us-west1"
            storage_prefix (string, optional): [description]. Defaults to None.
        """
        self.project_id = project_id
        self.location = location
        self.product_client = (
            vision.ProductSearchClient.from_service_account_json(creds_file)
        )
        self.image_client = (
            vision.ImageAnnotatorClient.from_service_account_file(gcp_account)
        )
        self.location_path = self.product_client.location_path(
            project=project_id, location=location
        )
        self.storage_client = (
            storage.Client.from_service_account_json(gcp_account)
        )
        self.bucket = self.storage_client.bucket(bucket_name)
        self.prefix = storage_prefix

    # Product
    def getProduct(self, product_id):
        product_path = self.product_client.product_path(
            project=self.project_id,
            location=self.location,
            product=product_id,
        )
        res = self.product_client.get_product(name=product_path)
        return ProductSearch.Product._from_response(self, res)


    class Product:
        def __init__(
            self,
            product_search, 
            product_id, 
            category,
            display_name, 
            labels, 
            description='',
        ):
            """Individual product.

            Args:
                product_search (ProductSearch)
                product_id (string): unique id for this product
                category (ProductCategories): category of item (APPAREL, etc)
                display_name (string): name to refer to this product
                labels (dict): key value pairs (i.e. {type: "top"})
                description (string, optional): product description
            """
            self.product_search = product_search
            self.product_id = product_id
            self.category = category
            self.display_name = display_name
            self.labels = labels
            self.description = description
            self.deleted = False

        @staticmethod
        def _from_response(product_search, res):
            """Create a product from the json data returned from the Product 
            Search API.

            Args:
                product_search (ProductSearch): ProductSearch to access API
                res (google.cloud.vision.types.Product): API response to parse

            Returns:
                ProductSearch.Product: Product constructed from res
            """
            # Make sure that product_labels is in dictionary format
            product_labels = {x.key: x.value for x in res.product_labels}
            return ProductSearch.Product(
                product_search,
                res.name.split('/')[-1],
                res.product_category,
                res.display_name,
                product_labels,
                res.name
            )

        def _checkDeleted(self):
            if self.deleted:
                raise Exception(
                    "Cannot perform operation on already deleted product")

        def delete(self):
            """Deletes a product
            """
            self._checkDeleted()
            productPath = self.product_search.product_client.product_path(
                project=self.product_search.project_id,
                location=self.product_search.location,
                product=self.product_id)
            self.product_search.product_client.delete_product(productPath)
            self.deleted = True

        def add_reference_image(self, filename):
            # image_id = str(uuid())
            image_id = filename.split('/')[-1]
            search = self.product_search
            print("Creating blob...")

            blob = search.bucket.blob(
                image_id if not search.prefix else os.path.join(
                    search.prefix, image_id
                )
            )
            print("Uploading from filename...")
            blob.upload_from_filename(filename)
            
            print("Making public...")
            blob.make_public()

            gcs_uri = os.path.join("gs://", search.bucket.name, blob.name)

            # Create a reference image.
            reference_image = vision.types.ReferenceImage(uri=gcs_uri)

            product_path = search.product_client.product_path(
                project=search.project_id,
                location=search.location,
                product=self.product_id
            )

            # The response is the reference image with `name` populated.
            res = search.product_client.create_reference_image(
                parent=product_path,
                reference_image=reference_image,
                reference_image_id=image_id
            )

            return res.name

        def listReferenceImages(self):
            """List references images associated with a product

            Returns:
                list: list of names of reference images
            """
            productPath = self.product_search.product_client.product_path(
                project=self.product_search.project_id,
                location=self.product_search.location,
                product=self.product_id)

            images = self.product_search.product_client.list_reference_images(
                parent=productPath)
            return [x.name for x in images]

        def _getReferenceImageBlobName(self, name):
            refImage = self.product_search.product_client.get_reference_image(
                name)
            return '/'.join(refImage.uri.split("//")[1].split("/")[1:])

        def getReferenceImageUrl(self, name):
            """Gets a public url for a reference image

            Args:
                name (string): reference image name

            Returns:
                string: public url for image
            """
            blobName = self._getReferenceImageBlobName(name)
            return self.product_search.bucket.blob(blobName).public_url

        def deleteReferenceImage(self, name):
            """Deletes a reference image

            Args:
                name (string): name of reference image to delete
            """
            blobName = self._getReferenceImageBlobName(name)
            self.product_search.product_client.delete_reference_image(name=name)
            self.product_search.bucket.blob(blobName).delete()

    def createProduct(
        self, 
        product_id, 
        category, 
        display_name=None, 
        description=None, 
        labels={},
    ):
        """Create a new product

        Args:
            product_id (string): unique id for this product
            category (ProductCategories): RETAIL, HOMEGOODS, etc
            display_name (string, optional): Display name. Defaults to None.
            description (string, optional): Dsecription Defaults to None.
            labels (dict, optional): i.e. {type: "shirt"}. Defaults to {}.

        Returns:
            ProductSearch.Product: Returns newly created product
        """

        display_name = display_name if display_name else product_id

        product_labels = []
        for key in labels:
            product_labels.append(
                vision.types.Product.KeyValue(key=key, value=labels[key]))

        product = vision.types.Product(
            display_name=display_name,
            product_category=category,
            product_labels=product_labels,
            description=description
        )

        res = self.product_client.create_product(
            parent=self.location_path,
            product=product,
            product_id=product_id
        )

        return ProductSearch.Product(
            self, product_id, category, display_name, labels, res.name
        )

    def listProducts(self):
        """Lists products all products.

        Returns:
            list: List of ProductSearch.Product
        """
        response = self.product_client.list_products(parent=self.location_path)
        return [ProductSearch.Product._from_response(self.product_search, x) for x in response]

    # ProductSet

    def _getProductSetPath(self, product_set_id):
        return self.product_client.product_set_path(
            project=self.project_id, location=self.location,
            product_set=product_set_id)

    class ProductSet:
        def __init__(self, product_search, name):
            self.product_search = product_search
            self.product_set_path = product_search._getProductSetPath(name)
            self.name = name
            self.product_set = product_search.product_client.get_product_set(
                name=self.product_set_path
            )
            self.deleted = False

        def _checkDeleted(self):
            if self.deleted:
                raise Exception(
                    "Can't perform operation on already deleted product set")

        def indexTime(self):
            """Get last time this product set was indexed.

            If the index time is earlier than the time you last added
            a product, it will not appear in search results until
            the Product Set re-indexes.

            Returns:
                timestamp: Last index time
            """
            productSet = self.product_search.product_client.get_product_set(
                name=self.product_set_path)
            return productSet.index_time

        def delete(self):
            """Delete this product set
            """
            self._checkDeleted()
            # Delete the product set.
            self.product_search.product_client.delete_product_set(
                name=self.product_set_path
            )
            self.deleted = True

        def addProduct(self, product):
            """Add a product to this product set

            Args:
                product (ProductSearch.Product): product to add
            """
            self._checkDeleted()
            product._checkDeleted()

            product_path = self.product_search.product_client.product_path(
                project=self.product_search.project_id,
                location=self.product_search.location,
                product=product.product_id
            )

            self.product_search.product_client.add_product_to_product_set(
                name=self.product_set_path, product=product_path
            )

        def removeProduct(self, product):
            self._checkDeleted()
            product._checkDeleted()

            productPath = self.product_search.product_client.product_path(
                project=self.product_search.project_id,
                location=self.product_search.location,
                product=product.product_id)

            self.product_search.product_client.remove_product_from_product_set(
                name=self.product_set_path, product=productPath)

        def list_products(self):
            self._checkDeleted()
            response = self.product_search.product_client.list_products_in_product_set(
                name=self.product_set_path)
            return [ProductSearch.Product._from_response(self.product_search, x) for x in response]

        def search(self, product_category, file_path=None, image_uri=None, filter=None):
            self._checkDeleted()
            # This little hack checks that exactly one of file_path or image_uri is set
            if bool(file_path) == bool(image_uri):
                raise Exception(
                    "Must provide one of either a file path or an image uri")

            if file_path:
                with open(file_path, 'rb') as image_file:
                    content = image_file.read()
                image = vision.types.Image(content=content)
            else:
                image_source = vision.types.ImageSource(image_uri=image_uri)
                image = vision.types.Image(source=image_source)

            product_search_params = vision.types.ProductSearchParams(
                product_set=self.product_set_path,
                product_categories=[product_category],
                filter=filter
            )

            image_context = vision.types.ImageContext(
                product_search_params=product_search_params
            )

            # Search products similar to the image.

            # Results are grouped by the item (i.e. multiple clothing in pic, multiple results)
            products_matches = self.product_search.image_client.product_search(
                image, image_context=image_context
            ).product_search_results.product_grouped_results
            responses = []

            for product_matches in products_matches:
                if not product_matches.object_annotations:
                    continue

                # Take the most confident label as the label for this bounding box
                product_label = max(product_matches.object_annotations, key=lambda x: x.score)

                # If we aren't confident in the object we're matching, ignore it
                if product_label.score < 0.5:
                    continue
                response = []
                for match in product_matches.results:
                    response.append({
                        'product': ProductSearch.Product._from_response(self.product_search, match.product),
                        'score': match.score,
                        'image': match.image
                    })
                responses.append({
                    "score": product_label.score,
                    "label": product_label.name,
                    "matches": response,
                    'boundingBox': product_matches.bounding_poly.normalized_vertices
                })
            return responses

    def createProductSet(self, name, display_name=None):
        '''
            If display_name is None, just set it to the product set id
        '''
        display_name = name if not display_name else display_name

        # Create a product set with the product set specification in the region.
        product_set = vision.types.ProductSet(display_name=display_name)

        # The response is the product set with `name` populated.
        self.product_client.create_product_set(
            parent=self.location_path,
            product_set=product_set,
            product_set_id=name
        )

        return ProductSearch.ProductSet(self, name)

    def getProductSet(self, name):
        return ProductSearch.ProductSet(self, name)

    def listProductSets(self):
        res = self.product_client.list_product_sets(parent=self.location_path)
        return [ProductSearch.ProductSet(self, x.name.split('/')[-1]) for x in res]
