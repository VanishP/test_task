"""

Creates plots of value and average price

"""

import sys
import argparse
import json

def parse_file(file):
    """ Parses .json file into argument dictionaries, return dict with lists of arguments """

    # Define argument lists for json.load
    def arg_to_lists(list_of_dict: object) -> object:
        ts = list(map(lambda obj: float(obj["ts"]), list_of_dict))
        volume = list(map(lambda obj: float(obj["volume"]), list_of_dict))
        av_price = list(map(lambda obj: float(obj["price"]), list_of_dict))
        return dict(zip(["time_stamp", "volume", "average_price"], [ts, volume, av_price]))

    try:
        args = json.load(file)
        return arg_to_lists(args)
    except:
        print('Error: incorrect structure of JSON file')
        sys.exit(1)

def parser_cl_args():
    """ Parses arguments from command line, return required arguments"""
    if len(sys.argv) == 10 and sys.argv[1] == "create":
        cl_arg =  parse_create_mode_cl_args()
    elif len(sys.argv) == 9 and sys.argv[1] == "append":
        cl_arg = parse_append_mode_cl_args()
    else:
        print("Error: incorrect arguments or their count")
        sys.exit(1)
    return cl_arg

def parse_create_mode_cl_args():
    """ Return required arguments for create mode"""
    pars = argparse.ArgumentParser()
    pars.add_argument("mode")
    pars.add_argument("data_file", type=argparse.FileType())
    pars.add_argument("--interval", type=int)
    pars.add_argument("--output", type=str)
    pars.add_argument("--period", nargs=2, type=float)
    cl_arg =  pars.parse_args()
    return cl_arg

def parse_append_mode_cl_args():
    """" Return required arguments for create mode"""
    pars = argparse.ArgumentParser()
    pars.add_argument("mode")
    pars.add_argument("old_file", type=argparse.FileType())
    pars.add_argument("new_file", type=argparse.FileType())
    pars.add_argument("--output", type=str)
    pars.add_argument("--period", nargs=2, type=float)
    cl_arg = pars.parse_args()
    return cl_arg





