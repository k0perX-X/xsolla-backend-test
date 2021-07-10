from pprint import pprint
import json
import requests
import unittest


class Tests(unittest.TestCase):

    def test_post_element(self):
        r = requests.post('http://localhost/goods/element', json={
            'product_name': '123',
            'category': None,
            'sku': "123",
            'price': 300
        })
        print(r)
        j1 = json.loads(r.text)
        pprint(j1)
        self.assertEqual(r.status_code, 201)
        r = requests.post('http://localhost/goods/element', json={
            'product_name': '123',
            'category': None,
            'sku': "123",
            'price': 300
        })
        print(r)
        j2 = json.loads(r.text)
        pprint(j2)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(j1['data']['product_id'] + 1, j2['data']['product_id'])

    def test_post_batch(self):
        r = requests.post('http://localhost/goods/batch', json=[{
            'product_name': '123',
            'category': None,
            'sku': "123",
            'price': 300
        }])
        print(r)
        j1 = json.loads(r.text)
        pprint(j1)
        self.assertEqual(r.status_code, 201)
        r = requests.post('http://localhost/goods/batch', json=[{
            'product_name': '123',
            'category': None,
            'sku': "123",
            'price': 300
        }, {
            'product_name': '123',
            'category': None,
            'sku': "123",
            'price': 300
        }])
        print(r)
        j2 = json.loads(r.text)
        pprint(j2)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(j1['data'][0]['data']['data']['product_id'] + 2, j2['data'][1]['data']['data']['product_id'])

    def test_post_batch10000(self):
        r = requests.post('http://localhost/goods/batch', json=[{
            'product_name': '123',
            'category': None,
            'sku': "123",
            'price': 300
        } for i in range(10000)])
        print(r)
        j2 = json.loads(r.text)
        # pprint(j2)
        self.assertEqual(r.status_code, 201)
        for i in range(len(j2['data']) - 1):
            self.assertEqual(j2['data'][i]['data']['data']['product_id'] + 1, j2['data'][i + 1]['data']['data']['product_id'])

    def test_get_batch(self):
        r = requests.get('http://localhost/goods/batch', json={
            'elements': 1000
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 400)
        r = requests.get('http://localhost/goods/batch', json={
            'elements': 1000,
            'index': 0
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 200)

    def test_get_element(self):
        r = requests.get('http://localhost/goods/element', json={
            'sku': 123,
            'elements': 100,
            'index': 0
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 200)
        r = requests.get('http://localhost/goods/element', json={
            'sku': '123',
            'elements': 100,
            'index': 0
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 200)
        r = requests.get('http://localhost/goods/element', json={
            'id': 2
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 200)
        r = requests.get('http://localhost/goods/element', json={
            'id': 2,
            'sku': 123
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 400)
        r = requests.get('http://localhost/goods/element', json={
            'sku': 123,
            'index': 0
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 400)

    def test_put_element(self):
        r = requests.put('http://localhost/goods/element', json={
            'product_id': 2,
            'edit_data': {
                'product_name': '0',
                'category': 'фигня',
                'sku': "20",
                'price': 3000
            }
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 200)
        r = requests.put('http://localhost/goods/element', json={
            'product_id': 2,
            'edit_data': {
                'product_id': 2,
            }
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 400)
        r = requests.put('http://localhost/goods/element', json={
            'product_id': 2,
            'edit_data': {
                'sku': None,
            }
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 400)
        r = requests.put('http://localhost/goods/element', json={
            'product_id': 2,
            'edit_data': {
                'price': 'awdawdaw'
            }
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 400)

    def test_put_batch(self):
        r = requests.put('http://localhost/goods/batch', json=[{
            'product_id': 2,
            'edit_data': {
                'product_name': '0',
                'category': 'фигня',
                'sku': "20",
                'price': 3000
            }
        }, {
            'product_id': 2,
            'edit_data': {
                'product_id': 2,
            }
        }, {
            'product_id': 2,
            'edit_data': {
                'sku': None,
            }
        }, {
            'product_id': 2,
            'edit_data': {
                'price': 'awdawdaw'
            }
        }])
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 207)
        self.assertEqual(j['data'][0]['HTTP_status_code'], 200)
        self.assertEqual(j['data'][1]['HTTP_status_code'], 400)
        self.assertEqual(j['data'][2]['HTTP_status_code'], 400)
        self.assertEqual(j['data'][3]['HTTP_status_code'], 400)

    def test_delete_element(self):
        r = requests.post('http://localhost/goods/batch', json=[{
            'product_name': '123',
            'category': None,
            'sku': "152",
            'price': 300
        }, {
            'product_name': '123',
            'category': None,
            'sku': "152",
            'price': 300
        }, {
            'product_name': '123',
            'category': None,
            'sku': "152",
            'price': 300
        }])
        print(r)
        j1 = json.loads(r.text)
        pprint(j1)
        self.assertEqual(r.status_code, 201)
        r = requests.delete('http://localhost/goods/element', json={
            'sku': 123,
            'id': 123
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 400)
        r = requests.delete('http://localhost/goods/element', json={
            'id': 'awdawdaw'
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 400)
        r = requests.delete('http://localhost/goods/element', json={
            'id': j1['data'][0]['data']['data']['product_id']
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(j['data']['deleted_rows'], 1)
        r = requests.delete('http://localhost/goods/element', json={
            'sku': 152
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(j['data']['deleted_rows'], 2)

    def test_delete_batch(self):
        r = requests.post('http://localhost/goods/batch', json=[{
            'product_name': '123',
            'category': None,
            'sku': "205",
            'price': 300
        }, {
            'product_name': '123',
            'category': None,
            'sku': 205,
            'price': 300
        }, {
            'product_name': '123',
            'category': None,
            'sku': "205",
            'price': 300
        }])
        print(r)
        j1 = json.loads(r.text)
        pprint(j1)
        self.assertEqual(r.status_code, 201)
        r = requests.delete('http://localhost/goods/batch', json=[{
            'id': j1['data'][0]['data']['data']['product_id']
        }, {
            'sku': 205
        }])
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(j['data'][0]['data']['data']['deleted_rows'], 1)
        self.assertEqual(j['data'][1]['data']['data']['deleted_rows'], 2)

    def test_delete_elementSKU123(self):
        r = requests.delete('http://localhost/goods/element', json={
            'sku': 123
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 200)


if __name__ == '__main__':
    unittest.main()
