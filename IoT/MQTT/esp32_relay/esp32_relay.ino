#include <WiFi.h>
#include <PubSubClient.h>
#include "secrets.h"  


#define RELAY_PIN  5 

WiFiClient espClient;
PubSubClient client(espClient);

const char* relay_topic = "devices/room1/relay/set";

// WiFi setup
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("Connection established");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

// MQTT message parser
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("MQTT packet received: ");
  Serial.print(topic);
  Serial.print(" -> ");
  
  String command = "";
  for (unsigned int i = 0; i < length; i++) {
    command += (char)payload[i];
  }
  Serial.println(command);

  command.toUpperCase();

  if (command == "ON") {
    digitalWrite(RELAY_PIN, HIGH);
  } else if (command == "OFF") {
    digitalWrite(RELAY_PIN, LOW);
  }
}

// MQTT reconnect ---
void reconnect() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect("ESP32_Relay", MQTT_USER, MQTT_PASS)) {
      Serial.println("successful!");
      client.subscribe(relay_topic);
    } else {
      Serial.print("error, rc=");
      Serial.print(client.state());
      Serial.println(" → retrying in 5s");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);  // Default state is off
  setup_wifi();
  client.setServer(MQTT_SERVER, MQTT_PORT);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}
