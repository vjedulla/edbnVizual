#matplotlib.use("Agg")  # Disable comment when no output should be shown (for running on servers without graphical interface)

import datetime
import multiprocessing as mp
import random
import os
import time

import pandas as pd
from joblib import Parallel, delayed, parallel_backend

import Bohmer.LikelihoodGraph as lg


def read_raw_file(file):
    """
    Read original file and group the data by the case number

    :param file: Locatin of original .csv file
    :return: dictionary with data grouped by case
    """
    print("Reading", file)
    output = {}

    with open(file, "r") as fin:
        fin.readline()
        for line in fin:
            line_split = line.split(",")
            date_parse = line_split[3].strip('\n')

            date = datetime.datetime.strptime(date_parse, "%m/%d/%y %H:%M:%S")

            # MANDO ADD: added unix timestamp
            # unixtime = int(time.mktime(date.timetuple()))

            line = ["a_" + line_split[1], "r_" + line_split[2], "wd_" + str(date.weekday())]

            if eval(line_split[0]) not in output:
                output[eval(line_split[0])] = []
            output[eval(line_split[0])].append(line)

    return output


def write_to_file(train_file, test_file, log_dict):
    """
    Function to split original data in training and test data with the introduction of anomalies.
    Anomalies are generated according to the explanation in Bohmer paper

    :param train_file: location to save the training file
    :param test_file: location to save the test file
    :param log_dict: dictionary containing the original data grouped by case
    """
    i = 0
    train_events = []
    test_events = []
    tst=0
    for key in log_dict:
        trace = log_dict[key]

        if random.randint(0,1) == 0: # Add file to training set with 50% chance
            for e_idx in range(len(trace)):
                train_events.append(",".join([str(x) for x in trace[e_idx]]) + "," + str(key) + ",0")
        else: # Add file to test set
            if random.randint(0,100) > 50: # No anomaly injection with 50% chance
                for e_idx in range(len(trace)):
                    test_events.append(",".join([str(x) for x in trace[e_idx]]) + "," + str(key) + ",0")
            else: # Anomaly injection
                trace = introduce_anomaly(trace)
                tst+=1
                for e_idx in range(len(trace)):
                    test_events.append(",".join([str(x) for x in trace[e_idx]]) + "," + str(key) + ",1")

    with open(train_file, "w") as fout:
        fout.write(",".join(["Activity", "Resource", "Weekday", "Case", "Anomaly"]) + "\n")
        for e in train_events:
            fout.write(e + "\n")

    with open(test_file, "w") as fout:
        fout.write(",".join(["Activity", "Resource", "Weekday", "Case", "Anomaly"]) + "\n")
        for e in test_events:
            fout.write(e + "\n")


def introduce_anomaly(trace):
    """
    Add anomaly to the input trace

    :param trace: input trace, containing no anomalies
    :return: trace containing anomalies
    """
    def alter_activity_order(trace):
        if len(trace) == 1:
            return trace
        alter = random.randint(0, len(trace) - 2)
        tmp = trace[alter]
        trace[alter] = trace[alter + 1]
        trace[alter + 1] = tmp
        return trace

    def new_activity(trace):
        new_trace = []
        insert = random.randint(0, len(trace) - 1)
        for i in range(0, len(trace) + 1):
            if i < insert:
                new_trace.append(trace[i])
            elif i == insert:
                new_trace.append(trace[i-1][:])
                new_trace[-1][0] = "a_NEW_ACTIVITY"
            else:
                new_trace.append(trace[i-1])
        return new_trace

    def new_date(trace):
        alter = random.randint(0, len(trace) - 1)
        new_date_generated = trace[alter][2]
        while new_date_generated == trace[alter][2]:
            new_date_generated = random.randint(0, 7)
        trace[alter][2] = "wd_" + str(new_date_generated)
        return trace

    def new_resource(trace):
        alter = random.randint(0, len(trace) - 1)
        trace[alter][1] = "r_NEW_RESOURCE"
        return trace

    def generate_Anomaly(trace, num_diff_anoms, from_nums, to_nums):
        anoms = set()
        for i in range(num_diff_anoms):
            anomaly = random.randint(0,3)
            while anomaly in anoms: # Ensure each type of anomaly is only choosen once
                anomaly = random.randint(0,3)
            for j in range(from_nums, to_nums + 1):
                if anomaly == 0:
                    trace = alter_activity_order(trace)
                elif anomaly == 1:
                    trace = new_activity(trace)
                elif anomaly == 2:
                    trace = new_date(trace)
                elif anomaly == 3:
                    trace = new_resource(trace)
        return trace

    density = random.randint(1,3)
    if density == 1:
        trace = generate_Anomaly(trace, 1, 2, 4)
    elif density == 2:
        trace = generate_Anomaly(trace, 2, 1, 3)
    elif density == 3:
        if random.randint(0,1) == 0:
            trace = generate_Anomaly(trace, 3, 1, 2)
        else:
            trace = generate_Anomaly(trace, 4, 1, 2)

    return trace


def preProcessData(path_to_data):
    for i in range(1,6):
        train = path_to_data + "BPIC15_train_" + str(i) + ".csv"
        test = path_to_data + "BPIC15_test_" + str(i) + ".csv"
        write_to_file(train, test, read_raw_file(path_to_data + "BPIC15_" + str(i) + "_sorted.csv"))

def preProcessFile(path_to_file, output_directory=None):
    parts = path_to_file.split("/")

    d = "/".join(parts[:-1]) + "/"
    f = parts[-1]

    train = f[:-4] + "_train_preprocessed.csv"
    test = f[:-4] + "_test_preprocessed.csv"

    if output_directory is not None:
        if not os.path.isdir(d+output_directory):
            os.makedirs(d+output_directory)

        # add a backslash automatically
        if output_directory[-1] != "/":
            output_directory += "/"

        out_train = d + output_directory + train
        out_test = d + output_directory + test
    else:
        out_train = d + train
        out_test = d + test

    write_to_file(out_train, out_test, read_raw_file(path_to_file))

    experiment_folder = "/".join(out_train.split("/")[:-1]) + "/"

    return out_train, out_test, experiment_folder


def preProcessData_total(path_to_data):
    total_log = {}
    test_keys = set()
    for i in range(5,0,-1):
        log = read_raw_file(path_to_data + "BPIC15_" + str(i) + "_sorted.csv")
        test_keys = test_keys.union(log.keys())
        total_log.update(log)

    train = path_to_data + "BPIC15_train_total.csv"
    test = path_to_data + "BPIC15_test_total.csv"
    write_to_file(train, test, total_log)
