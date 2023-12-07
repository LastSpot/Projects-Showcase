import pandas as pd
import glob
import re
import os
import sys
import pickle
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from sklearn import tree, metrics
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    classification_report,
    ConfusionMatrixDisplay,
)
from scipy.signal import butter, filtfilt, find_peaks
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from sklearn.model_selection import train_test_split


def viz_tree(dt_model, features_frames, cnames):
    feature_names = features_frames.columns.tolist()
    fig, ax = plt.subplots(figsize=(9, 4))
    tree.plot_tree(
        dt_model,
        feature_names=feature_names,
        fontsize=7,
        class_names=cnames,
        filled=True,
        ax=ax,
    )
    plt.title("Decision Tree")
    plt.savefig("dt.png")


def calc_magnitude(data):
    data["accel_mag"] = np.sqrt(data["x"] ** 2 + data["y"] ** 2 + data["z"] ** 2)
    data["accel_mag"] = data["accel_mag"] - data["accel_mag"].mean()
    return data


def remove_noise(data, sampling_rate):
    from scipy.signal import butter, filtfilt, find_peaks

    cutoff = 5
    order = 2
    b, a = butter(order, cutoff / (sampling_rate / 2), btype="lowpass")
    data["filtered_accel_mag"] = filtfilt(b, a, data["accel_mag"])
    return data


def add_features(window: pd.DataFrame):
    features = {}
    features["avg"] = window["accel_mag"].mean()
    features["max"] = window["accel_mag"].quantile(1)
    features["med"] = window["accel_mag"].quantile(0.5)
    features["min"] = window["accel_mag"].quantile(0)
    features["q25"] = window["accel_mag"].quantile(0.25)
    features["q75"] = window["accel_mag"].quantile(0.75)
    features["std"] = window["accel_mag"].std()
    df = pd.DataFrame([features])
    return df


def train_decision_tree(frames):
    X = frames[["avg", "max", "med", "min", "q25", "q75", "std"]]
    y = frames["activity"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    dt_model = DecisionTreeClassifier(criterion="entropy", max_depth=5).fit(
        X_train, y_train
    )
    dt_pred = dt_model.predict(X_test)
    acc = dt_model.score(X_test, y_test)
    dt_cm = confusion_matrix(y_test, dt_pred, labels=dt_model.classes_)
    print(classification_report(y_test, dt_pred))
    print("Accuracy on test set:", acc)
    return (dt_model, dt_cm, acc)


def classify_live_window(df):
    df_accel = df[df["accel_x"].notna() & df["accel_y"].notna() & df["accel_z"].notna()]
    df_valid = df_accel[["accel_x", "accel_y", "accel_z"]].rename(
        columns={"accel_x": "x", "accel_y": "y", "accel_z": "z"}
    )
    df_valid = calc_magnitude(df_valid)
    df_valid = add_features(df_valid)
    X = df_valid[["avg", "max", "med", "min", "q25", "q75", "std"]]
    with open("dt_model.pkl", "rb") as f:
        model = pickle.load(f)
    y_pred = model.predict(df_valid)
    return y_pred


def test_live_classification():
    data = {
        "accel_x": [0.011531],
        "accel_y": [0.002931],
        "accel_z": [0.019604],
        "time": ["2023-08-01 18:40:43.344408"],
    }
    df = pd.DataFrame(data)
    df = pd.concat([df] * 1000, ignore_index=True)
    y_pred = classify_live_window(df)
    print(y_pred)


def extract_features(data, window_sec, sample_rate, activity):
    window_data = data.resample(str(window_sec) + "S")
    dataFrameToReturn = pd.DataFrame(
        columns=["avg", "max", "med", "min", "q25", "q75", "std", "label"]
    )
    for time, window in window_data:
        features = add_features(window)
        features["label"] = [activity]
        dataFrameToReturn = pd.concat([dataFrameToReturn, features], join="inner")
    return dataFrameToReturn


def all_data_to_combined_csv():
    import os
    import sys

    folders = glob.glob("data/Activities/*")[1:]
    all_data = pd.DataFrame(
        columns=["avg", "max", "med", "min", "q25", "q75", "std", "label"]
    )
    all_data_list = []
    for folder in folders:
        activity = os.path.basename(folder)
        file_names = glob.glob("data/Activities/" + activity + "/*.csv")
        for file in file_names:
            file_data = pd.read_csv(file, parse_dates=["time"], index_col="time")
            window_sec = 10
            sampling_rate = 100
            file_data = calc_magnitude(file_data)
            file_data = remove_noise(file_data, sampling_rate)
            file_data = extract_features(file_data, window_sec, sampling_rate, activity)
            all_data_list.append(file_data)
    all_data = pd.concat(all_data_list, join="outer")
    all_data.to_csv(
        "./data/Activities/all_data.csv",
        columns=["avg", "max", "med", "min", "q25", "q75", "std", "label"],
        index=False,
    )
