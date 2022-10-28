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
        self.belt_imu_queue = []
        self.predqueue = []
        self.stick_threshold = False
        self.stick_threshold_time = time.perf_counter()
        self.location = [] # for lat and long
        self.gps_reason = ""

        self.predqueuebuffer = [] # to store prediction queue on fall prediction and ensure it is not overwritten

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code", str(rc))
        client.subscribe("group_05/imu/data")
        client.subscribe("group_05/imu/threshold")
        client.subscribe("group_05/gps")
        client.subscribe("group_05/flame")
        client.subscribe("group_05/panic")

    def on_message(self, client, userdata, msg):
        # print(msg.topic, msg.payload.decode("utf-8"))
        if (msg.topic == "group_05/imu/data"):
            self.store_imu_data(msg.payload.decode("utf-8"))
        elif (msg.topic == "group_05/imu/threshold"):
            self.update_threshold()
        elif (msg.topic == "group_05/gps"):
            self.update_location(msg.payload.decode("utf-8"))
        elif (msg.topic == "group_05/flame"):
            self.handle_flame()
        elif (msg.topic == "group_05/panic"):
            self.handle_panic()

    def store_database_entry(self):
        now = datetime.now()

        #TODO: handle case where predqueuebuffer less than 4
        while len(self.predqueuebuffer) < PREDQUEUE:
            # append NO PREDICTION to the START of the queue
            self.predqueuebuffer.insert(0, NO_PREDICTION) 
        
        obj = {"time":now.isoformat(), "lat":self.location[0], "long":self.location[1], 
        # "isflame": ,
        # "ispanic": ,
        "pred1": self.predqueuebuffer[0], 
        "pred2": self.predqueuebuffer[1], 
        "pred3": self.predqueuebuffer[2], 
        "pred4": self.predqueuebuffer[3],
        "pred5": self.predqueuebuffer[4], 
        "pred6": self.predqueuebuffer[5], 
        "pred7": self.predqueuebuffer[6], 
        "pred8": self.predqueuebuffer[7], 
        "pred9": self.predqueuebuffer[8], 
        "pred10": self.predqueuebuffer[9]}

        x = requests.post(db_url, json=obj)

    def store_imu_data(self, data):
        data = json.loads(data)
        imu_entry = [data["x"], data["y"], data["z"], data["rx"], data["ry"], data["rz"]]
        while len(self.belt_imu_queue) >= BELT_IMU_QUEUESIZE:
            self.belt_imu_queue.pop(0)
        self.belt_imu_queue.append(imu_entry)
    
    def send_buzzer_trigger(self): 
        self.client.publish("group_05/buzzer", "TEST SENDING BUZZER TRIGGER")
    
    def update_location(self, data):
        data = json.loads(data)
        # technically update location should be the last step in the api call after fall confirmed
        self.location = [data["lat"], data["long"]]
        msg = f'{self.gps_reason} at latitide: {data["lat"]} longitude: {data["long"]}'
        send_telegram_message(msg)
        print("telegram message sent")

        # UNCOMMENT THE LINES BELOW ONLY IF THE SERVER IS RUNNING
        self.store_database_entry()
        print("post request sent")
    
    def update_threshold(self):
        self.stick_threshold = True
        self.stick_threshold_time = time.perf_counter()

    def handle_flame(self):
        self.gps_reason = "flame detected"
        self.client.publish("group_05/gps_signal", "GPS trigger message")
        
    def handle_panic(self):
        # if this function is called, send gps data immediately to user
        self.gps_reason = "panic button asserted"
        self.client.publish("group_05/gps_signal", "GPS trigger message")

    def make_prediction(self):        
        # DO NOT make prediction if there is less than 60 imu entries
        if len(self.belt_imu_queue) < BELT_IMU_QUEUESIZE:
            return
        while len(self.belt_imu_queue) > BELT_IMU_QUEUESIZE:
            self.belt_imu_queue.pop(0)
        data = np.array(self.belt_imu_queue)
        pred = predictor(data) # dummy variable until api call is done
        # pred = "Fall" #test line remember to comment
        print(pred)
        # update predqueue
        while len(self.predqueue) >= PREDQUEUE:
            self.predqueue.pop(0)
        self.predqueue.append(pred)

        # 1 is dummy number for when fall detected
        if pred == "Fall" and self.stick_threshold:
            print("GPS Trigger")
            self.gps_reason = "Fall detected"
            self.predqueuebuffer = self.predqueue
            # fall confirmed, send trigger for gps data
            self.client.publish("group_05/gps_signal", "GPS trigger message")
    

def send_telegram_message(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={msg}"
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
        # make predictions every PRED_INTERVAL seconds
        if time.perf_counter() - predtimer > PRED_INTERVAL:
            predtimer = time.perf_counter()
            manager.make_prediction()

        # check if stick threshold is true
        if manager.stick_threshold:
            if time.perf_counter() - manager.stick_threshold_time > STICK_THRESHOLD_TIME:
                manager.stick_threshold = False
        # suspend the thread to make my cpu usage not 100%
        time.sleep(0.001)

if __name__ == "__main__":
    main()
