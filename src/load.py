import datetime

import numpy
import pandas as pd
import psycopg2
import psycopg2.extras as extras

import transform

mydb = psycopg2.connect(
    user='postgres',
    password='pass',
    port=5455,
    host='localhost',  # localhost: long string in SSM
)
print('Successful Connection')


cur = mydb.cursor()

cur.execute(
    """CREATE TABLE IF NOT EXISTS Branch
    (branch_id SERIAL PRIMARY KEY,
    branch_name TEXT
    );"""
)

cur.execute(
    """CREATE TABLE IF NOT EXISTS Transactions
    (transaction_id SERIAL PRIMARY KEY,
    date_time TIMESTAMP,
    branch_id INT,
    payment_amount FLOAT NOT NULL,
    payment_method TEXT,
    FOREIGN KEY (branch_id)
    REFERENCES Branch(branch_id));"""
)

cur.execute(
    """CREATE TABLE IF NOT EXISTS Orders
    (order_id SERIAL PRIMARY KEY,
    order_name TEXT,
    order_price FLOAT NOT NULL,
    transaction_id INT,
    FOREIGN KEY (transaction_id)
    REFERENCES Transactions(transaction_id)
    );"""
)

cur.execute(
    """CREATE TABLE IF NOT EXISTS Products
    (product_id SERIAL PRIMARY KEY,
    product_name TEXT,
    product_price FLOAT NOT NULL,
    product_size TEXT
    );"""
)


def execute_values(mydb, df, table):
    tuples = [tuple(x) for x in df.to_numpy()]

    cols = ','.join(list(df.columns))

    # SQL query to execute
    query = 'INSERT INTO %s(%s) VALUES %%s' % (table, cols)
    cursor = mydb.cursor()
    try:
        extras.execute_values(cursor, query, tuples)
        mydb.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print('Error: %s' % error)
        mydb.rollback()
        cursor.close()
        return 1
    print('The execute_values command has been completed successfully')
    cursor.close()


df = transform.get_transformed_data()
df1 = df[['date_time', 'payment_amount', 'payment_method', 'branch_id']]
df2 = df[['order_name', 'order_price', 'transaction_id']]

product_data = transform.transform_products_file()
df3 = product_data[['product_name', 'product_price', 'product_size']]

branch_data = transform.transform_branch_info()
df4 = branch_data[['branch_name']]


execute_values(mydb, df4, 'Branch')
execute_values(mydb, df1, 'Transactions')
execute_values(mydb, df2, 'Orders')
execute_values(mydb, df3, 'Products')

query = """UPDATE Transactions
SET branch_id=(SELECT branch_id FROM Branch where Branch.branch_name = '%s');""" % (
    (df4.to_numpy()[0][0])
)

cur.execute(query)
cur.close

mydb.commit()
mydb.close()
