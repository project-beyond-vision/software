import paho.mqtt.client as mqtt
import json
import csv
import time

#walking jogging sitting gettingup fall neutral climbing stairs
# lateral forward backward
person = "wamika"
action = "walking"
falltype = ""

COUNT_THRESHOLD = 60
MOSQUITTO_BROKER_IP = "localhost"
DATA_COLLECTION_INTERVAL = 3

circularqueue = []

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected.")
        client.subscribe("group_05/imu/data")
    else:
        print("Failed to connect. Error code:", rc)

def on_message(client, userdata, msg):
    global circularqueue
    # Payload is in msg. We convert it back to a Python dictionary.
    recv_dict = json.loads(msg.payload)

    # Recreate the data
    # print("Received data: ", recv_dict)
    circularqueue.append(recv_dict)
    while len(circularqueue) > COUNT_THRESHOLD:
        circularqueue.pop(0)

    # Can send for data analytics here

def setup(hostname: str) -> mqtt.Client:
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    # client.connect(hostname)
    client.connect(hostname, 1883, 60)
    client.loop_start()
    # client.loop_forever()
    return client

def actionstr(isStand):
    if isStand:
        action = "fall/right"
    return action

# Test main
def main():
    client = setup(MOSQUITTO_BROKER_IP)
    global circularqueue
    global action
    ctr = 0
    fields = ["x", "y", "z", "rx", "ry", "rz"]
    isStand = True
    print(f"get ready for {actionstr(isStand)} in 3 seconds")
    time.sleep(5)
    while True:
        action = actionstr(isStand)
        print(f"{action} now")
        time.sleep(3)
        # file write happens here
        with open(f"data/{person}/{action}/{ctr}.csv", "x") as f:
            # print(circularqueue)
            if len(circularqueue) == 60:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                for i in range(len(circularqueue)):
                    writer.writerow(circularqueue[i])
                ctr += 1
        print("action finished")
        time.sleep(6.5)



if __name__ == '__main__':
    main()

