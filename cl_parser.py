"""

Module with command line parser function and UserError class

"""

import argparse
from typing import  ClassVar, List, Tuple
import sys
import datetime


class UserError(Exception):
    def __init__(self,error_text:str="error"):
        self.msg = error_text


def parse_cl_args() -> ClassVar:
    """
    Parses arguments from command line, return required arguments
    """
    pars = add_arguments()
    cl_arg =  pars.parse_args()
    if check_cl_args(cl_arg):
        cl_arg.period = None
    return cl_arg

def add_arguments():
    """
    Adds command line arguments
    """
    pars = argparse.ArgumentParser()
    pars.add_argument("mode", type=str,
                      help="mode of create plots: create, append")
    pars.add_argument("file", type=argparse.FileType(),
                      help="""name of old .json data file in append mode
                                and .json data file in create mode""")
    pars.add_argument("--new_file", type=argparse.FileType(),
                      help="""name of new .json data file in append mode
                          and .json data file in create mode""")
    pars.add_argument("--interval", nargs=2, type=int, required=True,
                      help="""interval for ticks on axis of 2 arguments:
                                 first argument:
                                 0-sec,
                                 1-min,
                                 2-hour,
                                 3-day,
                                 4-week,
                                 second argument - length of interval""")
    pars.add_argument("--output", type=str, required=True,
                      help="name of output file")
    pars.add_argument("--period", nargs=4, type=str,
                      help="""time period for build plots in
                               ISO 8601 format (YYYY-MM-DDT HH:MM:SS.mmmmmm""")
    return pars

def check_cl_args(cl_arg:ClassVar) -> bool:
    """
    Checks command line arguments
    """
    check_mode_arg(cl_arg)
    if cl_arg.mode == "create":
         check_create_arg(cl_arg)
    if cl_arg.mode == "append":
        check_append_arg(cl_arg)
    check_interval_arg(cl_arg)
    if cl_arg.period is not None:
        return check_period_argument(cl_arg)
    return True

def check_mode_arg(cl_arg:ClassVar):
    """
    Checks mode arguments
    """
    try:
        if cl_arg.mode not in ["create", "append"]:
            raise UserError("Error: arg mode is incorrect ")
    except UserError as err:
        print(err.msg)
        sys.exit(1)

def check_create_arg(cl_arg:ClassVar):
    """
    Checks existence excess command line argument(--new_file)
    """
    try:
        if cl_arg.mode == "create" and cl_arg.new_file  is not None:
            raise UserError("Error: arg new_file isn't required in this mode ")
    except UserError as err:
        print(err.msg)
        sys.exit(1)

def check_append_arg(cl_arg: ClassVar):
    """
    Checks existence append command line argument(--new_file)
    """
    try:
        if cl_arg.mode == "append" and cl_arg.new_file is None:
            raise UserError("Error: arg new_file are required in this mode ")
    except UserError as err:
        print(err.msg)
        sys.exit(1)

def check_interval_arg(cl_arg: ClassVar):
    """
    Checks interval argument(--interval)
    """
    try:
        if cl_arg.interval[0] not in [0, 1, 2, 3, 4]:
            raise UserError("Error: incorrect interval time index")
    except UserError as err:
        print(err.msg)
        sys.exit(1)

def check_period_argument(cl_arg: ClassVar):
    """
    Checks period command line argument(--period)
    """
    fmt = "%Y-%m-%d %H:%M:%S.%f"
    try:
        p1 = cl_arg.period[0] + " " + cl_arg.period[1]
        p2 = cl_arg.period[2] + " " + cl_arg.period[3]
        if  (datetime.datetime.strptime(p1,fmt) >
             datetime.datetime.strptime(p2,fmt)):
            raise UserError("Error: incorrect period")
    except UserError as err:
        print(err.msg)
        return True
    except TypeError:
        print("Empty period or incorrect period")
        return True
    return False

def check_period_correct(period: List[str], data_frame: ClassVar,
                         data_file: ClassVar) -> Tuple:
    """
    Check contain period date with data or not
    """
    fmt = "%Y-%m-%d %H:%M:%S.%f"
    p0 = datetime.datetime.strptime(period[0] + " " + period[1], fmt)
    p1 = datetime.datetime.strptime(period[2] + " " + period[3], fmt)
    length = data_frame.shape[0] - 1
    try:
        if p0.timestamp() > data_frame.values[length, 0]\
                or p1.timestamp() < data_frame.values[0, 0]:
           raise UserError("Error: this period doesn't contain any values")
    except UserError as err:
        print(err.msg)
        if data_file is not None:
            data_file.unlink()
        sys.exit(1)
    return p0, p1