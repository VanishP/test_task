"""

Creates plots of value and average price

"""

from math import pi
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

from cl_parser import  parse_cl_args, check_period_correct





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
                    [[float(obj["ts"]),
                      float(obj["volume"]),
                      float(obj["price"])]],json_data))).T
    data_frame = pd.DataFrame(dict(zip(["time_stamp", "volume",
                                        "average_price"],
                                        [json_data[0].tolist()[0],
                                         json_data[1].tolist()[0],
                                         json_data[2].tolist()[0]])))
    return data_frame


def manage_visualizer(cl_arg: ClassVar):
    """
    Creates files with plots and data in selected mode(create, append) and
    records data and plots in dir.
    """

    if cl_arg.mode == "create":
        build_plot(cl_arg.file, cl_arg.period, cl_arg.output,
                   cl_arg.interval)
    elif cl_arg.mode == "append":
        data_file_path = unite_data_files(cl_arg)
        data_union = open(data_file_path, "r")
        build_plot(data_union, cl_arg.period,
                   cl_arg.output, cl_arg.interval, data_file_path)
        data_file_path.unlink()


def unite_data_files(cl_arg: ClassVar) -> ClassVar:
    """ Create .json file including union with other .json files"""
    data_file_path = pathlib.Path.cwd() / (cl_arg.output + "_data.json")
    data, append_data = cl_arg.new_file.read(), cl_arg.file.read()
    data = data[:-1] + ", " + append_data[1:]
    cl_arg.new_file.close()
    cl_arg.file.close()
    fout = open(data_file_path, "w")
    fout.write(data)
    fout.close()
    return data_file_path

def choise_date_in_period(period: List[str],
                          data_frame: ClassVar,
                          data_file: ClassVar) -> ClassVar:
    """ Filter data by period"""
    p0, p1 = check_period_correct(period, data_frame, data_file)
    data_frame = data_frame.loc[data_frame["time_stamp"] >= p0.timestamp()]
    data_frame = data_frame.loc[data_frame["time_stamp"] <= p1.timestamp()]
    return data_frame


def record_in_dir(data_file: io, output: str):
    """ Records in dir plots and data"""
    directory = pathlib.Path.cwd()/(output + "_dir")
    directory.mkdir(parents=True)
    output_file(directory/(output + ".html"))

    shutil.copyfile(data_file.name, directory/(output + "_data.json"))
    data_file.close()


def build_plot(data_file:io, period:List[str], output:str,
               interval: List[int], data_file_path: ClassVar=None ):
    """
    Prepares data and create plots
    """
    time_delta = [
        datetime.timedelta(seconds=interval[1]),
        datetime.timedelta(minutes=interval[1]),
        datetime.timedelta(hours=interval[1]),
        datetime.timedelta(days=interval[1]),
        datetime.timedelta(weeks=interval[1])
    ]

    data_frame = parse_file(data_file)
    data_frame = data_frame.sort_values(by="time_stamp")
    if period is not None:
        data_for_plots = choise_date_in_period(period,
                                               data_frame,
                                               data_file_path)
    else:
        data_for_plots = data_frame
    plots = create_plots(data_for_plots, time_delta[interval[0]])
    record_in_dir(data_file, output)
    show(plots)

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
    first_date = datetime.datetime.fromtimestamp(
                 data_frame.values[0, 0])
    last_date = datetime.datetime.fromtimestamp(
                data_frame.values[data_frame.shape[0] - 1, 0])
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
