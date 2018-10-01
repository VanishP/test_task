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
from bokeh.models.formatters import FuncTickFormatter
from bokeh.plotting import figure
import pandas as pd


class MyError(Exception):
    def __init__(self,error_text:str="error"):
        self.msg = error_text




def parse_file(json_file: io) -> Dict[str, List]:
    """
    Parses .json file into argument dictionaries,
    return dict with lists of arguments
    """
    print("in parse_file")

    # Define dict of argument lists for json.load
    def data_to_lists(list_of_dict: List[Dict]) -> Dict[str, List]:
        ts = list(map(lambda obj: float(obj["ts"]), list_of_dict))
        date = list(map(lambda obj:
                        datetime.datetime.fromtimestamp(float(obj["ts"])),
                        list_of_dict))
        volume = list(map(lambda obj: float(obj["volume"]), list_of_dict))
        av_price = list(map(lambda obj: float(obj["price"]), list_of_dict))
        return dict(zip(["date", "time_stamp", "volume", "average_price"],
                        [date, ts, volume, av_price]))

    args = json.load(json_file)
    json_file.close()
    return data_to_lists(args)



def parser_cl_args() -> ClassVar:
    """ Parses arguments from command line, return required arguments"""
    print("in parser_cl_args")
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
                           ISO 8601 format (YYYY-MM-DDTHH:MM:SS.mmmmmm""")


    cl_arg =  pars.parse_args()
    try:
        if cl_arg.mode == "create" and cl_arg.new_file  is not None:
            raise MyError("Error: arg new_file isn't required in this mode ")
    except MyError as err:
        print(err.msg)
        sys.exit(1)
    try:
        if cl_arg.mode == "append" and cl_arg.new_file is None:
            raise MyError("Error: arg new_file are required in this mode ")
    except MyError as err:
        print(err.msg)
        sys.exit(1)
    try:
        if cl_arg.interval[0] not in [1, 2, 3, 4, 5]:
            raise MyError("Error: incorrect interval time index")
    except MyError as err:
        print(err.msg)
        sys.exit(1)
    fmt = "%Y-%m-%d %H:%M:%S.%f"
    p1 = cl_arg.period[0] + " " + cl_arg.period[1]
    p2 = cl_arg.period[2] + " " + cl_arg.period[3]
    try:
        if  (datetime.datetime.strptime(p1,fmt) >
             datetime.datetime.strptime(p2,fmt)):
            raise MyError("Error: incorrect period")
    except MyError as err:
        print(err.msg)
        cl_arg.period = None
    return cl_arg


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
    print("in manage_visualizer")

    if cl_arg.mode == "create":
        data_frame = pd.DataFrame(parse_file(cl_arg.file))
        data_frame = data_frame.sort_values(by="date")
        if cl_arg.period is not None:
            data_for_plots = choise_date_in_period(cl_arg.period,
                                                   data_frame)
        else:
            data_for_plots = data_frame
        plots = create_plots(data_for_plots, time_delta[cl_arg.interval[0]])
        record_in_dir(cl_arg.file, cl_arg.output, plots)

    else:
        data_file = pathlib.Path.cwd() / (cl_arg.output + "_data.json")
        out_data = open(cl_arg.output + "_data.json", "w")
        data2 = cl_arg.new_file.read()
        data2 = data2[:-1] + ","
        cl_arg.new_file.close()
        out_data.write(data2)
        data1 = cl_arg.file.read()
        data1 = data1[1:]
        cl_arg.file.close()
        out_data.write(data1)
        out_data.close()
        out_data = open(cl_arg.output + "_data.json", "r")
        data_frame = pd.DataFrame(parse_file(out_data))
        data_frame = data_frame.sort_values(by="date")
        if cl_arg.period is not None:
            data_for_plots = choise_date_in_period(cl_arg.period,
                                                   data_frame, data_file)
        else:
            data_for_plots = data_frame
        plots = create_plots(data_for_plots, time_delta[cl_arg.interval[0]])
        record_in_dir(out_data, cl_arg.output, plots)
        data_file.unlink()


def choise_date_in_period(period: List[str],
                          data_frame: ClassVar,
                          data_file: ClassVar=None) -> ClassVar:
    """ Filter data by period"""
    print("in choise_date_in_period")
    fmt = "%Y-%m-%d %H:%M:%S.%f"
    p0 = datetime.datetime.strptime(period[0] + " " + period[1],fmt)
    p1 = datetime.datetime.strptime(period[2] + " " + period[3],fmt)
    length = data_frame.shape[0]-1
    try:
        if p0 > data_frame.values[length, 0] or p1 < data_frame.values[0, 0]:
           raise MyError("Error: this period doesn't contain any values")
    except MyError as err:
        print(err.msg)
        data_file.unlink()
        sys.exit(1)
    data_frame = data_frame.loc[data_frame["date"] >= p0]
    data_frame = data_frame.loc[data_frame["date"] <= p1]
    return data_frame

def record_in_dir(data_file: io, output: str, plots: ClassVar):
    """ Records in dir plots and data"""
    print("in record_in_dir")
    directory = pathlib.Path.cwd()/(output + "_dir")
    directory.mkdir(parents=True)
    output_file(directory/(output + ".html"))
    show(plots)
    shutil.copyfile(data_file.name, directory/(output + "_data.json"))
    data_file.close()


def create_plots(data_frame: ClassVar, time_delta: ClassVar) -> ClassVar:
    """ Create plots of volume and average price """
    print("in create_plots")
    print(time_delta)
    first_date = data_frame.values[0,0]
    last_date = data_frame.values[data_frame.shape[0] - 1, 0]
    date_tick = first_date
    ticks_date = [first_date - time_delta, first_date]
    print("f d=", first_date)
    print("l d=", last_date)
    while date_tick <= last_date:
        date_tick += time_delta
        ticks_date.append(date_tick)

    ticks = list(map(lambda x: x.timestamp(), ticks_date))
    ticks_date = list(map(lambda x: x.strftime("%d %b %Y %T"), ticks_date))
    ticks_dict = dict(zip(ticks, ticks_date))

    plot1 = figure(title=" Volume plot", x_axis_label="time stamp",
                   y_axis_label = "volume", plot_width=1000)
    plot1.line(data_frame["time_stamp"], data_frame["volume"])
    plot1.yaxis.major_label_orientation = "vertical"
    plot1.xaxis.ticker = FixedTicker(ticks=ticks)
    plot1.xaxis.major_label_overrides = ticks_dict
    plot1.xaxis.major_label_orientation = pi / 3

    plot2 = figure(title=" Average price plot", x_axis_label="time stamp",
                   y_axis_label = "average price", plot_width=1000)
    plot2.line(data_frame["time_stamp"], data_frame["average_price"])
    plot2.yaxis.major_label_orientation = "vertical"
    plot2.xaxis.ticker = FixedTicker(ticks=ticks)
    plot2.xaxis.major_label_overrides = ticks_dict
    plot2.xaxis.major_label_orientation = pi / 3
    return layouts.column([plot1, plot2])


if __name__ == '__main__':
    cl_arg = parser_cl_args()
    manage_visualizer(cl_arg)
