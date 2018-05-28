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
        p = Product(name="mesa", price=20)
        
        db.session.commit()
        order = Order(id=1)
        orderProduct = OrderProduct(order_id=1, product_id=1, quantity=-3, product=p)
        order.products.append(orderProduct)
        db.session.add(order)
        db.session.commit()
        op = OrderProduct.query.all()
        self.assertEqual(len(op), 0, "Se creo con cantidad negativa")
        
    
    def test_get_product(self):
         p = Product(name="silla", price=15)
         db.session.add(p)
         orde=Order()
         db.session.add(orde)
         op=OrderProduct(order_id = 1, product_id = 1, product= p, quantity=10)
         db.session.add(op)
         db.session.commit()
         resp = self.client.get('/order/1/product/1')
         product = json.loads(resp.data)
         self.assert200(resp, "No existe orden y/o producto")

if __name__ == '__main__':
    unittest.main()

