from pprint import pprint
import json
import requests
import unittest
from time import sleep
from multiprocessing.pool import Pool
max_request_per_batch = 100
max_elements_per_request = 2000

url = 'xsolla.jelastic.regruhosting.ru'  # 'localhost'  #


class Tests(unittest.TestCase):

    def test_post_element(self):
        r = requests.post(f'http://{url}/goods/element', json={
            'product_name': '123',
            'category': None,
            'sku': "123",
            'price': 300
        })
        print(r)
        j1 = json.loads(r.text)
        pprint(j1)
        self.assertEqual(r.status_code, 201)
        r = requests.post(f'http://{url}/goods/element', json={
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
        r = requests.post(f'http://{url}/goods/batch', json=[{
            'product_name': '123',
            'category': None,
            'sku': "123",
            'price': 300
        }])
        print(r)
        j1 = json.loads(r.text)
        pprint(j1)
        self.assertEqual(r.status_code, 201)
        r = requests.post(f'http://{url}/goods/batch', json=[{
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
        r = requests.post(f'http://{url}/goods/batch', json=[{
            'product_name': '123',
            'category': None,
            'sku': "250",
            'price': 300
        } for i in range(10000)])
        print(r)
        j2 = json.loads(r.text)
        # pprint(j2)
        self.assertEqual(r.status_code, 201)
        for i in range(len(j2['data']) - 1):
            self.assertEqual(j2['data'][i]['data']['data']['product_id'] + 1,
                             j2['data'][i + 1]['data']['data']['product_id'])

    def test_get_batch(self):
        r = requests.get(f'http://{url}/goods/batch', json={
            'elements': 1000
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 400)
        r = requests.get(f'http://{url}/goods/batch', json={
            'elements': 1000,
            'index': 0
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 200)
        r = requests.get(f'http://{url}/goods/batch', json={
            'elements': 100,
            'index': -1
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 400)


    def test_get_element(self):
        r = requests.get(f'http://{url}/goods/element', json={
            'sku': 123,
            'elements': 100,
            'index': 0
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 200)
        r = requests.get(f'http://{url}/goods/element', json={
            'sku': '123',
            'elements': 100,
            'index': 0
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 200)
        r = requests.get(f'http://{url}/goods/element', json={
            'product_id': 2
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 200)
        r = requests.get(f'http://{url}/goods/element', json={
            'product_id': 2,
            'sku': 123
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 400)
        r = requests.get(f'http://{url}/goods/element', json={
            'sku': 123,
            'index': 0
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 400)

    def test_put_element(self):
        r = requests.post(f'http://{url}/goods/element', json={
            'product_name': '123',
            'category': None,
            'sku': "123",
            'price': 300
        })
        print(r)
        j1 = json.loads(r.text)
        self.assertEqual(r.status_code, 201)
        r = requests.put(f'http://{url}/goods/element', json={
            'product_id': j1['data']['product_id'],
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
        r = requests.put(f'http://{url}/goods/element', json={
            'product_id': j1['data']['product_id'],
            'edit_data': {
                'product_id': 2,
            }
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 400)
        r = requests.put(f'http://{url}/goods/element', json={
            'product_id': j1['data']['product_id'],
            'edit_data': {
                'sku': None,
            }
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 400)
        r = requests.put(f'http://{url}/goods/element', json={
            'product_id': j1['data']['product_id'],
            'edit_data': {
                'price': 'awdawdaw'
            }
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 400)
        r = requests.put(f'http://{url}/goods/element', json={
            'product_id': j1['data']['product_id'],
            'edit_data': {
            }
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 400)


    def test_put_batch(self):
        r = requests.post(f'http://{url}/goods/element', json={
            'product_name': '123',
            'category': None,
            'sku': "123",
            'price': 300
        })
        print(r)
        j1 = json.loads(r.text)
        self.assertEqual(r.status_code, 201)
        r = requests.put(f'http://{url}/goods/batch', json=[{
            'product_id': j1['data']['product_id'],
            'edit_data': {
                'product_name': '0',
                'category': 'фигня',
                'sku': "20",
                'price': 3000
            }
        }, {
            'product_id': j1['data']['product_id'],
            'edit_data': {
                'product_id': 2,
            }
        }, {
            'product_id': j1['data']['product_id'],
            'edit_data': {
                'sku': None,
            }
        }, {
            'product_id': j1['data']['product_id'],
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
        r = requests.post(f'http://{url}/goods/batch', json=[{
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
        r = requests.delete(f'http://{url}/goods/element', json={
            'sku': 123,
            'product_id': 123
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 400)
        r = requests.delete(f'http://{url}/goods/element', json={
            'product_id': 'awdawdaw'
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 400)
        r = requests.delete(f'http://{url}/goods/element', json={
            'product_id': j1['data'][0]['data']['data']['product_id']
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(j['data']['deleted_rows'], 1)
        r = requests.delete(f'http://{url}/goods/element', json={
            'sku': 152
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(j['data']['deleted_rows'], 2)

    def test_delete_batch(self):
        r = requests.post(f'http://{url}/goods/batch', json=[{
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
        r = requests.delete(f'http://{url}/goods/batch', json=[{
            'product_id': j1['data'][0]['data']['data']['product_id']
        }, {
            'sku': 205
        }])
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(j['data'][0]['data']['data']['deleted_rows'], 1)
        self.assertEqual(j['data'][1]['data']['data']['deleted_rows'], 2)

    def test_delete_elementSKU250(self):
        r = requests.delete(f'http://{url}/goods/element', json={
            'sku': 250
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 200)

    def test_request(self):
        sleep(3)
        self.clear_all_data()

        r = requests.post(f'http://{url}/goods/batch', json=[{
            'product_name': '123',
            'category': None,
            'sku': "589s",
            'price': 100
        }, {
            'product_name': '123',
            'category': None,
            'sku': 589,
            'price': 150
        }, {
            'product_name': '123',
            'category': None,
            'sku': "589",
            'price': 300
        }])
        print(r)
        j1 = json.loads(r.text)
        pprint(j1)
        self.assertEqual(r.status_code, 201)

        r = requests.get(f'http://{url}/goods/request', json={
            'greater': {
                'price': 123
            },
            'less': {
                'price': 301
            },
            # 'equal': {
            #     'product_id': [123],
            #     'product_name': ['123'],
            #     'category': ['123'],
            #     'sku': ['132'],
            #     'price': [123]
            # },
            # 'not_equal':{
            #     'product_id': [123],
            #     'product_name': ['123'],
            #     'category': ['123'],
            #     'sku': ['132'],
            #     'price': [123]
            # },
            # 'like': {
            #     'product_name': ['123'],
            #     'category': ['123'],
            #     'sku': ['132'],
            # },
            'and/or': 'and',
            'elements': 100,
            'index': 0
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(j['data']['data']), 2)
        r = requests.get(f'http://{url}/goods/request', json={
            # 'greater': {
            #     'price': 123
            # },
            'less': {
                'price': 100
            },
            # 'equal': {
            #     'product_id': [123],
            #     'product_name': ['123'],
            #     'category': ['123'],
            #     'sku': ['132'],
            #     'price': [123]
            # },
            # 'not_equal':{
            #     'product_id': [123],
            #     'product_name': ['123'],
            #     'category': ['123'],
            #     'sku': ['132'],
            #     'price': [123]
            # },
            # 'like': {
            #     'product_name': ['123'],
            #     'category': ['123'],
            #     'sku': ['132'],
            # },
            'and/or': 'and',
            'elements': 100,
            'index': 0
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(j['data']['data']), 0)
        r = requests.get(f'http://{url}/goods/request', json={
            # 'greater': {
            #     'price': 123
            # },
            # 'less': {
            #     'price': 100
            # },
            'equal': {
                # 'product_id': [123],
                # 'product_name': ['123'],
                # 'category': ['123'],
                'sku': 589,
                # 'price': [123]
            },
            # 'not_equal':{
            #     'product_id': [123],
            #     'product_name': ['123'],
            #     'category': ['123'],
            #     'sku': ['132'],
            #     'price': [123]
            # },
            # 'like': {
            #     'product_name': ['123'],
            #     'category': ['123'],
            #     'sku': ['132'],
            # },
            'and/or': 'and',
            'elements': 100,
            'index': 0
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(j['data']['data']), 2)
        r = requests.get(f'http://{url}/goods/request', json={
            # 'greater': {
            #     'price': 123
            # },
            # 'less': {
            #     'price': 100
            # },
            # 'equal': {
            #     # 'product_id': [123],
            #     # 'product_name': ['123'],
            #     # 'category': ['123'],
            #     'sku': ['205'],
            #     # 'price': [123]
            # },
            'not_equal': {
                # 'product_id': [123],
                # 'product_name': ['123'],
                # 'category': ['123'],
                'sku': ['589s'],
                # 'price': [123]
            },
            # 'like': {
            #     'product_name': ['123'],
            #     'category': ['123'],
            #     'sku': ['132'],
            # },
            'and/or': 'and',
            'elements': 100,
            'index': 0
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(j['data']['data']), 2)
        r = requests.get(f'http://{url}/goods/request', json={
            # 'greater': {
            #     'price': 123
            # },
            # 'less': {
            #     'price': 100
            # },
            # 'equal': {
            #     # 'product_id': [123],
            #     # 'product_name': ['123'],
            #     # 'category': ['123'],
            #     'sku': ['205'],
            #     # 'price': [123]
            # },
            # 'not_equal':{
            #     # 'product_id': [123],
            #     # 'product_name': ['123'],
            #     # 'category': ['123'],
            #     'sku': ['205s'],
            #     # 'price': [123]
            # },
            'like': {
                # 'product_name': ['123'],
                # 'category': ['123'],
                'sku': ['%s'],
            },
            'and/or': 'and',
            'elements': 100,
            'index': 0
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(j['data']['data']), 1)
        r = requests.get(f'http://{url}/goods/request', json={
            'greater': {
                'price': 150
            },
            'less': {
                'price': 150
            },
            # 'equal': {
            #     # 'product_id': [123],
            #     # 'product_name': ['123'],
            #     # 'category': ['123'],
            #     'sku': ['205'],
            #     # 'price': [123]
            # },
            # 'not_equal':{
            #     # 'product_id': [123],
            #     # 'product_name': ['123'],
            #     # 'category': ['123'],
            #     'sku': ['205s'],
            #     # 'price': [123]
            # },
            # 'like': {
            #     # 'product_name': ['123'],
            #     # 'category': ['123'],
            #     'sku': ['%s'],
            # },
            'and/or': 'or',
            'elements': 100,
            'index': 0
        })
        print(r)
        j = json.loads(r.text)
        pprint(j)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(j['data']['data']), 2)

    @staticmethod
    def clear_all_data():
        r = requests.get(f'http://{url}/goods/request', json={
            'greater': {
                'product_id': 0
            },
            'and/or': 'and',
            'elements': max_elements_per_request,
            'index': 0
        })
        print(r)
        j = json.loads(r.text)
        # pprint(j)
        l = [i['product_id'] for i in j['data']['data']]
        g = max_elements_per_request
        while g < j['data']['rows']:
            r = requests.get(f'http://{url}/goods/request', json={
                'greater': {
                    'product_id': 0
                },
                'and/or': 'and',
                'elements': max_elements_per_request,
                'index': g - 1
            })
            g += max_elements_per_request
            l += [i['product_id'] for i in j['data']['data']]
        while len(l) > 0:
            js = []
            for i in range(max_request_per_batch):
                if len(l) > 0:
                    js.append({'product_id': l.pop()})
                else:
                    break
            r = requests.delete(f'http://{url}/goods/batch', json=js)
            print(r)
            # j = json.loads(r.text)
            # pprint(j)

    # def test_ddos(self):
    #     def f(a):
    #         r = requests.post(f'http://{url}/goods/element', json={
    #             'product_name': '123',
    #             'category': None,
    #             'sku': "123",
    #             'price': 300
    #         })
    #         print(r)
    #         return r.status_code
    #     p = Pool(100)
    #     s = p.map(f, [i for i in range(10000)])
    #     j = {}
    #     for i in s:
    #         if i not in j:
    #             j[i] = 0
    #         else:
    #             j[i] += 1
    #     pprint(j)


if __name__ == '__main__':
    Tests.clear_all_data()
    unittest.main()
    sleep(10)
    Tests.clear_all_data()
