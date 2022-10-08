/*
  SimpleMQTTClient.ino
  The purpose of this exemple is to illustrate a simple handling of MQTT and Wifi connection.
  Once it connects successfully to a Wifi network and a MQTT broker, it subscribe to a topic and send a message to it.
  It will also send a message delayed 5 seconds later.
*/

#include "EspMQTTClient.h"
#include "config.h"

EspMQTTClient client(
  ssid,
  wifiPassword,
  "192.168.0.190",  // MQTT Broker server ip
  "MQTTUsername",   // Can be omitted if not needed
  "MQTTPassword",   // Can be omitted if not needed
  "TestClient",     // Client name that uniquely identify your device
  1883              // The MQTT port, default to 1883. this line can be omitted
);

void setup()
{
  Serial.begin(115200);
}

void onConnectionEstablished()
{
  // Subscribe to "mytopic/test" and display received message to Serial
  client.subscribe("group_05/panic", [](const String & payload) {
    Serial.println(payload);
  });
}

unsigned long timer = 0;

void loop()
{
  client.loop();
  if (millis() - timer > 1000) {
    client.publish("group_05/imu", "This is a message"); // You can activate the retain flag by setting the third parameter to true
    Serial.println("published.\n");
    timer = millis();
  }
}
