######################################################################
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
######################################################################

"""
Product Steps

Steps file for products.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
from behave import given
from compare import expect # Importa expect para las aserciones BDD
from service.models import Category # Importa Category para manejar el Enum

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204

@given('the following products')
def step_impl(context):
    """ Delete all Products and load new ones """
    #
    # List all of the products and delete them one by one
    #
    rest_endpoint = f"{context.base_url}/products"
    context.resp = requests.get(rest_endpoint)
    expect(context.resp.status_code).to_equal(HTTP_200_OK) # Asegura que la solicitud GET fue exitosa

    for product in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{product['id']}")
        expect(context.resp.status_code).to_equal(HTTP_204_NO_CONTENT) # Asegura que la eliminación fue exitosa

    #
    # load the database with new products
    #
    for row in context.table:
        product_data = {
            "name": row['name'],
            "description": row['description'],
            "price": float(row['price']), # Convertir a float para JSON, luego a Decimal en el modelo
            "available": row['available'].lower() == 'true', # Convertir a booleano
            "category": row['category'].upper() # Convertir a mayúsculas para el Enum
        }
        
        # Crear el producto a través de la API REST
        context.resp = requests.post(rest_endpoint, json=product_data)
        expect(context.resp.status_code).to_equal(HTTP_201_CREATED) # Asegura que la creación fue exitosa
        
        # Opcional: Almacenar los productos creados en el contexto para futuras aserciones
        if 'products' not in context:
            context.products = []
        context.products.append(context.resp.json())

