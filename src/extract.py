import os

import pandas as pd


def read_file(filename):
    if is_csv(filename) == True:
        try:
            content = pd.read_csv(filename, header=None)
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
        print("Error: Incompatible file type. Please upload a '.csv' file.")


def is_csv(filename):
    extension = os.path.splitext(filename)[1]
    if extension == '.csv':
        return True
    else:
        False
