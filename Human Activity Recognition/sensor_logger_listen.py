from datetime import datetime
import json
import pandas as pd
from flask import Flask, request
import logging
##from A2_walking_detection import classify_live_window
from A3_activity_recognition import classify_live_window

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
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, ConfusionMatrixDisplay
from scipy.signal import butter, filtfilt, find_peaks
from sklearn.tree import DecisionTreeClassifier,export_graphviz
from sklearn.model_selection import train_test_split

import warnings
warnings.filterwarnings("ignore") # for append deprecation warning

# Modify this line depending on what sensors you are planning to use for classification. See below for the streams you have available. 
ALLOWED_SENSORS = ['accelerometer','gyroscope']
WINDOW_SIZE = 5 #seconds
UPDATE_FREQ_MS = 100

df = pd.DataFrame()
row_count=0
data_pkts=0

app = Flask(__name__)

# Set the logging off for Flask
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
log = logging.getLogger('flask')
log.setLevel(logging.ERROR)

@app.route("/data", methods=["POST"])

def data():  # listens to the data streamed from the sensor logger

    global row_count, data_pkts
    global df
    
    if str(request.method) == "POST":
##            print(f'received data: {request.data}\n\n\n\n\n\n\n\n\n\n\n')
            data = json.loads(request.data)

            
            for d in data['payload']:

                if d['name'] not in ALLOWED_SENSORS:
                    continue

                row = {}
                row['time'] = datetime.fromtimestamp(d['time'] / 1000000000)
                
                if d['name'] == 'accelerometer':
                    row['accel_x'] = d['values']['x']
                    row['accel_y'] = d['values']['y'] 
                    row['accel_z'] = d['values']['z']
                    
                elif d['name'] == 'accelerometeruncalibrated':
                    row['acceluncalib_x'] = d['values']['x']
                    row['acceluncalib_y'] = d['values']['y']
                    row['acceluncalib_z'] = d['values']['z']

                elif d['name'] == 'totalacceleration':
                    row['totalaccel_x'] = d['values']['x']
                    row['totalaccel_y'] = d['values']['y']
                    row['totalaccel_z'] = d['values']['z']

                elif d['name'] == 'gyroscope':
                    row['gyro_x'] = d['values']['x']
                    row['gyro_y'] = d['values']['y']
                    row['gyro_z'] = d['values']['z']
                    
                elif d['name'] == 'gyroscopeuncalibrated':
                    row['gyro_x'] = d['values']['x']
                    row['gyro_y'] = d['values']['y']
                    row['gyro_z'] = d['values']['z']

                elif d['name'] == 'gravity':
                    row['gravity_x'] = d['values']['x']
                    row['gravity_y'] = d['values']['y']
                    row['gravity_z'] = d['values']['z']
                    
                elif d['name'] == 'orientation':
                    row['quat_x'] = d['values']['qx']
                    row['quat_y'] = d['values']['qy']
                    row['quat_z'] = d['values']['qz']
                    row['quat_w'] = d['values']['qw']
                    row['roll'] = d['values']['roll']
                    row['pitch'] = d['values']['pitch']
                    row['yaw'] = d['values']['yaw']
                    
                elif d['name'] == 'magnetometeruncalibrated':
                    row['maguncalib_x'] = d['values']['x']
                    row['maguncalib_y'] = d['values']['y']
                    row['maguncalib_z'] = d['values']['z']
                    
                elif d['name'] == 'magnetometer':
                    row['mag_x'] = d['values']['x']
                    row['mag_y'] = d['values']['y']
                    row['mag_z'] = d['values']['z']
                    
                elif d['name'] == 'barometer':
                    row['pressure'] = d['values']['pressure']
                    row['relativeAltitude'] = d['values']['relativeAltitude']
                    
                elif d['name'] == 'microphone':
                    row['dBFS'] = d['values']['dBFS']
                    
                elif d['name'] == 'light':
                    row['lux'] = d['values']['lux']
                    
                elif d['name'] == 'location':
                    row['latitude'] = d['values']['latitude'] 
                    row['longitude'] = d['values']['longitude']
                    row['altitude'] = d['values']['altitude']
                    row['speed'] = d['values']['speed']
                    row['bearing'] = d['values']['bearing']
                    row['horizontalAccuracy'] = d['values']['horizontalAccuracy']
                    row['verticalAccuracy'] = d['values']['verticalAccuracy']

                df = df.append(row, ignore_index=True)
                row_count += 1

    data_pkts += 1
    if data_pkts % WINDOW_SIZE == 0:
        classify()
        row_count = 0
        data_pkts = 0
        
    return "success"

@app.route("/classify", methods=["POST"])

def classify():
    window = df.iloc[-row_count:]
    window.reset_index()
##    print(window.shape)
##    print(window.tail())
    result = classify_live_window(window)
    print(result)
    return result


if __name__ == "__main__":
	app.run(port=8000, host="0.0.0.0")
