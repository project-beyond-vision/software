import numpy as np
import pandas as pd
import keras

STEP_SIZE = 60
NUM_FEATURES = 6

activity = ['Fall', 'Idle', 'Sitting Action', 'Walking']

mu = [0.04569659011830065, -0.04667049408489638, 0.8193719554627664, 0.04278531663187139, 0.8072567849686795, -0.6344224077940189]
sigma = [0.39364945576561455, 0.7887451362981683, 0.8280885411621361, 87.75105207254057, 59.09748109827988, 51.21752423835156]

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
