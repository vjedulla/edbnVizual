#import eDBN.Execute as edbn
# from builtins import print

# import Utils.Utils as utils

import pandas as pd
from eDBN import Execute as edbn
from Utils.LogFile import LogFile
from Utils.BPIPreProcess import preProcessFile
import Utils.PlotResults as plot

from ConceptDrift.ConceptDrift import *

def run(default_dataset="edbn/Data/BPIC15_1_sorted.csv", default_alias="run/"):
    # Use the BPIC15_x_sorted.csv to generate new training and test datafiles with anomalies introduced
    # After running this once you can comment this line out
    # which_dataset = "edbn/Data/BPIC15_1_sorted.csv"
    # which_dataset = "edbn/Data/BPIC15_1_sorted.csv"
    # preprocess_folder = "run/"

    which_dataset = default_dataset
    preprocess_folder = default_alias

    train_file, test_file, experiment_folder = preProcessFile(which_dataset, preprocess_folder)

    # Indicate which are the training and test files
    # train_file = "../Data/{}BPIC15_train_1.csv".format(preprocess_folder)
    # test_file = "../Data/{}BPIC15_test_1.csv".format(preprocess_folder)

    # Load logfile to use as training data
    train_data = LogFile(train_file, ",", 0, 500000, None, "Case")
    train_data.remove_attributes(["Anomaly", "time"])

    # Train the model
    model = edbn.train(train_data)

    # Test the model and save the scores in ../Data/output.csv
    test_data = LogFile(test_file, ",", header=0, rows=500000, time_attr=None, trace_attr="Case", values=train_data.values)
    edbn.test(test_data, experiment_folder + "output.csv", model, label="Anomaly", normal_val="0")

    # # Plot the ROC curve based on the results
    # plot.plot_single_roc_curve(experiment_folder + "output.csv")
    scores = get_event_scores(test_data.data, model)

    print("Finished scoring...")

    # plot_single_scores(scores)
    r, ps = plot_pvalues(scores, 20)
    return scores, (r, ps), model


def stephenRun():
    # Use the BPIC15_x_sorted.csv to generate new training and test datafiles with anomalies introduced
    # After running this once you can comment this line out
    # preProcessData("../Data/")

    # Indicate which are the training and test files
    train_file = "../Data/BPIC15_train_1.csv"
    test_file = "../Data/BPIC15_test_1.csv"

    # Load logfile to use as training data
    train_data = LogFile(train_file, ",", 0, 500000, None, "Case")
    train_data.remove_attributes(["Anomaly"])

    # Train the model
    model = edbn.train(train_data)

    # Test the model and save the scores in ../Data/output.csv
    test_data = LogFile(test_file, ",", header=0, rows=500000, time_attr=None, trace_attr="Case",
                        values=train_data.values)
    edbn.test(test_data, "../Data/output.csv", model, label="Anomaly", normal_val="0")

    # Plot the ROC curve based on the results
    plot.plot_single_roc_curve("../Data/output.csv")


if __name__ == "__main__":
    run()
    # stephenRun()
