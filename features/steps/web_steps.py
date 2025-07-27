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

# pylint: disable=function-redefined, missing-function-docstring, too-many-statements
# flake8: noqa
"""
Web Steps

Steps file for web interactions with Selenium

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import logging
from behave import when, then, given # Añadir 'given'
from compare import expect # Añadir 'expect' para aserciones BDD
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC # Cambiar a EC para consistencia
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import WebDriverException # Añadir para manejo de excepciones
import time # Para usar time.sleep si es necesario para esperas explícitas

# Configuración del log
LOGGER = logging.getLogger('flask.app')

ID_PREFIX = 'product_'


@when('I visit the "Home Page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.base_url)
    # Esperar a que la página cargue completamente y un elemento clave esté presente
    WebDriverWait(context.driver, context.wait_seconds).until(
        EC.presence_of_element_located((By.ID, ID_PREFIX + "id"))
    )
    # Uncomment next line to take a screenshot of the web page
    # context.driver.save_screenshot('home_page.png')

@then('I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    expect(context.driver.title).to_contain(message) # Usar expect para consistencia

@then('I should not see "{text_string}"')
def step_impl(context, text_string):
    element = context.driver.find_element(By.TAG_NAME, 'body')
    expect(element.text).to_not_contain(text_string) # Usar expect para consistencia

@when('I set the "{element_name}" to "{text_value}"') # Cambiado text_string a text_value
def step_impl(context, element_name, text_value): # Cambiado text_string a text_value
    """ Establece el valor de un campo de texto """
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_value)

@when('I select "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    """ Selecciona un valor en un desplegable """
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.presence_of_element_located((By.ID, element_id))
    )
    select_element = Select(element)
    select_element.select_by_visible_text(text)

@then('I should see "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    """ Verifica que un desplegable tiene un valor seleccionado """
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.presence_of_element_located((By.ID, element_id))
    )
    select_element = Select(element)
    expect(select_element.first_selected_option.text).to_equal(text) # Usar expect para consistencia

@then('the "{element_name}" field should be empty')
def step_impl(context, element_name):
    """ Verifica que un campo de texto está vacío """
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.presence_of_element_located((By.ID, element_id))
    )
    expect(element.get_attribute('value')).to_equal('') # Usar expect para consistencia

##################################################################
# These two function simulate copy and paste
##################################################################
@when('I copy the "{element_name}" field')
def step_impl(context, element_name):
    """ Copia el valor de un campo al portapapeles (context) """
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute('value')
    LOGGER.info('Clipboard contains: %s', context.clipboard)

@when('I paste the "{element_name}" field')
def step_impl(context, element_name):
    """ Pega el valor del portapapeles (context) a un campo """
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)

##################################################################
# This code works because of the following naming convention:
# The buttons have an id in the html hat is the button text
# in lowercase followed by '-btn' so the Clean button has an id of
# id='clear-btn'. That allows us to lowercase the name and add '-btn'
# to get the element id of any button
##################################################################

@when('I press the "{button_name}" button')
def step_impl(context, button_name):
    """ Presiona un botón """
    button_id = button_name.lower().replace(" ", "-") + "-btn"
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.element_to_be_clickable((By.ID, button_id))
    )
    element.click()
    # Esperar a que el mensaje de flash aparezca o la página se actualice
    # Esto puede variar dependiendo de cómo se manejen los mensajes en la UI
    # Se añade una pequeña espera explícita para asegurar que la UI reaccione
    time.sleep(0.5) # Pequeña espera para que la UI se actualice


@then('I should see the message "{message}"')
def step_impl(context, message):
    """ Verifica el mensaje de flash """
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.text_to_be_present_in_element(
            (By.ID, "flash_message"), # Asumiendo que el ID del elemento del mensaje es 'flash_message'
            message
        )
    )
    expect(found).to_be(True)

##################################################################
# This code works because of the following naming convention:
# The id field for text input in the html is the element name
# prefixed by ID_PREFIX so the Name field has an id='pet_name'
# We can then lowercase the name and prefix with pet_ to get the id
##################################################################

@then('I should see "{text_value}" in the "{element_name}" field') # Cambiado text_string a text_value
def step_impl(context, text_value, element_name): # Cambiado text_string a text_value
    """ Verifica que un campo de texto contiene un valor específico """
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.text_to_be_present_in_element_value(
            (By.ID, element_id),
            text_value
        )
    )
    expect(found).to_be(True) # Usar expect para consistencia

@when('I change "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    """ Cambia el valor de un campo de texto """
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)

@given('a product with name "{name}"')
def step_impl(context, name):
    """
    Busca un producto por nombre de la lista de productos cargados
    y almacena su ID en el contexto para uso posterior.
    """
    if 'products' not in context:
        raise Exception("No products loaded in context. Make sure 'Given the following products' step runs first.")

    found_product = None
    for product in context.products:
        if product['name'] == name:
            found_product = product
            break
    
    expect(found_product).to_not_be(None, f"Product with name '{name}' not found in loaded products.")
    
    if 'product_id_map' not in context:
        context.product_id_map = {}
    context.product_id_map[name] = found_product['id']
    LOGGER.info(f"Stored ID {found_product['id']} for product '{name}'")


@when('I set the "{field_name}" field to the ID of "{product_name}"')
def step_impl(context, field_name, product_name):
    """ Establece el campo ID con el ID de un producto específico """
    if 'product_id_map' not in context or product_name not in context.product_id_map:
        raise Exception(f"ID for product '{product_name}' not found in context. Make sure 'Given a product with name' step runs first.")
    
    product_id = context.product_id_map[product_name]
    element_id = field_name.lower().replace(" ", "_")
    if element_id == "id":
        element_id = "product_id"
    
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(str(product_id))
    LOGGER.info(f"Set {field_name} to ID {product_id} for product '{product_name}'")


@then('the "{column_name}" column should contain the ID of "{product_name}"')
def step_impl(context, column_name, product_name):
    """
    Verifica que la columna especificada en la tabla de resultados contiene el ID
    del producto con el nombre dado.
    """
    if 'product_id_map' not in context or product_name not in context.product_id_map:
        raise Exception(f"ID for product '{product_name}' not found in context.")
    
    expected_id = str(context.product_id_map[product_name])
    
    # Esperar a que la tabla de resultados se actualice
    WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((By.ID, "search_results"))
    )
    
    table = context.driver.find_element(By.ID, "search_results")
    rows = table.find_elements(By.TAG_NAME, "tr")
    
    # Encontrar el índice de la columna
    header = rows[0] # Asumiendo que la primera fila es el encabezado
    headers = [th.text for th in header.find_elements(By.TAG_NAME, "th")]
    
    try:
        column_index = headers.index(column_name)
    except ValueError:
        raise Exception(f"Column '{column_name}' not found in table headers: {headers}")

    found = False
    for i, row in enumerate(rows):
        if i == 0: # Saltar la fila del encabezado
            continue
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) > column_index:
            if cols[column_index].text == expected_id:
                found = True
                break
    expect(found).to_be(True, f"ID '{expected_id}' not found in column '{column_name}'")


@then('the "{column_name}" column should contain "{text_value}"')
def step_impl(context, column_name, text_value):
    """
    Verifica que la columna especificada en la tabla de resultados contiene el valor de texto dado.
    """
    # Esperar a que la tabla de resultados se actualice
    WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((By.ID, "search_results"))
    )
    
    table = context.driver.find_element(By.ID, "search_results")
    rows = table.find_elements(By.TAG_NAME, "tr")
    
    # Encontrar el índice de la columna
    header = rows[0] # Asumiendo que la primera fila es el encabezado
    headers = [th.text for th in header.find_elements(By.TAG_NAME, "th")]
    
    try:
        column_index = headers.index(column_name)
    except ValueError:
        raise Exception(f"Column '{column_name}' not found in table headers: {headers}")

    found = False
    for i, row in enumerate(rows):
        if i == 0: # Saltar la fila del encabezado
            continue
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) > column_index:
            if cols[column_index].text == text_value:
                found = True
                break
    expect(found).to_be(True, f"Text '{text_value}' not found in column '{column_name}'")

