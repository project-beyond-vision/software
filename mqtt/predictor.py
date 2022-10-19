import numpy as np
import pandas as pd
import keras



activity = ['Fall', 'Jogging', 'Sitting action', 'Walking', 'climbing stairs', 'getting up']

mu = [0.012236175547560521, -0.844028325626327, -0.1543912455955434, 0.2556826382272823, 1.5261069734771806, -0.2920010667935128]
sigma = [0.34769250871819196, 0.5536567307930977, 0.42467598155613845, 35.02454787273533, 35.0604674029397, 27.524737149885194]

def normalize_features(data, mu_data, sigma_data):
    return (data - mu_data)/sigma_data

def predictor(inputs):

    Test_data = inputs
    for i in range(0,6):
        for j in range(0,60):
            Test_data[j][i] = normalize_features(Test_data[j][i], mu[i], sigma[i])

    Test_data = np.reshape(Test_data, newshape=(1,) + Test_data.shape)

    # print("test data shape: ", Test_data.shape)

    model = keras.models.load_model('best_model_lstm.h5')

    Test_data = Test_data.astype("float32")

    pred = model.predict(Test_data)
    prediction = np.argmax(pred, axis=1)
    return activity[prediction[0]]
