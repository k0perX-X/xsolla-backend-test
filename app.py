from flask import Flask, request
import psycopg2
import json
import logging

app = Flask(__name__)
table_name = 'goods'
commit_timer_seconds = 5
max_elements_per_request = 2000
logging.basicConfig(filename="/var/lib/postgresql/data/log.txt", level=logging.WARNING)
columns = ['product_id', 'product_name', 'category', 'sku', 'price']

conn = psycopg2.connect(dbname='goods', user='postgres',
                        password='', host='localhost')
conn.autocommit = True
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS goods (
    product_id bigserial NOT NULL UNIQUE,
    product_name text,
    category text,
    sku text NOT NULL,
    price real NOT NULL,
    PRIMARY KEY (product_id));""")


# Status codes:
# 0 - OK
# 1 - JSONDecodeError
# 2 - InvalidJSONFormat
# 3 - NotNullViolation
# 4 - InvalidTextRepresentation
# 5 - IdNotInTable

def elements_index_args_check(r: dict) -> tuple:
    if 'index' not in r or 'elements' not in r:
        return {"status": "InvalidJSONFormat: index or elements not in json", "status_code": 2}, 400

    if not str(r['index']).isdigit():
        return {"status": "InvalidJSONFormat: index is not digit", "status_code": 2}, 400
    else:
        index = int(r['index'])

    if not str(r['elements']).isdigit():
        return {"status": "InvalidJSONFormat: elements is not digit", "status_code": 2}, 400
    else:
        elements = int(r['elements'])
    if elements > max_elements_per_request:
        return {"status": "InvalidJSONFormat: elements is greater than allowed", "status_code": 2}, 400

    return index, elements


@app.route('/goods/batch', methods=["GET"])
def batch_get():
    # {
    #     'elements': 100,
    #     'index': 0
    # }
    try:
        r = json.loads(request.data)
    except json.JSONDecodeError:
        return {"status": "JSONDecodeError", "status_code": 1}, 400

    t = elements_index_args_check(r)
    logging.error(str(t))
    if type(t[0]) == dict:
        return t
    else:
        index, elements = t

    cursor.execute("SELECT COUNT(*) FROM public.goods")
    rows = cursor.fetchall()[0][0]
    cursor.execute("SELECT product_id, product_name, category, sku, price FROM goods "
                   f"ORDER BY product_id LIMIT {elements} OFFSET {index}")

    return {
               "status": "OK",
               "status_code": 0,
               "data": {
                   "rows": rows,
                   'data': [{
                       "product_id": row[0],
                       'product_name': row[1],
                       'category': row[2],
                       'sku': row[3],
                       'price': row[4],
                   } for row in cursor.fetchall()]
               }
           }, 200


@app.route('/goods/element', methods=["GET"])
def element_get():
    # {
    #     'sku': 213,
    #     'elements': 100,
    #     'index': 0
    # }
    # {
    #     'id': 123
    # }
    try:
        r = json.loads(request.data)
    except json.JSONDecodeError:
        return {"status": "JSONDecodeError", "status_code": 1}, 400

    if 'sku' not in r and 'id' not in r:
        return {"status": "InvalidJSONFormat: sku and id not in json", "status_code": 2}, 400
    elif 'sku' in r and 'id' in r:
        return {"status": "InvalidJSONFormat: sku and id in json at the same time", "status_code": 2}, 400

    # sku
    elif 'sku' in r:
        t = elements_index_args_check(r)
        if type(t[0]) == dict:
            return t
        else:
            index, elements = t

        cursor.execute(f"SELECT COUNT(*) FROM goods WHERE sku = '{r['sku']}'")
        rows = cursor.fetchall()[0][0]
        cursor.execute("SELECT product_id, product_name, category, sku, price FROM goods "
                       f"WHERE sku = '{r['sku']}' ORDER BY product_id "
                       f"LIMIT {elements} OFFSET {index}")

        return {
                   "status": "OK",
                   "status_code": 0,
                   "data": {
                       'rows': rows,
                       'data': [{
                           "product_id": row[0],
                           'product_name': row[1],
                           'category': row[2],
                           'sku': row[3],
                           'price': row[4],
                       } for row in cursor.fetchall()]
                   }
               }, 200

    # id
    else:
        if not str(r['id']).isdigit():
            return {"status": "JSONDecodeError: id is not digit", "status_code": 1}, 400
        else:
            ID = int(r['id'])

        cursor.execute(f"SELECT product_id, product_name, category, sku, price FROM goods WHERE product_id = {ID}")
        return {
                   "status": "OK",
                   "status_code": 0,
                   "data": {
                       'rows': 1,
                       'data': [{
                           "product_id": row[0],
                           'product_name': row[1],
                           'category': row[2],
                           'sku': row[3],
                           'price': row[4],
                       } for row in cursor.fetchall()]
                   }
               }, 200


@app.route('/goods/element', methods=["POST"])
def element_post():
    # {
    #     'product_name': '123',
    #     'category': None,
    #     'sku': "123",
    #     'price': 300
    # }
    try:
        r = json.loads(request.data)
    except json.JSONDecodeError:
        return {"status": "JSONDecodeError: id is not digit", "status_code": 1}, 400

    return add_row(r)


def add_row(r: dict):
    if 'product_name' not in r or 'category' not in r or 'sku' not in r or 'price' not in r:
        return {"status": "InvalidJSONFormat: product_name or category or sku or price not in json",
                "status_code": 2}, 400

    try:
        cursor.execute("INSERT INTO goods (product_name,category,sku,price) "
                       "VALUES (%s, %s, %s, %s); "
                       "SELECT product_id, product_name, category, sku, price FROM goods "
                       "ORDER BY product_id DESC LIMIT 1;",
                       [r['product_name'], r['category'], r['sku'], r['price']])
    except psycopg2.errors.NotNullViolation:
        return {"status": "NotNullViolation", "status_code": 3}, 400
    except psycopg2.errors.InvalidTextRepresentation:
        return {"status": "InvalidTextRepresentation", "status_code": 4}, 400

    row = cursor.fetchall()[0]
    return {
               "status": "OK",
               "status_code": 0,
               "data": {
                   "product_id": row[0],
                   'product_name': row[1],
                   'category': row[2],
                   'sku': row[3],
                   'price': row[4],
               }
           }, 201


@app.route('/goods/batch', methods=["POST"])
def batch_post():
    # [
    #     {
    #         'product_name': '123',
    #         'category': None,
    #         'sku': "123",
    #         'price': 300
    #     },
    #     {
    #         'product_name': '123',
    #         'category': None,
    #         'sku': "123",
    #         'price': 300
    #     }
    # ]
    try:
        r = json.loads(request.data)
    except json.JSONDecodeError:
        return {"status": "JSONDecodeError: id is not digit", "status_code": 1}, 400

    if type(r) != list:
        return {"status": "InvalidJSONFormat", "status_code": 2}, 400
    status = 201
    l = []
    for i in r:
        row = add_row(i)
        if row[1] == 400:
            status = 207
        l.append({
            'data': row[0],
            'HTTP_status_code': row[1]
        })
    return {
               "status": "OK",
               "status_code": 0,
               "data": [l]
            }, status


@app.route('/goods/element', methods=["PUT"])
def element_put():
    # {
    #     'product_id': 1203,
    #     'edit_data': {
    #         'product_name': '123',
    #         'category': None,
    #         'sku': "123",
    #         'price': 300
    #     }
    # }
    try:
        r = json.loads(request.data)
    except json.JSONDecodeError:
        return {"status": "JSONDecodeError", "status_code": 1}, 400
    return edit_row(r)


def edit_row(r: dict):
    if 'product_id' not in r or 'edit_data' not in r:
        return {"status": "InvalidJSONFormat: product_id or edit_data not in json", "status_code": 2}, 400
    if type(r['edit_data']) != dict:
        return {"status": "InvalidJSONFormat: edit_data is not dictionary", "status_code": 2}, 400
    delete_keys = []
    for i in r['edit_data']:
        if i not in columns or i == 'product_id':
            delete_keys.append(i)
    for i in delete_keys:
        del r['edit_data'][i]
    if len(r['edit_data']) < 1:
        return {"status": "InvalidJSONFormat: edit_data does not contain required fields", "status_code": 2}, 400

    try:
        cursor.execute("SELECT COUNT(*) FROM goods WHERE product_id = %s;", [r['product_id']])
        if cursor.fetchall()[0][0] == 0:
            return {"status": "IdNotInTable", "status_code": 5}, 400
        cursor.execute(f"UPDATE goods SET {', '.join([i + ' = %s' for i in r['edit_data'].keys()])} "
                       "WHERE product_id = %s; "
                       "SELECT product_id, product_name, category, sku, price FROM goods WHERE product_id = %s;",
                       [*r['edit_data'].values(), r['product_id'], r['product_id']])
    except psycopg2.errors.NotNullViolation:
        return {"status": "NotNullViolation", "status_code": 3}, 400
    except psycopg2.errors.InvalidTextRepresentation:
        return {"status": "InvalidTextRepresentation", "status_code": 4}, 400

    row = cursor.fetchall()[0]
    return {
               "status": "OK",
               "status_code": 0,
               "data": {
                   "product_id": row[0],
                   'product_name': row[1],
                   'category': row[2],
                   'sku': row[3],
                   'price': row[4],
               }
           }, 200


@app.route('/goods/batch', methods=["PUT"])
def batch_put():
    # [
    #     {
    #         'product_id': 1203,
    #         'edit_data': {
    #             'product_name': '123',
    #             'category': None,
    #             'sku': "123",
    #             'price': 300
    #         }
    #     },
    #     {
    #         'product_id': 1203,
    #         'edit_data': {
    #             'product_name': '123',
    #             'category': None,
    #             'sku': "123",
    #             'price': 300
    #         }
    #     }
    # ]
    try:
        r = json.loads(request.data)
    except json.JSONDecodeError:
        return {"status": "JSONDecodeError: id is not digit", "status_code": 1}, 400

    if type(r) != list:
        return {"status": "InvalidJSONFormat", "status_code": 2}, 400
    status = 200
    l = []
    for i in r:
        row = edit_row(i)
        if row[1] == 400:
            status = 207
        l.append({
            'data': row[0],
            'HTTP_status_code': row[1]
        })
    return {
               "status": "OK",
               "status_code": 0,
               "data": [l]
            }, status


@app.route('/goods/element', methods=["DELETE"])
def element_delete():
    # {
    #     'sku': 213
    # }
    # {
    #     'id': 123
    # }
    try:
        r = json.loads(request.data)
    except json.JSONDecodeError:
        return {"status": "JSONDecodeError", "status_code": 1}, 400
    return delete_row(r)


def delete_row(r: dict):
    if 'sku' not in r and 'id' not in r:
        return {"status": "InvalidJSONFormat: sku and id not in json", "status_code": 2}, 400
    elif 'sku' in r and 'id' in r:
        return {"status": "InvalidJSONFormat: sku and id in json at the same time", "status_code": 2}, 400

    # sku
    elif 'sku' in r:
        cursor.execute(f"SELECT COUNT(*) FROM goods WHERE sku = '{r['sku']}'")
        rows = cursor.fetchall()[0][0]
        cursor.execute(f"DELETE FROM goods WHERE sku = '{r['sku']}'")

        return {
                   "status": "OK",
                   "status_code": 0,
                   "deleted_rows": rows
               }, 200

    # id
    else:
        if not str(r['id']).isdigit():
            return {"status": "JSONDecodeError: id is not digit", "status_code": 1}, 400
        else:
            ID = int(r['id'])

        cursor.execute(f"SELECT COUNT(*) FROM goods WHERE product_id = {ID}")
        rows = cursor.fetchall()[0][0]
        cursor.execute(f"DELETE FROM goods WHERE product_id = {ID}")

        return {
                   "status": "OK",
                   "status_code": 0,
                   "deleted_rows": rows
               }, 200


@app.route('/goods/batch', methods=["DELETE"])
def batch_delete():
    # [
    #     {
    #         'sku': 213
    #     },
    #     {
    #         'id': 123
    #     }
    # ]
    try:
        r = json.loads(request.data)
    except json.JSONDecodeError:
        return {"status": "JSONDecodeError: id is not digit", "status_code": 1}, 400

    if type(r) != list:
        return {"status": "InvalidJSONFormat", "status_code": 2}, 400
    status = 200
    l = []
    for i in r:
        row = delete_row(i)
        if row[1] == 400:
            status = 207
        l.append({
            'data': row[0],
            'HTTP_status_code': row[1]
        })
    return {
               "status": "OK",
               "status_code": 0,
               "data": [l]
            }, status


def main():
    app.run()


if __name__ == '__main__':
    main()
