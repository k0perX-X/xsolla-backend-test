from flask import Flask, request
import psycopg2
import json
import logging
import configparser

config = configparser.ConfigParser()
config.read("settings.ini")

app = Flask(__name__)
max_elements_per_request = int(config["Settings"]["max_elements_per_request"])
max_request_per_batch = int(config["Settings"]["max_request_per_batch"])
logging.basicConfig(filename=config["Settings"]["log_file_path"], level=logging.WARNING)
columns = ['product_id', 'product_name', 'category', 'sku', 'price']
str_columns = ['product_name', 'category', 'sku']

conn = psycopg2.connect(dbname=config["Database"]["dbname"], user=config["Database"]["user"],
                        password=config["Database"]["password"], host=config["Database"]["host"])
conn.autocommit = True
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS goods (
    product_id bigserial NOT NULL UNIQUE,
    product_name text,
    category text,
    sku text NOT NULL,
    price real NOT NULL,
    PRIMARY KEY (product_id));""")

# TODO: apiTokens

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
    if elements < 1:
        return {"status": "InvalidJSONFormat: elements is less than allowed", "status_code": 2}, 400
    if index < 0:
        return {"status": "InvalidJSONFormat: index is less than allowed", "status_code": 2}, 400

    return index, elements


@app.route('/goods/request')
def request_data():
    # {
    #     'greater': {
    #         'product_id': 123,
    #         'price': 123
    #     },
    #     'less': {
    #         'product_id': 123,
    #         'price': 123
    #     },
    #     'equal': {
    #         'product_id': [123],
    #         'product_name': ['123'],
    #         'category': ['123'],
    #         'sku': ['132'],
    #         'price': [123]
    #     },
    #     'not_equal':{
    #         'product_id': [123],
    #         'product_name': ['123'],
    #         'category': ['123'],
    #         'sku': ['132'],
    #         'price': [123]
    #     },
    #     'like': {
    #         'product_name': ['123'],
    #         'category': ['123'],
    #         'sku': ['132'],
    #     },
    #     'and/or': 'and',
    #     'elements': 100,
    #     'index': 0
    # }
    try:
        r = json.loads(request.data)
    except json.JSONDecodeError:
        return {"status": "JSONDecodeError", "status_code": 1}, 400

    t = elements_index_args_check(r)
    if type(t[0]) == dict:
        return t
    else:
        index, elements = t

    if 'and/or' not in r:
        return {"status": "InvalidJSONFormat: and/or not in json", "status_code": 2}, 400

    for i in r:
        if type(r[i]) == dict:
            for j in r[i]:
                if j in str_columns:
                    if type(r[i][j]) == int:
                        r[i][j] = str(r[i][j])
                    elif type(r[i][j]) == list:
                        for g in range(len(r[i][j])):
                            r[i][j][g] = str(r[i][j][g])

    requests = []
    lst = []
    # for i in ('greater', 'less', 'equal', 'not_equal', 'like'):
    if 'greater' in r:
        for j in r['greater']:
            if j in ('product_id', 'price'):
                requests.append(f'"{j}" > %s')
                lst.append(r["greater"][j])

    if 'less' in r:
        for j in r['less']:
            if j in ('product_id', 'price'):
                requests.append(f'"{j}" < %s')
                lst.append(r["less"][j])

    if 'equal' in r:
        for j in r['equal']:
            if type(r['equal'][j]) != list:
                requests.append(f'"{j}" = %s')
                lst.append(r["equal"][j])
            else:
                for i in r['equal'][j]:
                    requests.append(f'"{j}" = %s')
                    lst.append(i)

    if 'not_equal' in r:
        for j in r['not_equal']:
            if type(r['not_equal'][j]) != list:
                requests.append(f'not({j} = %s)')
                lst.append(r["not_equal"][j])
            else:
                for i in r['not_equal'][j]:
                    requests.append(f'not({j} = %s)')
                    lst.append(i)

    if 'like' in r:
        for j in r['like']:
            if j in str_columns:
                if type(r['like'][j]) != list:
                    requests.append(f'"{j}" like %s')
                    lst.append(r["like"][j])
                else:
                    for i in r['like'][j]:
                        requests.append(f'"{j}" like %s')
                        lst.append(i)

    if len(requests) == 0:
        return {"status": "InvalidJSONFormat: empty request", "status_code": 2}, 400

    try:
        if r['and/or'].lower() == 'and':
            cursor.execute("SELECT product_id, product_name, category, sku, price FROM goods "
                           f"WHERE {' and '.join([i for i in requests])} "
                           f"ORDER BY product_id LIMIT {elements} OFFSET {index}; ", lst)
        elif r['and/or'].lower() == 'or':
            cursor.execute("SELECT product_id, product_name, category, sku, price FROM goods "
                           f"WHERE {' or '.join([i for i in requests])} "
                           f"ORDER BY product_id LIMIT {elements} OFFSET {index}; ", lst)
        else:
            return {"status": "InvalidJSONFormat: and/or is not correct", "status_code": 2}, 400
    except psycopg2.errors.NotNullViolation:
        return {"status": "NotNullViolation", "status_code": 3}, 400
    except psycopg2.errors.InvalidTextRepresentation:
        return {"status": "InvalidTextRepresentation", "status_code": 4}, 400
    except psycopg2.errors.UndefinedFunction:
        return {"status": "InvalidTextRepresentation", "status_code": 4}, 400
    except psycopg2.ProgrammingError:
        return {"status": "InvalidTextRepresentation", "status_code": 4}, 400

    rows = cursor.fetchall()
    return {
               "status": "OK",
               "status_code": 0,
               "data": {
                   "rows": len(rows),
                   'data': [{
                       "product_id": row[0],
                       'product_name': row[1],
                       'category': row[2],
                       'sku': row[3],
                       'price': row[4],
                   } for row in rows]
               }
           }, 200


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
    if type(t[0]) == dict:
        return t
    else:
        index, elements = t

    try:
        cursor.execute("SELECT product_id, product_name, category, sku, price FROM goods "
                       f"ORDER BY product_id LIMIT {elements} OFFSET {index}")
    except psycopg2.errors.NotNullViolation:
        return {"status": "NotNullViolation", "status_code": 3}, 400
    except psycopg2.errors.InvalidTextRepresentation:
        return {"status": "InvalidTextRepresentation", "status_code": 4}, 400
    except psycopg2.errors.UndefinedFunction:
        return {"status": "InvalidTextRepresentation", "status_code": 4}, 400
    except psycopg2.ProgrammingError:
        return {"status": "InvalidTextRepresentation", "status_code": 4}, 400

    rows = cursor.fetchall()
    return {
               "status": "OK",
               "status_code": 0,
               "data": {
                   "rows": len(rows),
                   'data': [{
                       "product_id": row[0],
                       'product_name': row[1],
                       'category': row[2],
                       'sku': row[3],
                       'price': row[4],
                   } for row in rows]
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
    #     'product_id': 123
    # }
    try:
        r = json.loads(request.data)
    except json.JSONDecodeError:
        return {"status": "JSONDecodeError", "status_code": 1}, 400

    if 'sku' not in r and 'product_id' not in r:
        return {"status": "InvalidJSONFormat: sku and id not in json", "status_code": 2}, 400
    elif 'sku' in r and 'product_id' in r:
        return {"status": "InvalidJSONFormat: sku and id in json at the same time", "status_code": 2}, 400

    # sku
    elif 'sku' in r:
        if type(r['sku']) != str and type(r['sku']) != int:
            return {"status": "InvalidJSONFormat: sku is not int or str", "status_code": 2}, 400
        t = elements_index_args_check(r)
        if type(t[0]) == dict:
            return t
        else:
            index, elements = t

        try:
            cursor.execute(f"SELECT COUNT(*) FROM goods WHERE sku = '{r['sku']}'")
            rows = cursor.fetchall()[0][0]
            cursor.execute("SELECT product_id, product_name, category, sku, price FROM goods "
                           f"WHERE sku = '{r['sku']}' ORDER BY product_id "
                           f"LIMIT {elements} OFFSET {index}")
        except psycopg2.errors.NotNullViolation:
            return {"status": "NotNullViolation", "status_code": 3}, 400
        except psycopg2.errors.InvalidTextRepresentation:
            return {"status": "InvalidTextRepresentation", "status_code": 4}, 400
        except psycopg2.errors.UndefinedFunction:
            return {"status": "InvalidTextRepresentation", "status_code": 4}, 400
        except psycopg2.ProgrammingError:
            return {"status": "InvalidTextRepresentation", "status_code": 4}, 400

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
        if not str(r['product_id']).isdigit():
            return {"status": "InvalidJSONFormat: product_id is not digit", "status_code": 2}, 400
        else:
            pid = int(r['product_id'])

        cursor.execute(f"SELECT product_id, product_name, category, sku, price FROM goods WHERE product_id = {pid}")
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
    if type(r['sku']) != str and type(r['sku']) != int:
        return {"status": "InvalidJSONFormat: sku is not int or str", "status_code": 2}, 400
    if type(r['product_name']) != str and r['product_name'] is not None:
        return {"status": "InvalidJSONFormat: product_name is not str", "status_code": 2}, 400
    if type(r['category']) != str and r['category'] is not None:
        return {"status": "InvalidJSONFormat: category is not str", "status_code": 2}, 400
    if type(r['price']) != int:
        return {"status": "InvalidJSONFormat: category is not int", "status_code": 2}, 400

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
    except psycopg2.errors.UndefinedFunction:
        return {"status": "InvalidTextRepresentation", "status_code": 4}, 400
    except psycopg2.ProgrammingError:
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
    lst = []
    j = 0
    for i in r:
        row = add_row(i)
        if row[1] == 400:
            status = 207
        lst.append({
            'data': row[0],
            'HTTP_status_code': row[1]
        })
        j += 1
        if j > max_request_per_batch:
            break
    return {
               "status": "OK",
               "status_code": 0,
               "data": lst
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
    # {
    #     'sku': '1203',
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
    if 'edit_data' not in r:
        return {"status": "InvalidJSONFormat: edit_data not in json", "status_code": 2}, 400
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

    if 'sku' not in r and 'product_id' not in r:
        return {"status": "InvalidJSONFormat: sku and id not in json", "status_code": 2}, 400
    elif 'sku' in r and 'product_id' in r:
        return {"status": "InvalidJSONFormat: sku and id in json at the same time", "status_code": 2}, 400

    if 'sku' in r['edit_data']:
        if type(r['edit_data']['sku']) != str and type(r['edit_data']['sku']) != int:
            return {"status": "InvalidJSONFormat: sku is not int or str", "status_code": 2}, 400
    if 'product_name' in r['edit_data']:
        if type(r['edit_data']['product_name']) != str and r['edit_data']['product_name'] is not None:
            return {"status": "InvalidJSONFormat: product_name is not str", "status_code": 2}, 400
    if 'category' in r['edit_data']:
        if type(r['edit_data']['category']) != str and r['edit_data']['category'] is not None:
            return {"status": "InvalidJSONFormat: category is not str", "status_code": 2}, 400
    if 'price' in r['edit_data']:
        if type(r['edit_data']['price']) != int:
            return {"status": "InvalidJSONFormat: category is not int", "status_code": 2}, 400

    if 'product_id' in r:
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
        except psycopg2.errors.UndefinedFunction:
            return {"status": "InvalidTextRepresentation", "status_code": 4}, 400
        except psycopg2.ProgrammingError:
            return {"status": "InvalidTextRepresentation", "status_code": 4}, 400

        row = cursor.fetchall()[0]
        return {
                   "status": "OK",
                   "status_code": 0,
                   "data": [{
                       "product_id": row[0],
                       'product_name': row[1],
                       'category': row[2],
                       'sku': row[3],
                       'price': row[4],
                   }]
               }, 200
    else:
        try:
            cursor.execute("SELECT COUNT(*) FROM goods WHERE sku = %s;", [r['sku']])
            if cursor.fetchall()[0][0] == 0:
                return {"status": "IdNotInTable", "status_code": 5}, 400
            cursor.execute(f"UPDATE goods SET {', '.join([i + ' = %s' for i in r['edit_data'].keys()])} "
                           "WHERE sku = %s; "
                           "SELECT product_id, product_name, category, sku, price FROM goods WHERE sku = %s;",
                           [*r['edit_data'].values(), r['sku'], r['sku']])
        except psycopg2.errors.NotNullViolation:
            return {"status": "NotNullViolation", "status_code": 3}, 400
        except psycopg2.errors.InvalidTextRepresentation:
            return {"status": "InvalidTextRepresentation", "status_code": 4}, 400
        except psycopg2.errors.UndefinedFunction:
            return {"status": "InvalidTextRepresentation", "status_code": 4}, 400
        except psycopg2.ProgrammingError:
            return {"status": "InvalidTextRepresentation", "status_code": 4}, 400

        return {
                   "status": "OK",
                   "status_code": 0,
                   "data": [{
                       "product_id": row[0],
                       'product_name': row[1],
                       'category': row[2],
                       'sku': row[3],
                       'price': row[4],
                   } for row in cursor.fetchall()]
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
    lst = []
    j = 0
    for i in r:
        row = edit_row(i)
        if row[1] == 400:
            status = 207
        lst.append({
            'data': row[0],
            'HTTP_status_code': row[1]
        })
        j += 1
        if j > max_request_per_batch:
            break
    return {
               "status": "OK",
               "status_code": 0,
               "data": lst
            }, status


@app.route('/goods/element', methods=["DELETE"])
def element_delete():
    # {
    #     'sku': 213
    # }
    # {
    #     'product_id': 123
    # }
    try:
        r = json.loads(request.data)
    except json.JSONDecodeError:
        return {"status": "JSONDecodeError", "status_code": 1}, 400
    return delete_row(r)


def delete_row(r: dict):
    if 'sku' not in r and 'product_id' not in r:
        return {"status": "InvalidJSONFormat: sku and id not in json", "status_code": 2}, 400
    elif 'sku' in r and 'product_id' in r:
        return {"status": "InvalidJSONFormat: sku and id in json at the same time", "status_code": 2}, 400

    # sku
    elif 'sku' in r:
        if type(r['sku']) != str and type(r['sku']) != int:
            return {"status": "InvalidJSONFormat: sku is not int or str", "status_code": 2}, 400
        try:
            cursor.execute(f"SELECT COUNT(*) FROM goods WHERE sku = '{r['sku']}'")
            rows = cursor.fetchall()[0][0]
            cursor.execute(f"DELETE FROM goods WHERE sku = '{r['sku']}'")
        except psycopg2.errors.NotNullViolation:
            return {"status": "NotNullViolation", "status_code": 3}, 400
        except psycopg2.errors.InvalidTextRepresentation:
            return {"status": "InvalidTextRepresentation", "status_code": 4}, 400
        except psycopg2.errors.UndefinedFunction:
            return {"status": "InvalidTextRepresentation", "status_code": 4}, 400
        except psycopg2.ProgrammingError:
            return {"status": "InvalidTextRepresentation", "status_code": 4}, 400

        return {
                   "status": "OK",
                   "status_code": 0,
                   "data": {"deleted_rows": rows}
               }, 200

    # id
    else:
        if not str(r['product_id']).isdigit():
            return {"status": "InvalidJSONFormat: id is not digit", "status_code": 2}, 400
        else:
            pid = int(r['product_id'])

        try:
            cursor.execute(f"SELECT COUNT(*) FROM goods WHERE product_id = {pid}")
            rows = cursor.fetchall()[0][0]
            cursor.execute(f"DELETE FROM goods WHERE product_id = {pid}")
        except psycopg2.errors.NotNullViolation:
            return {"status": "NotNullViolation", "status_code": 3}, 400
        except psycopg2.errors.InvalidTextRepresentation:
            return {"status": "InvalidTextRepresentation", "status_code": 4}, 400
        except psycopg2.errors.UndefinedFunction:
            return {"status": "InvalidTextRepresentation", "status_code": 4}, 400
        except psycopg2.ProgrammingError:
            return {"status": "InvalidTextRepresentation", "status_code": 4}, 400

        return {
                   "status": "OK",
                   "status_code": 0,
                   "data": {"deleted_rows": rows}
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
    lst = []
    j = 0
    for i in r:
        row = delete_row(i)
        if row[1] == 400:
            status = 207
        lst.append({
            'data': row[0],
            'HTTP_status_code': row[1]
        })
        j += 1
        if j > max_request_per_batch:
            break
    return {
               "status": "OK",
               "status_code": 0,
               "data": lst
            }, status


def main():
    from waitress import serve
    serve(app, host="0.0.0.0", port=config["Settings"]["server_port"])


if __name__ == '__main__':
    main()
