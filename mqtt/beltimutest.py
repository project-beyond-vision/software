import json
import requests
import paho.mqtt.client as mqtt
import time

TOKEN = "TOKEN"
chat_id = "ID" 
message = "fall detected"
def send_message_to_user():
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
    print(requests.get(url).json()) # this sends the message and prints out the return value

def main():
    client = setup("localhost") #get current ip with ifconfig
    
    temp = time.perf_counter()
    tempthreshold = time.perf_counter()
    while True:
        if time.perf_counter() - temp > 0.05:
            temp = time.perf_counter()
            data = {"x" : time.perf_counter(), "y" : time.perf_counter()/2, "z" : time.perf_counter()/3, "rx" : time.perf_counter(), "ry" : time.perf_counter()/2, "rz" : time.perf_counter()/3 }
            data = json.dumps(data)
            client.publish("group_05/imu/data", data)
        
        if time.perf_counter() - tempthreshold > 12:
            print("threshold")
            tempthreshold = time.perf_counter()
            client.publish("group_05/imu/threshold", "yes")
        time.sleep(0.001)

def setup(hostname: str) -> mqtt.Client:
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    print("Connecting")
    client.connect(hostname, 1883, 60)
    client.loop_start()
    return client

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected.")
        client.subscribe("group_05/gps_signal")
        print("subscribed to ")
    else:
        print("Failed to connect. Error code:", rc)

def on_message(client, userdata, msg):
    print("send gps")
    # Payload is in msg. We convert it back to a Python dictionary.
    # recv_dict = json.loads(msg.payload)
    data = {"lat": 3.14, "long": 2.71}
    client.publish("group_05/gps", json.dumps(data))
    # send_message_to_user()

if __name__ == "__main__":
    main()
