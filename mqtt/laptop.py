import sys
sys.path.append('..')

import paho.mqtt.client as mqtt
import json
import requests
from datetime import datetime
from config import *
from predictor import *
import time

# it should have 60 entries in it
# x y z rx ry rz

class MqttManager():

    def __init__(self, client):
        self.client = client
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        dummy = [1.1,2.2,3.3,4.4,5.5,6.6]
        self.belt_imu_queue = []
        for i in range(60):
            self.belt_imu_queue.append(dummy)
        self.predqueue = []
        self.stick_threshold = False
        self.stick_threshold_time = time.perf_counter()
        self.location = [] # for lat and long

        self.predqueuebuffer = [] # to store prediction queue on fall prediction and ensure it is not overwritten

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code", str(rc))
        client.subscribe("group_05/imu/data")
        client.subscribe("group_05/imu/threshold")
        client.subscribe("group_05/gps")

    def on_message(self, client, userdata, msg):
        print(msg.topic, msg.payload.decode("utf-8"))
        if (msg.topic == "group_05/imu/data"):
            self.store_imu_data(msg.payload.decode("utf-8"))
        elif (msg.topic == "group_05/imu/threshold"):
            self.update_threshold()
        elif (msg.topic == "group_05/gps"):
            self.update_location(msg.payload.decode("utf-8"))

    def store_database_entry(self):
        now = datetime.now()

        #TODO: handle case where predqueuebuffer less than 4
        while len(self.predqueuebuffer) < 4:
            # append NO PREDICTION to the START of the queue
            self.predqueuebuffer.insert(0, NO_PREDICTION) 
        
        obj = {"time":now.isoformat(), "lat":self.location[0], "long":self.location[1], 
        "pred1": self.predqueuebuffer[0], 
        "pred2": self.predqueuebuffer[1], 
        "pred3": self.predqueuebuffer[2], 
        "pred4": self.predqueuebuffer[3]}

        x = requests.post(db_url, json=obj)

    def store_imu_data(self, data):
        data = json.loads(data)
        imu_entry = [data["x"], data["y"], data["z"], data["rx"], data["ry"], data["rz"]]
        while len(self.belt_imu_queue) >= 60:
            self.belt_imu_queue.pop(0)
        self.belt_imu_queue.append(imu_entry)
    
    def send_buzzer_trigger(self): 
        self.client.publish("group_05/buzzer", "TEST SENDING BUZZER TRIGGER")
    
    def update_location(self, data):
        data = json.loads(data)
        # technically update location should be the last step in the api call after fall confirmed
        self.location = [data["lat"], data["long"]]

        send_telegram_message()
        print("telegram message sent")

        # UNCOMMENT THE LINES BELOW ONLY IF THE SERVER IS RUNNING
        self.store_database_entry()
        print("post request sent")
    
    def update_threshold(self):
        self.stick_threshold = True
        self.stick_threshold_time = time.perf_counter()

    def make_prediction(self):        
        # DO NOT make prediction if there is less than 60 imu entries
        if len(self.belt_imu_queue) < 60:
            return
        print("here")
        pred = predictor(np.array(self.belt_imu_queue)) # dummy variable until api call is done
        print(pred)
        # update predqueue
        while len(self.predqueue) >= 4:
            self.predqueue.pop(0)
        self.predqueue.append(pred)

        # 1 is dummy number for when fall detected
        if pred == activity[0] and self.stick_threshold:
            self.predqueuebuffer = self.predqueue
            # fall confirmed, send trigger for gps data
            self.client.publish("group_05/gps_signal", "GPS trigger message")
    

def send_telegram_message():
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
    print(requests.get(url).json()) # this sends the message and prints out the return value



def main():
    client = mqtt.Client()
    manager = MqttManager(client)

    print("Connecting")
    client.connect(mosquitto_ip, 1883, 60)
    # client.loop_forever() #blocks function thread from executing forever
    client.loop_start() # non-blocking
    predtimer = time.perf_counter()
    while True:
        # make predictions in 3 second intervals
        if time.perf_counter() - predtimer > PRED_INTERVAL:
            predtimer = time.perf_counter()
            manager.make_prediction()

        # check if stick threshold is true
        if manager.stick_threshold:
            if time.perf_counter_ns() - manager.stick_threshold_time > STICK_THRESHOLD_TIME:
                manager.stick_threshold = False
        

        time.sleep(0.001)

if __name__ == "__main__":
    main()
