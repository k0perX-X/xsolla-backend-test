from flask import Flask, abort
import psycopg2
import sys
from threading import Timer

app = Flask(__name__)
table_name = 'goods'
commit_timer_seconds = 5

conn = psycopg2.connect(dbname='goods', user='postgres',
                        password='', host='localhost')
conn.autocommit = True
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS public.goods (
    product_id bigserial NOT NULL,
    product_name text,
    category text,
    sku text NOT NULL,
    price money NOT NULL,
    PRIMARY KEY (product_id))""")


# cursor.execute("INSERT INTO goods (product_name,category,sku,price) "
#                "VALUES (null, null, '123', 1000.00);")


@app.route('/', methods=["GET"])
def main_page():
    return "Hello world"


def main():
    app.run()


if __name__ == '__main__':
    main()
