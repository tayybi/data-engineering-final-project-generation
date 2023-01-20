import csv
import datetime
import io
import json
import os

import boto3
import pandas as pd
import psycopg2
import psycopg2.extras as extras

s3 = boto3.client('s3')


def lambda_handler(event, context):
    # getting bucket and file name
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # get object
    response = s3.get_object(Bucket=bucket, Key=key)

    user = os.environ.get(r'user')
    password = os.environ.get(r'password')
    host = os.environ.get(r'host')
    port = os.environ.get(r'port')
    dbname = os.environ.get(r'dbname')

    mydb = psycopg2.connect(
        dbname=dbname, user=user, password=password, host=host, port=port
    )

    print('Successful Connection')

    cursor = mydb.cursor()

    def read_file(response):
        if is_csv(key) == True:
            try:
                content = pd.read_csv(response['Body'], sep=',', header=None)
                if content.empty:
                    print('File is empty. Please try uploading another file.')
                else:
                    content.columns = [
                        'date_time',
                        'branch',
                        'name',
                        'items',
                        'balance',
                        'payment_method',
                        'card_details',
                    ]

                    content = content.drop(['name', 'card_details'], axis=1)
                    return content
            except FileNotFoundError:
                print(
                    'Error: File not found in src directory. Please move your file to the src directory.'
                )
        else:
            print(
                "Error: Incompatible file type. Please upload a '.csv' file."
            )

    def is_csv(key):
        return key.endswith('.csv')

    main_file = read_file(response)

    def get_transformed_data():
        formatted_date_time = []
        order_prices = []
        order_names = []

        i = 0
        for value in main_file['items']:
            order_list = str(value).split(', ')
            for product in order_list:
                order_names.append(product[:-7])
                order_prices.append(float(product[-4:]))
            main_file.at[i, 'items'] = order_list
            i += 1

        data1 = main_file.explode('items')
        data1['items'] = order_names
        data1['product_price'] = order_prices
        data1['transaction_id'] = data1.index

        for value in data1['date_time']:
            converted_date_time = datetime.datetime.strptime(
                value, '%d/%m/%Y %H:%M'
            ).strftime('%Y-%m-%d %H:%M')
            formatted_date_time.append(converted_date_time)

        data1['date_time'] = formatted_date_time

        adjusted_transition_id = []
        for transaction in data1['transaction_id']:
            adjusted_transition_id.append(transaction + 1)

        data1['transaction_id'] = adjusted_transition_id

        data_to_load = {
            'order_name': order_names,
            'order_price': order_prices,
            'date_time': data1['date_time'],
            'branch_name': data1['branch'],
            'payment_amount': data1['balance'],
            'payment_method': data1['payment_method'],
            'transaction_id': data1['transaction_id'],
        }

        return pd.DataFrame(data_to_load)

    def transform_products_file():
        prod_name = []
        prod_price = []
        prod_size = []
        for key, value in products.items():
            prod_name.append(key)
            price = value[0]
            prod_size.append('Regular')
            prod_price.append(price)
            prod_name.append(key)
            price = value[1]
            prod_price.append(price)
            prod_size.append('Large')

        df = pd.DataFrame()

        df['name'] = prod_name
        df['price'] = prod_price
        df['size'] = prod_size

        product_info = {
            'product_name': prod_name,
            'product_price': prod_price,
            'product_size': prod_size,
        }
        return pd.DataFrame(product_info)

    products = {
        'Latte': [2.15, 2.45],
        'Flavoured latte - Vanilla': [2.55, 2.85],
        'Flavoured latte - Caramel': [2.55, 2.85],
        'Flavoured latte - Hazelnut': [2.55, 2.85],
        'Flavoured latte - Gingerbread': [2.55, 2.85],
        'Cappuccino': [2.15, 2.45],
        'Americano': [1.95, 2.25],
        'Flat white': [2.15, 2.45],
        'Cortado': [2.05, 2.35],
        'Mocha': [2.30, 2.70],
        'Espresso': [1.50, 1.80],
        'Filter coffee': [1.50, 1.80],
        'Chai latte': [2.30, 2.60],
        'Hot chocolate': [2.20, 2.90],
        'Flavoured hot chocolate - Caramel': [2.60, 2.90],
        'Flavoured hot chocolate - Hazelnut': [2.60, 2.90],
        'Flavoured hot chocolate - Vanilla': [2.60, 2.90],
        'Luxury hot chocolate': [2.40, 2.70],
        'Red Label tea': [1.20, 1.80],
        'Speciality Tea - Earl Grey': [1.30, 1.60],
        'Speciality Tea - Green': [1.30, 1.60],
        'Speciality Tea - Camomile': [1.30, 1.60],
        'Speciality Tea - Peppermint': [1.30, 1.60],
        'Speciality Tea - Fruit': [1.30, 1.60],
        'Speciality Tea - Darjeeling': [1.30, 1.60],
        'Speciality Tea - English breakfast': [1.30, 1.60],
        'Iced latte': [2.35, 2.85],
        'Flavoured iced latte - Vanilla': [2.75, 3.25],
        'Flavoured iced latte - Caramel': [2.75, 3.25],
        'Flavoured iced latte - Hazelnut': [2.75, 3.25],
        'Iced americano': [2.15, 2.50],
        'Frappes - Chocolate Cookie': [2.75, 3.25],
        'Frappes - Strawberries & Cream': [2.75, 3.25],
        'Frappes - Coffee': [2.75, 3.25],
        'Smoothies - Carrot Kick': [2.00, 2.50],
        'Smoothies - Berry Beautiful': [2.00, 2.50],
        'Smoothies - Glowing Greens': [2.00, 2.50],
        'Hot Chocolate': [1.40, 1.70],
        'Glass of milk': [0.70, 1.10],
    }

    def transform_branch_info():
        df = pd.DataFrame()
        df['branch_name'] = main_file['branch']
        transformed_branch_data = df.iloc[:1]
        return transformed_branch_data

    def execute_values(mydb, df, table):
        tuples = [tuple(x) for x in df.to_numpy()]

        cols = ','.join(list(df.columns))

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

    df = get_transformed_data()
    df1 = df[['date_time', 'payment_amount', 'payment_method']]

    df2 = df[['order_name', 'order_price', 'transaction_id']]

    product_data = transform_products_file()
    df3 = product_data[['product_name', 'product_price', 'product_size']]

    branch_data = transform_branch_info()
    df4 = branch_data[['branch_name']]
    branch_name = df4.to_numpy()[0][0]

    cursor.execute('SELECT * FROM public.Branch;')
    branches = cursor.fetchall()
    branch_list = [branches[index][1] for index, item in enumerate(branches)]

    if branch_name not in branch_list:
        execute_values(mydb, df4, 'public.Branch')
    else:
        print(
            'Branch already in database. Skipping adding branch data to branch table.'
        )

    branch_id_retrieval_query = cursor.execute(
        'SELECT * FROM public.Branch where branch_name = (%s);', (branch_name,)
    )
    result = cursor.fetchone()
    df1_copy = df1.copy()
    df1_copy['branch_id'] = result[0]

    execute_values(mydb, df1_copy, 'public.Transactions')
    execute_values(mydb, df2, 'public.Orders')
    execute_values(mydb, df3, 'public.Products')

    mydb.commit()
    mydb.close()
