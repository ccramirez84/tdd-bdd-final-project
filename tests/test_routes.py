# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Product API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from decimal import Decimal
from urllib.parse import quote_plus # Importa quote_plus para codificar URLs
from service import app
from service.common.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_405_METHOD_NOT_ALLOWED, HTTP_409_CONFLICT, HTTP_415_UNSUPPORTED_MEDIA_TYPE
from service.models import db, Product, init_db, Category
from tests.factories import ProductFactory

# Se utiliza un URI de base de datos en memoria para las pruebas
DATABASE_URI = os.getenv(
    "DATABASE_URI", "sqlite:///test.db"
)
BASE_URL = "/products"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductService(TestCase):
    """Product Service Test Cases"""

    @classmethod
    def setUpClass(cls):
        """Runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Use a local SQLite database for testing
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        db.session.query(Product).delete()  # Elimina todos los productos de la base de datos
        db.session.commit()
        self.client = app.test_client()

    def tearDown(self):
        """Runs once after each test"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_products(self, count: int = 1) -> list:
        """Crea un número de productos falsos para las pruebas"""
        products = []
        for _ in range(count):
            product = ProductFactory()
            response = self.client.post(BASE_URL, json=product.serialize())
            self.assertEqual(
                response.status_code,
                HTTP_201_CREATED,
                "Could not create test product",
            )
            new_product = response.get_json()
            product.id = new_product["id"]
            products.append(product)
        return products

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, HTTP_200_OK)
        # Actualizado para coincidir con el contenido actual de index.html
        self.assertIn(b"Product Catalog Administration", response.data)

    def test_health(self):
        """It should be healthy"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data['message'], 'OK')

    # ----------------------------------------------------------
    # TEST CREATE
    # ----------------------------------------------------------
    def test_create_product(self):
        """It should Create a new Product"""
        product = ProductFactory()
        resp = self.client.post(
            BASE_URL, json=product.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, HTTP_201_CREATED)
        # Check the data is correct
        new_product = resp.get_json()
        self.assertIsNotNone(new_product["id"])
        self.assertEqual(new_product["name"], product.name)
        self.assertEqual(new_product["description"], product.description)
        self.assertEqual(Decimal(new_product["price"]), product.price)
        self.assertEqual(new_product["available"], product.available)
        self.assertEqual(new_product["category"], product.category.name)

    def test_create_product_no_content_type(self):
        """It should not Create a Product with no Content-Type"""
        # Se necesita importar json para dumps
        import json
        product = ProductFactory()
        # Envía datos como cadena JSON sin Content-Type
        resp = self.client.post(BASE_URL, data=json.dumps(product.serialize()))
        self.assertEqual(resp.status_code, HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_product_bad_content_type(self):
        """It should not Create a Product with bad Content-Type"""
        product = ProductFactory()
        resp = self.client.post(
            BASE_URL, json=product.serialize(), content_type="text/html"
        )
        self.assertEqual(resp.status_code, HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_product_bad_available(self):
        """It should not Create a Product with a bad available attribute"""
        test_product = ProductFactory()
        data = test_product.serialize()
        data["available"] = "true"  # available no es un booleano
        resp = self.client.post(
            BASE_URL, json=data, content_type="application/json"
        )
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)

    def test_create_product_bad_category(self):
        """It should not Create a Product with a bad category attribute"""
        test_product = ProductFactory()
        data = test_product.serialize()
        data["category"] = "UNKNOWN_CATEGORY"  # categoría no válida
        resp = self.client.post(
            BASE_URL, json=data, content_type="application/json"
        )
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)

    def test_get_product(self):
        """It should Get a single Product"""
        # Crea un producto de prueba
        test_product = self._create_products(1)[0]
        # Realiza una solicitud GET al endpoint del producto
        response = self.client.get(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, HTTP_200_OK)
        data = response.get_json()
        # Afirma que los datos recuperados coinciden con el producto de prueba
        self.assertEqual(data["name"], test_product.name)
        self.assertEqual(data["description"], test_product.description)
        self.assertEqual(Decimal(data["price"]), test_product.price)
        self.assertEqual(data["available"], test_product.available)
        self.assertEqual(data["category"], test_product.category.name)

    def test_get_product_not_found(self):
        """It should not Get a Product that does not exist"""
        # Realiza una solicitud GET con un ID que no existe (0)
        response = self.client.get(f"{BASE_URL}/0")
        # Asegura que el código de retorno sea HTTP_404_NOT_FOUND
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_update_product(self):
        """It should Update an existing Product"""
        # Crea un producto para actualizar
        test_product = self._create_products(1)[0]
        # Actualiza algunos de sus atributos
        new_description = "Updated description for the test product"
        new_price = Decimal('123.45')
        test_product.description = new_description
        test_product.price = new_price
        test_product.available = False

        # Realiza una solicitud PUT al endpoint del producto
        response = self.client.put(
            f"{BASE_URL}/{test_product.id}",
            json=test_product.serialize(),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, HTTP_200_OK)
        data = response.get_json()

        # Afirma que los datos actualizados coinciden
        self.assertEqual(data["description"], new_description)
        self.assertEqual(Decimal(data["price"]), new_price)
        self.assertEqual(data["available"], False)

        # Verifica que el producto en la base de datos también se actualizó
        fetched_product = Product.find(test_product.id)
        self.assertEqual(fetched_product.description, new_description)
        self.assertEqual(fetched_product.price, new_price)
        self.assertEqual(fetched_product.available, False)


    def test_update_product_not_found(self):
        """It should not Update a Product that does not exist"""
        product = ProductFactory()
        response = self.client.put(f"{BASE_URL}/0", json=product.serialize(), content_type="application/json") # ID que no existe
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_update_product_no_content_type(self):
        """It should not Update a Product with no Content-Type"""
        import json # Se necesita importar json para dumps
        test_product = self._create_products(1)[0]
        # Envía datos como cadena JSON sin Content-Type
        resp = self.client.put(f"{BASE_URL}/{test_product.id}", data=json.dumps(test_product.serialize()))
        self.assertEqual(resp.status_code, HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_product_bad_content_type(self):
        """It should not Update a Product with bad Content-Type"""
        test_product = self._create_products(1)[0]
        resp = self.client.put(
            f"{BASE_URL}/{test_product.id}", json=test_product.serialize(), content_type="text/html"
        )
        self.assertEqual(resp.status_code, HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_delete_product(self):
        """It should Delete a Product"""
        # Crea un producto para eliminar
        test_product = self._create_products(1)[0]
        # Envía una solicitud DELETE al endpoint del producto
        response = self.client.delete(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0) # No content

        # Afirma que el producto ya no existe
        response = self.client.get(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_delete_product_not_found(self):
        """It should not Delete a Product that does not exist"""
        response = self.client.delete(f"{BASE_URL}/0") # ID que no existe
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT) # DELETE is idempotent, so 204 is expected even if not found

    def test_list_all_products(self):
        """It should Get a list of Products"""
        # Crea 5 productos de prueba
        self._create_products(5)
        # Realiza una solicitud GET al endpoint base
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, HTTP_200_OK)
        data = response.get_json()
        # Afirma que se devuelven 5 productos
        self.assertEqual(len(data), 5)

    def test_list_products_by_name(self):
        """It should List Products by Name"""
        # Crea productos con nombres específicos para la prueba
        ProductFactory(name="TestNameProduct").create()
        ProductFactory(name="AnotherTestNameProduct").create()
        ProductFactory(name="TestNameProduct").create() # Otro con el mismo nombre

        # Realiza una solicitud GET con el filtro de nombre
        response = self.client.get(BASE_URL, query_string={"name": "TestNameProduct"})
        self.assertEqual(response.status_code, HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 2)
        for product in data:
            self.assertEqual(product["name"], "TestNameProduct")

    def test_list_products_by_category(self):
        """It should List Products by Category"""
        ProductFactory(category=Category.CLOTHS).create()
        ProductFactory(category=Category.FOOD).create()
        ProductFactory(category=Category.CLOTHS).create()
        ProductFactory(category=Category.TOOLS).create()

        response = self.client.get(BASE_URL, query_string={"category": Category.CLOTHS.name})
        self.assertEqual(response.status_code, HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 2)
        for product in data:
            self.assertEqual(product["category"], Category.CLOTHS.name)

    def test_list_products_by_availability(self):
        """It should List Products by Availability"""
        ProductFactory(available=True).create()
        ProductFactory(available=False).create()
        ProductFactory(available=True).create()

        response = self.client.get(BASE_URL, query_string={"available": "true"})
        self.assertEqual(response.status_code, HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 2)
        for product in data:
            self.assertTrue(product["available"])

        response = self.client.get(BASE_URL, query_string={"available": "false"})
        self.assertEqual(response.status_code, HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        for product in data:
            self.assertFalse(product["available"])

    def test_list_products_by_price(self):
        """It should List Products by Price"""
        ProductFactory(price=Decimal('10.00')).create()
        ProductFactory(price=Decimal('25.50')).create()
        ProductFactory(price=Decimal('10.00')).create()

        response = self.client.get(BASE_URL, query_string={"price": "10.00"})
        self.assertEqual(response.status_code, HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 2)
        for product in data:
            self.assertEqual(Decimal(product["price"]), Decimal('10.00'))

    def test_list_products_by_multiple_filters(self):
        """It should List Products by multiple filters (name and category)"""
        ProductFactory(name="Shirt", category=Category.CLOTHS).create()
        ProductFactory(name="Pants", category=Category.CLOTHS).create()
        ProductFactory(name="Shirt", category=Category.FOOD).create() # This one should not match

        response = self.client.get(BASE_URL, query_string={"name": "Shirt", "category": Category.CLOTHS.name})
        self.assertEqual(response.status_code, HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Shirt")
        self.assertEqual(data[0]["category"], Category.CLOTHS.name)

    def test_method_not_allowed(self):
        """It should not allow an unsupported method call"""
        response = self.client.put(BASE_URL, json={})
        self.assertEqual(response.status_code, HTTP_405_METHOD_NOT_ALLOWED)

