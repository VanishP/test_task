"""

Creates plots of value and average price

"""

import sys
from math import pi
import argparse
import json
import shutil
from typing import Dict, List, io, ClassVar

import datetime

import pathlib

import bokeh.layouts as layouts
from bokeh.io import output_file, show
from bokeh.models import FixedTicker
from bokeh.plotting import figure
import pandas as pd
import numpy as np


class UserError(Exception):
    def __init__(self,error_text:str="error"):
        self.msg = error_text




def parse_file(json_file: io) -> Dict[str, List]:
    """
    Parses .json file into argument dictionaries,
    return dict with lists of arguments
    """
    args = json.load(json_file)
    json_file.close()
    return create_data_dict(args)

def create_data_dict(json_data: List[Dict]) -> ClassVar:
    """
    Creates dictionary with data lists: timestamps, date, volume and price
    """
    json_data = np.array(list(map(lambda obj:
                    [[datetime.datetime.fromtimestamp(float(obj["ts"])),
                      float(obj["ts"]),
                      float(obj["volume"]),
                      float(obj["price"])]],json_data))).T
    data_frame = pd.DataFrame(dict(zip(["date", "time_stamp", "volume",
                                        "average_price"],
                                        [json_data[0].tolist()[0],
                                         json_data[1].tolist()[0],
                                         json_data[2].tolist()[0],
                                         json_data[3].tolist()[0]])))
    return data_frame


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
    check_excess_create_arg(cl_arg)
    check_excess_create_arg(cl_arg)
    check_interval_arg(cl_arg)
    if cl_arg is not None:
        return check_period_argument(cl_arg)
    return True

def check_excess_create_arg(cl_arg:ClassVar):
    """
    Checks existence excess command line argument(--new_file)
    """
    try:
        if cl_arg.mode == "create" and cl_arg.new_file  is not None:
            raise UserError("Error: arg new_file isn't required in this mode ")
    except UserError as err:
        print(err.msg)
        sys.exit(1)

def check_append_arg(cl_arg:ClassVar):
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


def manage_visualizer(cl_arg: ClassVar):
    """
    Creates files with plots and data in selected mode(create, append) and
    records data and plots in dir.
    """
    time_delta = [
             datetime.timedelta(seconds=cl_arg.interval[1]),
             datetime.timedelta(minutes=cl_arg.interval[1]),
             datetime.timedelta(hours=cl_arg.interval[1]),
             datetime.timedelta(days=cl_arg.interval[1]),
             datetime.timedelta(weeks=cl_arg.interval[1])
             ]
    print(cl_arg.mode)

    if cl_arg.mode == "create":
        data_frame = parse_file(cl_arg.file)
        data_frame = data_frame.sort_values(by="date")
        if cl_arg.period is not None:
            data_for_plots = choise_date_in_period(cl_arg.period,
                                                   data_frame)
        else:
            data_for_plots = data_frame
        plots = create_plots(data_for_plots, time_delta[cl_arg.interval[0]])
        record_in_dir(cl_arg.file, cl_arg.output, plots)

    else:
        data_file = create_union_data_file(cl_arg)
        out_data = open(data_file, "r")
        data_frame = parse_file(out_data)
        data_frame = data_frame.sort_values(by="date")
        if cl_arg.period is not None:
            data_for_plots = choise_date_in_period(cl_arg.period,
                                                   data_frame, data_file)
        else:
            data_for_plots = data_frame
        plots = create_plots(data_for_plots, time_delta[cl_arg.interval[0]])
        record_in_dir(out_data, cl_arg.output, plots)
        data_file.unlink()

def create_union_data_file(cl_arg: ClassVar) -> ClassVar:
    """ Create .json file including union of other .json files"""
    data_file = pathlib.Path.cwd() / (cl_arg.output + "_data.json")
    out_data = open(data_file, "w")
    data2 = cl_arg.new_file.read()
    data2 = data2[:-1] + ","
    cl_arg.new_file.close()
    out_data.write(data2)
    data1 = cl_arg.file.read()
    data1 = data1[1:]
    cl_arg.file.close()
    out_data.write(data1)
    out_data.close()
    return data_file

def choise_date_in_period(period: List[str],
                          data_frame: ClassVar,
                          data_file: ClassVar=None) -> ClassVar:
    """ Filter data by period"""
    fmt = "%Y-%m-%d %H:%M:%S.%f"
    p0 = datetime.datetime.strptime(period[0] + " " + period[1],fmt)
    p1 = datetime.datetime.strptime(period[2] + " " + period[3],fmt)
    length = data_frame.shape[0]-1
    try:
        if p0 > data_frame.values[length, 0] or p1 < data_frame.values[0, 0]:
           raise UserError("Error: this period doesn't contain any values")
    except UserError as err:
        print(err.msg)
        if data_file is not None:
            data_file.unlink()
        sys.exit(1)
    data_frame = data_frame.loc[data_frame["date"] >= p0]
    data_frame = data_frame.loc[data_frame["date"] <= p1]
    return data_frame

def record_in_dir(data_file: io, output: str, plots: ClassVar):
    """ Records in dir plots and data"""
    directory = pathlib.Path.cwd()/(output + "_dir")
    directory.mkdir(parents=True)
    output_file(directory/(output + ".html"))
    show(plots)
    shutil.copyfile(data_file.name, directory/(output + "_data.json"))
    data_file.close()



def create_plots(data_frame: ClassVar, time_delta: ClassVar) -> ClassVar:
    """ Create plots of volume and average price """
    ticks_dict = define_ticks(data_frame, time_delta)

    # Create Volume plot
    volume = sum_volume(data_frame["volume"].values)
    plot1 = plotting(data_frame["time_stamp"].values,
                     volume, ticks_dict, "Volume")

    # Create Average Price plot
    plot2 = plotting(data_frame["time_stamp"].values,
                     data_frame["average_price"].values,
                     ticks_dict, "Average price")
    return layouts.column([plot1, plot2])

def plotting(x: ClassVar, y: ClassVar,
             ticks_dict: Dict, name: str="f(x)") -> ClassVar:
    """ Plotting the graph"""
    plot = figure(title=name + " plot", x_axis_label="time stamp",
                   y_axis_label=name, plot_width=1000)
    plot.line(x, y)
    plot.yaxis.major_label_orientation = "vertical"
    plot.xaxis.ticker = FixedTicker(ticks=list(ticks_dict.keys()))
    plot.xaxis.major_label_overrides = ticks_dict
    plot.xaxis.major_label_orientation = pi / 3
    return plot

def sum_volume(volume: ClassVar) -> ClassVar:
    """ Calculate  volume values since first date"""
    for i in range(volume.size)[1:]:
        volume[i] += volume[i - 1]
    return volume



def define_ticks(data_frame: ClassVar,
                 time_delta: ClassVar) -> Dict[int, str]:
    """ Define ticks on xaxis according with interval argument"""
    first_date = data_frame.values[0, 0]
    last_date = data_frame.values[data_frame.shape[0] - 1, 0]
    date_tick = first_date
    ticks_date = [first_date - time_delta, first_date]
    while date_tick <= last_date:
        date_tick += time_delta
        ticks_date.append(date_tick)

    ticks = list(map(lambda x: x.timestamp(), ticks_date))
    ticks_date = list(map(lambda x: x.strftime("%d %b %Y %T"), ticks_date))
    ticks_dict = dict(zip(ticks, ticks_date))
    return ticks_dict

if __name__ == '__main__':
    cl_arg = parse_cl_args()
    manage_visualizer(cl_arg)
