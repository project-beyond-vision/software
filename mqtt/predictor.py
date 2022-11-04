import numpy as np
import pandas as pd
import keras

STEP_SIZE = 60
NUM_FEATURES = 6

activity = ['Sitting action', 'Fall', 'Walking', 'climbing stairs', 'getting up']

mu = [0.016859139784946162, -0.036989516129032354, 0.3306317204301088, -0.716561021505379, -0.41315268817204404, 0.056315860215054955]
sigma = [0.3169782064815828, 0.298379167917324, 0.5189035834200442, 55.572584842376756, 31.52775141330042, 32.75767648225105]

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
    model = keras.models.load_model('best_model_tr.h5')

    Test_data = Test_data.astype("float32")

    pred = model.predict(Test_data)
    prediction = np.argmax(pred, axis=1)[0]

    # print(prediction.shape)

    return activity[prediction]
