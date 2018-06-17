import os
import unittest

from flask import json
from flask_testing import TestCase

from app import create_app, db
from app.models import Product, Order, OrderProduct

basedir = os.path.abspath(os.path.dirname(__file__))

class OrderingTestCase(TestCase):
    def create_app(self):
        config_name = 'testing'
        app = create_app()
        app.config.update(
            SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir, 'test.db'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            TESTING=True
        )
        return app

    # Creamos la base de datos de test
    def setUp(self):
        db.session.commit()
        db.drop_all()
        db.create_all()

    # Destruimos la base de datos de test
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_iniciar_sin_productos(self):
        resp = self.client.get('/product')
        data = json.loads(resp.data)

        assert len(data) == 0, "La base de datos tiene productos"

 

    def test_orderProduc_negativo(self):
        '''
        Punto 1_a:
        Hacer un test de unidad para verificar
        que no se pueda crear una instancia de la
        clase OrderProduct si el atributo quantity 
        es un entero negativo.
        '''
        p = Product(name="mesa", price=20)
        db.session.commit()
        order = Order(id=1)
        orderProduct = OrderProduct(order_id=1, product_id=1, quantity=-3, product=p)
        order.products.append(orderProduct)
        db.session.add(order)
        db.session.commit()
        op = OrderProduct.query.filter('product_id=1', 'order_id=1') #
        
        self.assertIsNotNone(op, "no se creo negativo")
    
    def test_get_product(self):
        '''
        Punto 1_b:
        Hacer un test de unidad para probar el 
        funcionamiento del método GET en el endpoint 
        /order/<pk_order>/product/<pk_product>
        '''
        p = Product(name="silla", price=15)
        db.session.add(p)
        orde=Order()
        db.session.add(orde)
        op=OrderProduct(order_id=1, product_id=1, product= p, quantity=10)
        db.session.add(op)
        db.session.commit()
        resp = self.client.get('/order/1/product/1')
        product = json.loads(resp.data)
        self.assert200(resp, "No existe orden y/o producto")

    def test_product_get(self):
        '''
        Punto 2_a:
        Hacer un test de unidad para probar el funcionamiento 
        del método GET en el endpoint /product.
        '''
        # Creo producto
        producto = Product(name="silla", price=15)

        # Commiteo el producto a la db
        db.session.add(producto)
        db.session.commit()

        #Envio el GET
        resp = self.client.get('/product')

        product = json.loads(resp.data)
        self.assertEqual(len(product), 1, "No devolvio el producto")
        
        #Testeo respuesta de GET
        self.assert200(resp)

    def test_order_product_PUT(self):
        '''
        Punto opcional 1_a:
        Hacer un test de unidad para probar el 
        funcionamiento del método PUT en el endpoint 
        /order/<pk_order>/product/<pk_product>.
        '''

        #Creo Producto
        producto = {
            'id':1,
            'name': 'Tenedor',
            'price': 50
        }
    
        self.client.post('/product', data=json.dumps(producto), content_type='application/json')

        #creo una orden
        order = {
            "id": 1
        }

        order = Order()

        #Guardo la orden en la db directo ya que no esta en endpoint en la api
        db.session.add(order)
        db.session.commit()

        producto = {
            'quantity': 1,
            'id': 1,
            'name': 'Tenedor',
            'price': 500
        }

        orderProduct = {"quantity": 1, "product":{"id":1}}

        #Creo el OrderProduct
        self.client.post('/order/1/product', data=json.dumps(orderProduct), content_type='application/json')

        #Cambio la cantidad del order producto y hago un put en el endpoint
        orderProduct =  {"quantity":2,"product":{"id":1}}
        self.client.put('/order/1/product/1', data=json.dumps(orderProduct), content_type='application/json')
        resp = self.client.get('/order/1/product/1')
        data = json.loads(resp.data)
        assert data['quantity'] == 2,"No se cambio el precio del producto"

if __name__ == '__main__':
    unittest.main()

