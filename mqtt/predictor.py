import numpy as np
import pandas as pd
import keras

STEP_SIZE = 60
NUM_FEATURES = 6

activity = ['Fall', 'Idle', 'Sitting Action', 'Walking']

mu = [0.039890441176468644, -0.06346862745098501, 0.8367115196078488, 0.317587745098041, 0.912695098039213, -0.6950524509803874]
sigma = [0.3556153673106574, 0.6891854584032185, 0.711727411960497, 76.97070179565804, 51.52418094530509, 45.26152652685546]

def normalize_features(data, mu_data, sigma_data):
    return (data - mu_data)/sigma_data

def predictor(inputs):

    Test_data = inputs

    for i in range(0,NUM_FEATURES):
        for j in range(0,STEP_SIZE):
            Test_data[j][i] = normalize_features(Test_data[j][i], mu[i], sigma[i])
    print(Test_data[0][0])
    Test_data = np.asarray(Test_data).reshape(1, STEP_SIZE * NUM_FEATURES)

    # print("test data shape: ", Test_data.shape)

    # Use absolute path to the .h5 file
    model = keras.models.load_model('best_model_cnn.h5')

    Test_data = Test_data.astype("float32")

    pred = model.predict(Test_data)
    prediction = np.argmax(pred, axis=1)[0]

    # print(prediction.shape)

    return activity[prediction]
