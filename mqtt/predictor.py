import numpy as np
import pandas as pd
import keras

STEP_SIZE = 60
NUM_FEATURES = 6

activity = ['Fall', 'Idle', 'Sitting Action', 'getting up']

mu = [0.023561455260570106, 0.002645034414947382, 0.7785737463126928, 1.8111327433628308, 1.0473372664700051, 0.6916715830875049]
sigma = [0.3791756317252335, 0.9001023621770838, 0.9596440036725823, 101.56639996458057, 63.4680471424946, 58.78677950701748]

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
