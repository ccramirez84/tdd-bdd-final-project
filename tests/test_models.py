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
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError # Importa DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#   P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Casos de Prueba para el Modelo de Producto"""

    @classmethod
    def setUpClass(cls):
        """Se ejecuta una vez antes de toda la suite de pruebas"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Se ejecuta una vez después de toda la suite de pruebas"""
        db.session.close()

    def setUp(self):
        """Se ejecuta antes de cada prueba"""
        db.session.query(Product).delete()  # Limpia las pruebas anteriores
        db.session.commit()

    def tearDown(self):
        """Se ejecuta después de cada prueba"""
        db.session.remove()

    ######################################################################
    #   C A S O S   D E   P R U E B A
    ######################################################################

    def test_create_a_product(self):
        """Debe crear un producto y afirmar que existe"""
        product = Product(name="Fedora", description="Un sombrero rojo", price=Decimal('12.50'), available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "Un sombrero rojo")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, Decimal('12.50')) # Asegúrate de comparar con Decimal
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """Debe crear un producto y añadirlo a la base de datos"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None # Asegura que el id sea None antes de la creación para auto-incremento
        product.create()
        # Afirma que se le asignó un ID y aparece en la base de datos
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Verifica que coincide con el producto original
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(new_product.price, product.price) # Compara Decimal directamente
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    ######################################################################
    #   A Ñ A D E   T U S   C A S O S   D E   P R U E B A   A Q U Í
    ######################################################################

    def test_read_a_product(self):
        """Debe leer un Producto por ID"""
        product = ProductFactory()
        product.create()
        self.assertIsNotNone(product.id)

        # Busca el producto en la base de datos
        found_product = Product.find(product.id)
        self.assertIsNotNone(found_product)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)
        self.assertEqual(found_product.available, product.available)
        self.assertEqual(found_product.category, product.category)

    def test_product_not_found(self):
        """No debe devolver un Producto si no se encuentra el ID"""
        self.assertIsNone(Product.find(0)) # Asumiendo que 0 es un ID inválido o inexistente

    def test_update_a_product(self):
        """Debe actualizar un Producto existente"""
        product = ProductFactory()
        product.create()
        self.assertIsNotNone(product.id)

        # Actualiza el nombre y la descripción del producto
        original_id = product.id
        product.name = "Nombre Actualizado"
        product.description = "Descripción actualizada para el producto"
        product.available = False
        product.price = Decimal('99.99')
        product.category = Category.AUTOMOTIVE
        product.update()

        # Busca el producto actualizado y afirma los cambios
        fetched_product = Product.find(original_id)
        self.assertEqual(fetched_product.id, original_id)
        self.assertEqual(fetched_product.name, "Nombre Actualizado")
        self.assertEqual(fetched_product.description, "Descripción actualizada para el producto")
        self.assertEqual(fetched_product.available, False)
        self.assertEqual(fetched_product.price, Decimal('99.99'))
        self.assertEqual(fetched_product.category, Category.AUTOMOTIVE)

    def test_update_no_id(self):
        """No debe actualizar un Producto sin ID"""
        product = ProductFactory()
        product.id = None # Asegura que no haya ID establecido
        # Espera una DataValidationError al intentar actualizar sin un ID
        self.assertRaises(DataValidationError, product.update)

    def test_delete_a_product(self):
        """Debe eliminar un Producto"""
        product = ProductFactory()
        product.create()
        self.assertEqual(len(Product.all()), 1)

        # Elimina el producto
        product.delete()
        self.assertEqual(len(Product.all()), 0)
        self.assertIsNone(Product.find(product.id))

    def test_list_all_products(self):
        """Debe listar todos los Productos en la base de datos"""
        products = Product.all()
        self.assertEqual(products, [])

        # Crea 5 productos
        for _ in range(5):
            product = ProductFactory()
            product.create()

        # Afirma que hay 5 productos en la base de datos
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_by_name(self):
        """Debe encontrar un Producto por Nombre"""
        # Crea productos con varios nombres
        ProductFactory(name="Laptop").create()
        ProductFactory(name="Teclado").create()
        ProductFactory(name="Laptop").create() # Otra laptop

        products = Product.find_by_name("Laptop")
        self.assertEqual(len(products.all()), 2) # Usa .all() para ejecutar la consulta
        for product in products:
            self.assertEqual(product.name, "Laptop")

    def test_find_by_category(self):
        """Debe encontrar Productos por Categoría"""
        ProductFactory(category=Category.CLOTHS).create()
        ProductFactory(category=Category.FOOD).create()
        ProductFactory(category=Category.CLOTHS).create()
        ProductFactory(category=Category.TOOLS).create()

        products = Product.find_by_category(Category.CLOTHS)
        self.assertEqual(len(products.all()), 2)
        for product in products:
            self.assertEqual(product.category, Category.CLOTHS)

    def test_find_by_availability(self):
        """Debe encontrar Productos por Disponibilidad"""
        ProductFactory(available=True).create()
        ProductFactory(available=False).create()
        ProductFactory(available=True).create()

        available_products = Product.find_by_availability(True)
        self.assertEqual(len(available_products.all()), 2)
        for product in available_products:
            self.assertTrue(product.available)

        unavailable_products = Product.find_by_availability(False)
        self.assertEqual(len(unavailable_products.all()), 1)
        for product in unavailable_products:
            self.assertFalse(product.available)

    def test_find_by_price(self):
        """Debe encontrar Productos por Precio"""
        ProductFactory(price=Decimal('10.00')).create()
        ProductFactory(price=Decimal('25.50')).create()
        ProductFactory(price=Decimal('10.00')).create()
        ProductFactory(price=Decimal('50.00')).create()

        products_at_10 = Product.find_by_price(Decimal('10.00'))
        self.assertEqual(len(products_at_10.all()), 2)
        for product in products_at_10:
            self.assertEqual(product.price, Decimal('10.00'))

        products_at_25_50 = Product.find_by_price(Decimal('25.50'))
        self.assertEqual(len(products_at_25_50.all()), 1)
        for product in products_at_25_50:
            self.assertEqual(product.price, Decimal('25.50'))

    def test_find_by_price_with_string(self):
        """Debe encontrar Productos por Precio cuando se pasa como string"""
        ProductFactory(price=Decimal('15.75')).create()
        ProductFactory(price=Decimal('30.00')).create()
        ProductFactory(price=Decimal('15.75')).create()

        products_at_15_75 = Product.find_by_price("15.75") # Pasa el precio como string
        self.assertEqual(len(products_at_15_75.all()), 2)
        for product in products_at_15_75:
            self.assertEqual(product.price, Decimal('15.75'))

    def test_deserialize_missing_data(self):
        """Debe levantar un DataValidationError si faltan datos al deserializar"""
        product = Product()
        # Intenta deserializar un diccionario sin la clave 'name'
        self.assertRaisesRegex(DataValidationError, "missing name", product.deserialize, {})

        # Intenta deserializar un diccionario sin la clave 'description'
        data = {"name": "Test Product"}
        self.assertRaisesRegex(DataValidationError, "missing description", product.deserialize, data)

        # Intenta deserializar un diccionario sin la clave 'price'
        data = {"name": "Test Product", "description": "Some description"}
        self.assertRaisesRegex(DataValidationError, "missing price", product.deserialize, data)

        # Intenta deserializar un diccionario sin la clave 'available'
        data = {"name": "Test Product", "description": "Some description", "price": "10.00"}
        self.assertRaisesRegex(DataValidationError, "missing available", product.deserialize, data)

        # Intenta deserializar un diccionario sin la clave 'category'
        data = {"name": "Test Product", "description": "Some description", "price": "10.00", "available": True}
        self.assertRaisesRegex(DataValidationError, "missing category", product.deserialize, data)

    def test_deserialize_invalid_category(self):
        """Debe levantar un DataValidationError si la categoría es inválida al deserializar"""
        product = Product()
        data = ProductFactory().serialize() # Obtiene datos válidos de un producto
        data["category"] = "INVALID_CATEGORY" # Cambia la categoría a una inválida
        self.assertRaisesRegex(DataValidationError, "Invalid attribute: 'INVALID_CATEGORY'", product.deserialize, data)

    def test_deserialize_invalid_available_type(self):
        """Debe levantar un DataValidationError si el tipo de 'available' es inválido al deserializar"""
        product = Product()
        data = ProductFactory().serialize() # Obtiene datos válidos de un producto
        data["available"] = "True" # Cambia 'available' a un string en lugar de booleano
        self.assertRaisesRegex(DataValidationError, "Invalid type for boolean", product.deserialize, data)

    def test_deserialize_bad_data(self):
        """Debe levantar un DataValidationError si los datos son incorrectos o faltan"""
        product = Product()
        # Prueba con datos que no son un diccionario
        self.assertRaisesRegex(DataValidationError, "body of request contained bad or no data", product.deserialize, None)
        self.assertRaisesRegex(DataValidationError, "body of request contained bad or no data", product.deserialize, "not a dict")
        self.assertRaisesRegex(DataValidationError, "body of request contained bad or no data", product.deserialize, 123)

