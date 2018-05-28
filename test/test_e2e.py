import unittest
import os
import time
import threading

from selenium import webdriver
from selenium.webdriver.common.keys import Keys 

from app import create_app, db
from app.models import Product, Order, OrderProduct

basedir = os.path.abspath(os.path.dirname(__file__))

class Ordering(unittest.TestCase):
    # Creamos la base de datos de test
    def setUp(self):
        self.app = create_app()
        self.app.config.update(
            SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir, 'test.db'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            TESTING=True
        )
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.baseURL = 'http://localhost:5000'

        db.session.commit()
        db.drop_all()
        db.create_all()

        # start the Flask server in a thread
        threading.Thread(target=self.app.run).start()

        # give the server a second to ensure it is up
        time.sleep(1)

        self.driver = webdriver.Chrome()

    def test_title(self):
        driver = self.driver
        driver.get(self.baseURL)
        add_product_button = driver.find_element_by_xpath('/html/body/main/div[1]/div/button')
        add_product_button.click()
        modal = driver.find_element_by_id('modal')
        assert modal.is_displayed(), "El modal no esta visible"

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.driver.close()

    def test_cant_negativo(self):
        orden = Order(id= 1)
        db.session.add(orden)
        producto = Product(name= 'mesa', price= 10)
        db.session.add(producto)
        db.session.commit()
        driver = self.driver
        driver.get(self.baseURL)
        boton_agregar_producto = driver.find_element_by_xpath('/html/body/main/div[1]/div/button')
        boton_agregar_producto.click()
        seleccionar_producto = driver.find_element_by_id('select-prod')
        seleccionar_producto.click()
        opcion_seleccionada = driver.find_element_by_xpath('//*[@id="select-prod"]/option[2]')
        opcion_seleccionada.click()
        cantidad_ingresada = driver.find_element_by_xpath('//*[@id="quantity"]')
        cantidad_ingresada.send_keys(Keys.DELETE)
        cant = "-3" 
        cantidad_ingresada.send_keys(str(cant))
        time.sleep(5)
        boton_guardar = driver.find_element_by_xpath('//*[@id="save-button"]')
        boton_guardar.click()
        time.sleep(10) 
        cantidad_en_tabla = driver.find_element_by_xpath('//*[@id="orders"]/table/tbody/tr/td[4]')
        self.assertGreater(int(cantidad_en_tabla.text),0,"Agrego una cantidad negativa")

if __name__ == "__main__":
    unittest.main()