import datetime

import pandas as pd
import hashlib

import extract
import products_collection as products

main_file = extract.read_file(r'src\chesterfield.csv')

                    # 'date_time',
                    # 'branch',
                    # 'name',
                    # 'items',
                    # 'balance',
                    # 'payment_method',
                    # 'card_details',

def df_transection(file):
    formatted_date_time = []
    #formating the date and time
    for value in file['date_time']:
        converted_date_time = datetime.datetime.strptime(
            value, '%d/%m/%Y %H:%M'
        ).strftime('%Y-%m-%d %H:%M')
        formatted_date_time.append(converted_date_time)
    file['date_time'] = formatted_date_time
    # makeing the unique transection id
    file['transaction_id'] = (file['branch'] + file['date_time']).apply(lambda x: hashlib.sha1(x.encode()).hexdigest())
    #return new datafrmae for transection table
    data_to_load = {
        'date_time': file['date_time'],
        'branch_name': file['branch'],
        'payment_amount': file['balance'],
        'payment_method': file['payment_method'],
        'transaction_id': file['transaction_id'],
    }
    return pd.DataFrame(data_to_load)


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
        'branch_id': 1,
    }

    return pd.DataFrame(data_to_load)


def transform_products_file():
    prod_name = []
    prod_price = []
    prod_size = []
    for key, value in products.drinks.items():
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


def transform_branch_info():
    df = pd.DataFrame()
    df['branch_name'] = main_file['branch']
    transformed_branch_data = df.iloc[:1]
    return transformed_branch_data

print(df_transection(main_file))