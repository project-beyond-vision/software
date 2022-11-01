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
FLAME_MESSAGE = "Flame detected"
PANIC_MESSAGE = "Panic button asserted"
EMPTY_STRING = ""

class MqttManager():

    def __init__(self, client):
        self.client = client
        self.datastore = {}
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code", str(rc))
        client.subscribe("group_05/imu/data")
        client.subscribe("group_05/imu/threshold")
        client.subscribe("group_05/gps")
        client.subscribe("group_05/flame")
        client.subscribe("group_05/panic")

    def on_message(self, client, userdata, msg):
        # print(msg.topic, msg.payload.decode("utf-8"))
        inputmsg = msg.payload.decode("utf-8")

        data = json.loads(inputmsg)

        if not data["id"] in self.datastore:
            self.datastore[data["id"]] = {}
            self.datastore[data["id"]]["imu_queue"] = []
            self.datastore[data["id"]]["gps_reason"] = ""
            self.datastore[data["id"]]["chat_id"] = data["chat_id"]
            self.datastore[data["id"]]["location"] = []
            self.datastore[data["id"]]["predqueue"] = []
            self.datastore[data["id"]]["predqueuebuffer"] = []

        if (msg.topic == "group_05/imu/data"):
            self.store_imu_data(data)
        elif (msg.topic == "group_05/gps"):
            self.update_location(data)
        elif (msg.topic == "group_05/flame"):
            self.handle_flame(data["id"])
        elif (msg.topic == "group_05/panic"):
            self.handle_panic(data["id"])

    def store_database_entry(self, id):
        now = datetime.now()

        #TODO: handle case where predqueuebuffer less than 4
        while len(self.datastore[id]["predqueuebuffer"]) < PREDQUEUE:
            # append NO PREDICTION to the START of the queue
            self.datastore[id]["predqueuebuffer"].insert(0, "") 
        
        obj = {"time":now.isoformat(), "lat":self.datastore[id]["location"][0], "long":self.datastore[id]["location"][1], 
        "is_flame": self.datastore[id]["gps_reason"] == FLAME_MESSAGE,
        "is_panic": self.datastore[id]["gps_reason"] == PANIC_MESSAGE,
        "pred1": self.datastore[id]["predqueuebuffer"][0], 
        "pred2": self.datastore[id]["predqueuebuffer"][1], 
        "pred3": self.datastore[id]["predqueuebuffer"][2], 
        "pred4": self.datastore[id]["predqueuebuffer"][3],
        "pred5": self.datastore[id]["predqueuebuffer"][4], 
        "pred6": self.datastore[id]["predqueuebuffer"][5], 
        "pred7": self.datastore[id]["predqueuebuffer"][6], 
        "pred8": self.datastore[id]["predqueuebuffer"][7], 
        "pred9": self.datastore[id]["predqueuebuffer"][8], 
        "pred10": self.datastore[id]["predqueuebuffer"][9]}

        x = requests.post(db_url, json=obj)

    def store_imu_data(self, data):
        imu_entry = [data["x"], data["y"], data["z"], data["rx"], data["ry"], data["rz"]]
        while len(self.datastore[data["id"]]["imu_queue"]) >= BELT_IMU_QUEUESIZE:
            self.datastore[data["id"]]["imu_queue"].pop(0)
        self.datastore[data["id"]]["imu_queue"].append(imu_entry)
    
    def send_buzzer_trigger(self): 
        self.client.publish("group_05/buzzer", "TEST SENDING BUZZER TRIGGER")
    
    def update_location(self, data):
        # technically update location should be the last step in the api call after fall confirmed
        self.datastore[data["id"]]["location"] = [data["lat"], data["long"]]
        msg = f'{self.datastore[data["id"]]["gps_reason"]} at latitide: {data["lat"]} longitude: {data["long"]}'
        send_telegram_message(msg, self.datastore[data["id"]]["chat_id"])
        self.datastore[data["id"]]["gps_reason"] = EMPTY_STRING
        print("telegram message sent")

        # UNCOMMENT THE LINES BELOW ONLY IF THE SERVER IS RUNNING
        try:
            self.store_database_entry(data["id"])
            print("post request sent")
        except Exception as e:
            print(f"caught {e}")
            print(f"Is the database server running and connected to your local network?")

    def handle_flame(self, id):
        self.datastore[id]["gps_reason"] = FLAME_MESSAGE
        self.client.publish("group_05/gps_signal", str(id))
        
    def handle_panic(self, id):
        # if this function is called, send gps data immediately to user
        self.datastore[id]["gps_reason"] = PANIC_MESSAGE
        self.client.publish("group_05/gps_signal", str(id))

    def make_prediction(self, id):        
        # DO NOT make prediction if there is less than 60 imu entries
        if len(self.datastore[id]["imu_queue"]) < BELT_IMU_QUEUESIZE:
            return
        while len(self.datastore[id]["imu_queue"]) > BELT_IMU_QUEUESIZE:
            self.datastore[id]["imu_queue"].pop(0)
        data = np.array(self.datastore[id]["imu_queue"])
        pred = predictor(data) # dummy variable until api call is done
        # pred = "Fall" #test line remember to comment
        print(pred)
        # update predqueue
        while len(self.datastore[id]["predqueue"]) >= PREDQUEUE:
            self.datastore[id]["predqueue"].pop(0)
        self.datastore[id]["predqueue"].append(pred)

        if pred == "Fall":# and self.stick_threshold:
            print("GPS Trigger")
            self.datastore[id]["gps_reason"] = "Fall detected"
            self.datastore[id]["predqueuebuffer"] = self.datastore[id]["predqueue"]
            # fall confirmed, send trigger for gps data
            self.client.publish("group_05/gps_signal", str(id))
    

def send_telegram_message(msg, chatid):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chatid}&text={msg}"
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
        for key in manager.datastore:
            if time.perf_counter() - predtimer > PRED_INTERVAL:
                predtimer = time.perf_counter()
                manager.make_prediction(key)
        # suspend the thread to make my cpu usage not 100%
        time.sleep(0.001)

if __name__ == "__main__":
    main()
