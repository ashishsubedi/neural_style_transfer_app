import numpy as np
import tensorflow as tf

import cv2

import tensorflow.keras.backend as K
import sys
import time
import PIL

# from flask import Flask, render_template, request
# from werkzeug.utils import secure_filename
import os
from os import path
# from uuid import uuid4
# import json



# app = Flask(__name__)

UPLOAD_FOLDER = path.abspath('uploads')

#CONFIGS
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

MODEL_PATH = os.path.abspath('model/simple_model.h5')

IMAGE_WIDTH, IMAGE_HEIGHT = 28,28
n_C = 1

model = None

def load_model():
    global model
    if model == None:
        model = tf.keras.models.load_model(MODEL_PATH)
        print('Model loaded')
    return model


def load_and_preprocess(path):
    img = cv2.imread(path)
    img = cv2.resize(img,(IMAGE_WIDTH,IMAGE_HEIGHT),cv2.INTER_CUBIC)
    origi = img.copy()
    img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    img = img.astype(np.float32)
    img = img/255.0
    # img = preprocess_input(img)
    img = img.reshape(-1,IMAGE_WIDTH,IMAGE_HEIGHT,n_C)
    return img,origi

def perform_ops(image):
    img,origi = load_and_preprocess(image)
    print(img.shape)

    model = load_model()
    

    prediction = model.predict(img)
    print("Prediction complete")
    return np.argmax(prediction)



