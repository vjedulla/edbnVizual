#import eDBN.Execute as edbn
# from builtins import print

# import Utils.Utils as utils
from config import UPLOAD_FOLDER
import pandas as pd
from eDBN import Execute as edbn
from Utils.LogFile import LogFile
from Utils.BPIPreProcess import preProcessFile, get_constructed_file
import Utils.PlotResults as plot
import time


from ConceptDrift.ConceptDrift import *

def only_train(default_dataset="edbn/Data/BPIC15_1_sorted.csv", default_alias="run/"):
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

    return model

def train_vars_and_test(model, alias, filename, event_emit_obj):
    file = UPLOAD_FOLDER + "/" + alias + "/" + filename

    folder = UPLOAD_FOLDER + "/" + alias + "/"

    train_file = get_constructed_file(file)
    test_file = get_constructed_file(file, type="test")

    train_data = LogFile(train_file, ",", 0, 500000, None, "Case")
    train_data.remove_attributes(["Anomaly", "time"])

    event_emit_obj('score_resp', {'step': 2, "msg": "Data loaded."})

    train_data.create_k_context()
    event_emit_obj('score_resp', {'step': 3, "msg": "Build K-Context for data."})

    model_trained_on_data = edbn.train_seperate(train_data, model)

    event_emit_obj('score_resp', {'step': 4, "msg": "Finished training data."})

    test_data = LogFile(test_file, ",", header=0, rows=500000, time_attr=None, trace_attr="Case",
                        values=train_data.values)

    edbn.test(test_data, folder + "output.csv", model_trained_on_data, label="Anomaly", normal_val="0")

    event_emit_obj('score_resp', {'step': 5, "msg": "Finished testing"})

    # # Plot the ROC curve based on the results
    # plot.plot_single_roc_curve(experiment_folder + "output.csv")
    event_emit_obj('score_resp', {'step': 6, "msg": "Preparing to score."})
    scores = get_event_scores(test_data.data, model_trained_on_data)

    r = list(scores.keys())
    one = np.random.randint(0, len(r))
    random_key = r[one]

    print(random_key)
    print(test_data.convert_int2string('Case', int(random_key)))

    # results = plottable(scores)
    event_emit_obj('score_resp', {'step': 7, "msg": "Finished scoring!"})

    print("Finished scoring...")

    # plot_single_scores(scores)
    # r, ps = plot_pvalues(scores, 20)
    return scores
    # return scores, (r, ps), model


def plottable(scores):
    """
    Plot all accumulated trace scores

    :param scores: scores
    :return: None
    """

    y = []
    x = []
    for key in sorted(scores.keys()):
        if sum(scores[key]) != 0:
            y.append(math.log10(sum(scores[key]) / len(scores[key])))

    return y

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
