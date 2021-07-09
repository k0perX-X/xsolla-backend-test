from flask import Flask, abort, request
import psycopg2
import json
import logging

app = Flask(__name__)
table_name = 'goods'
commit_timer_seconds = 5
max_elements_per_request = 2000
logging.basicConfig(filename="/var/lib/postgresql/data/log.txt", level=logging.DEBUG)

conn = psycopg2.connect(dbname='goods', user='postgres',
                        password='', host='localhost')
conn.autocommit = True
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS public.goods (
    product_id bigserial NOT NULL,
    product_name text,
    category text,
    sku text NOT NULL,
    price real NOT NULL,
    PRIMARY KEY (product_id));""")


def elements_index_args_check(args) -> tuple:
    logging.debug(str(args))
    if 'index' not in args or 'elements' not in args:
        return tuple(abort(400))

    if not args.get('index').isdigit():
        return tuple(abort(400))
    else:
        index = int(args.get('index'))

    if not args.get('elements').isdigit():
        return tuple(abort(400))
    else:
        elements = int(args.get('elements'))
    if elements > max_elements_per_request:
        return tuple(abort(400))

    return index, elements


@app.route('/goods/catalog', methods=["GET"])
def catalog():
    t = elements_index_args_check(request.args)
    if len(t) == 1:
        return t[0]
    else:
        index, elements = t

    cursor.execute("SELECT COUNT(*) FROM public.goods")
    lines_in_table = cursor.fetchall()[0][0]
    cursor.execute("SELECT product_id, product_name, category, sku, price FROM public.goods "
                   f"ORDER BY product_id ASC LIMIT {elements} OFFSET {index}")
    data = {
        "lines_in_table": lines_in_table,
        'data': [{
            "product_id": row[0],
            'product_name': row[1],
            'category': row[2],
            'sku': row[3],
            'price': row[4],
        } for row in cursor.fetchall()]
    }
    return data


@app.route('/goods/element', methods=["GET"])
def element_get():
    if 'sku' not in request.args and 'id' not in request.args:
        return abort(400)
    elif 'sku' in request.args and 'id' in request.args:
        return abort(400)

    # sku
    elif 'sku' not in request.args:

        if not request.args.get('sku').isdigit():
            return abort(400)
        else:
            sku = int(request.args.get('sku'))

        t = elements_index_args_check(request.args)
        if len(t) == 1:
            return t[0]
        else:
            index, elements = t

        cursor.execute("SELECT product_id, product_name, category, sku, price FROM public.goods "
                       f"WHERE sku == {sku} ORDER BY product_id ASC"
                       f"ORDER BY product_id ASC LIMIT {elements} OFFSET {index}")
        data = {
            'data': [{
                "product_id": row[0],
                'product_name': row[1],
                'category': row[2],
                'sku': row[3],
                'price': row[4],
            } for row in cursor.fetchall()]
        }
        return data

    # id
    else:
        if not request.args.get('id').isdigit():
            return abort(400)
        else:
            id = int(request.args.get('id'))

        cursor.execute("SELECT product_id, product_name, category, sku, price FROM public.goods "
                       f"WHERE product_id == {id} ORDER BY product_id ASC")
        data = {
            'data': [{
                "product_id": row[0],
                'product_name': row[1],
                'category': row[2],
                'sku': row[3],
                'price': row[4],
            } for row in cursor.fetchall()]
        }
        return data


@app.route('/goods/element', methods=["POST"])
def element_post():
    try:
        r = json.loads(request.data)
    except json.JSONDecodeError:
        return abort(400)

    if 'product_name' not in r or 'category' not in r or 'sku' not in r or 'price' not in r:
        return abort(400)

    try:
        cursor.execute("INSERT INTO goods (product_name,category,sku,price) "
                       "VALUES (%s, %s, %s, %s);", [r['product_name'], r['category'], r['sku'], r['price']])
    except psycopg2.errors.NotNullViolation:
        return abort(400)
    except psycopg2.errors.InvalidTextRepresentation:
        return abort(400)

    return "OK"  # TODO выводить получившуюся строку


def main():
    app.run()


if __name__ == '__main__':
    main()
