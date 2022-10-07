import paho.mqtt.client as mqtt
import json

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected.")
        client.subscribe("Group_05/sensors/#")
    else:
        print("Failed to connect. Error code:", rc)

def on_message(client, userdata, msg):
    # Payload is in msg. We convert it back to a Python dictionary.
    recv_dict = json.loads(msg.payload)

    # Recreate the data
    print("Received data: ", recv_dict)

    # Can send for data analytics here

def setup(hostname: str) -> mqtt.Client:
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    # client.connect(hostname)
    client.connect("localhost", 1883, 60)
    # client.loop_start()
    client.loop_forever()
    return client

# Test main
def main():
    setup("192.168.0.1")

if __name__ == '__main__':
    main()