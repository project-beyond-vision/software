import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected with result code", str(rc))
    client.subscribe("group_05/imu")

def on_message(client, userdata, msg):
    print(msg.topic, msg.payload.decode("utf-8"))

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    print("Connecting")
    client.connect("192.168.0.190", 1883, 60)
    client.publish("group_05/panic", "TEST SENDING")
    client.loop_forever()

if __name__ == "__main__":
    main()
