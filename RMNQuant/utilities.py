"""Module containing extra tools"""
import pathlib as pl

import pandas as pd

def read_data(path, excel_sheet=0):
    """Function to read incoming data"""

    datapath = pl.Path(path)

    if datapath.suffix == ".csv":

        try:
            data = pd.read_csv(datapath, sep = ";", engine='python')
            data.columns[1]

        except IndexError:
            try:
                data = pd.read_csv(datapath, sep="\t")
                data.columns[1]

            except IndexError:
                raise TypeError("csv file must have ';' or tabulated separator")

    elif datapath.suffix == ".xlsx":

        data = pd.read_excel(datapath, engine="openpyxl", sheet_name=excel_sheet)

    elif datapath.suffix == ".txt":
        data = None
        pass #To be implemented later

    else:
        raise TypeError("File extension not supported." 
                        "Supported types: '.csv', '.xlsx', '.txt' ")

    return data

def is_empty(any_structure):
    """Check if container is empty

    :param any_structure: data container to analyze
    :return: if empty True, if not False
    """

    if any_structure:

        return False

    else:

        return True

def check_for_sum(y):
    """Check if two args given in y through '+' operator

    :param y:
    """

    x = [i for i in y.split('+')]

    return x

def append_value(dict_obj, key, value):
    """Add/append values to an existing key to a
    dictionary"""

    # Check if key exist in dict or not
    if key in dict_obj:
        # Key exist in dict.
        # Check if type of value of key is list or not
        if not isinstance(dict_obj[key], list):
            # If type is not list then make it list
            dict_obj[key] = [dict_obj[key]]
        # Append the value in list
        dict_obj[key].append(value)
    else:
        # As key is not in dict,
        # so, add key-value pair
        dict_obj[key] = value

        return dict_obj
