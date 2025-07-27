# Copyright 2016, 2022 John J. Rofrano. All Rights Reserved.
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

# spell: ignore Rofrano jsonify restx dbname
"""
Product Store Service with UI
"""
from flask import jsonify, request, abort, url_for
from service.models import Product, Category # Importa Category para los filtros
from service.common import status  # HTTP Status Codes
from . import app
from decimal import Decimal # Importar Decimal para manejar precios


######################################################################
# H E A L T H   C H E C K
######################################################################
@app.route("/health")
def healthcheck():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="OK"), status.HTTP_200_OK


######################################################################
# H O M E   P A G E
######################################################################
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


######################################################################
#   U T I L I T Y   F U N C T I O N S
######################################################################
def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


######################################################################
# C R E A T E   A   N E W   P R O D U C T
######################################################################
@app.route("/products", methods=["POST"])
def create_products():
    """
    Creates a Product
    This endpoint will create a Product based the data in the body that is posted
    """
    app.logger.info("Request to Create a Product...")
    check_content_type("application/json")

    data = request.get_json()
    app.logger.info("Processing: %s", data)
    product = Product()
    product.deserialize(data)
    product.create()
    app.logger.info("Product with new id [%s] saved!", product.id)

    message = product.serialize()

    # Descomenta esta línea de código una vez que se implemente LEER UN PRODUCTO
    location_url = url_for("get_products", product_id=product.id, _external=True)
    # location_url = "/"  # elimina una vez que se implemente LEER
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# L I S T   A L L   P R O D U C T S
######################################################################

@app.route("/products", methods=["GET"])
def list_products():
    """
    Lists all Products or filters by query parameters
    """
    app.logger.info("Request to List Products...")
    
    # Iniciar con todos los productos y aplicar filtros secuencialmente
    products = Product.all()
    
    name = request.args.get("name")
    category = request.args.get("category")
    available = request.args.get("available")
    price = request.args.get("price")

    if name:
        app.logger.info("Find by name: %s", name)
        products = Product.find_by_name(name).all() # Obtiene todos los productos con ese nombre
    
    # Si ya se filtró por nombre, aplicar el siguiente filtro sobre los resultados actuales
    if category:
        app.logger.info("Find by category: %s", category)
        try:
            category_enum = getattr(Category, category.upper())
            # Filtra los productos actuales por categoría
            products = [p for p in products if p.category == category_enum]
        except AttributeError:
            abort(status.HTTP_400_BAD_REQUEST, f"Invalid category: {category}")
    
    if available:
        app.logger.info("Find by available: %s", available)
        available_bool = available.lower() == "true"
        # Filtra los productos actuales por disponibilidad
        products = [p for p in products if p.available == available_bool]
    
    if price:
        app.logger.info("Find by price: %s", price)
        try:
            price_decimal = Decimal(price)
            # Filtra los productos actuales por precio
            products = [p for p in products if p.price == price_decimal]
        except Exception as e:
            abort(status.HTTP_400_BAD_REQUEST, f"Invalid price format: {price} - {str(e)}")

    results = [product.serialize() for product in products]
    app.logger.info("Returning %d products", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# R E A D   A   P R O D U C T
######################################################################

@app.route("/products/<int:product_id>", methods=["GET"])
def get_products(product_id):
    """
    Retrieve a single Product

    This endpoint will return a Product based on it's id
    """
    app.logger.info("Request to Retrieve Product with id [%s]", product_id)
    product = Product.find(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")
    return jsonify(product.serialize()), status.HTTP_200_OK


######################################################################
# U P D A T E   A   P R O D U C T
######################################################################

@app.route("/products/<int:product_id>", methods=["PUT"])
def update_products(product_id):
    """
    Update a Product

    This endpoint will update a Product based on the body that is posted
    """
    app.logger.info("Request to Update Product with id [%s]", product_id)
    check_content_type("application/json")

    product = Product.find(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")

    data = request.get_json()
    app.logger.info("Processing: %s", data)
    product.deserialize(data)
    product.id = product_id # Asegura que el ID no cambie durante la actualización
    product.update()
    app.logger.info("Product with id [%s] updated.", product.id)
    return jsonify(product.serialize()), status.HTTP_200_OK


######################################################################
# D E L E T E   A   P R O D U C T
######################################################################

@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_products(product_id):
    """
    Delete a Product

    This endpoint will delete a Product based on the id specified in the path
    """
    app.logger.info("Request to Delete Product with id [%s]", product_id)
    product = Product.find(product_id)
    if product:
        product.delete()
    app.logger.info("Product with id [%s] deleted.", product_id)
    return "", status.HTTP_204_NO_CONTENT

