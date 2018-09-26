"""

Creates plots of value and average price

"""

import plotly.plotly as py
import json

def parse_file(file_name):
    """ Parses .json file into argument dictionaries, return dict with lists of arguments """
    json_data = open(file_name)

    # Define argument lists for json.load
    def arg_to_lists(list_of_dict: object) -> object:
        ts = list(map(lambda obj: float(obj["ts"]), list_of_dict))
        volume = list(map(lambda obj: float(obj["volume"]), list_of_dict))
        av_price = list(map(lambda obj: float(obj["price"]), list_of_dict))
        return dict(zip(["time_stamp", "volume", "average_price"], [ts, volume, av_price]))

    try:
        args = json.load(json_data)
        return arg_to_lists(args)
    except:
        print('Error: incorrect structure of JSON file')
        return False




json_data1 = parse_file("TKN0_TKN88.json")
print(json_data1["average_price"])
