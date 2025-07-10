#include <WiFi.h>
#include <PubSubClient.h>
#include "DHT.h"

/* Include WIFI + MQTT settings */
#include "secrets.h"

/* MQTT Topic */
const char* topic = "sensors/room1/dht21";

/* DHT settings*/
#define DHTPIN 4
#define DHTTYPE DHT21  
DHT dht(DHTPIN, DHTTYPE);

// WiFi Clients 
WiFiClient espClient;
PubSubClient client(espClient);

/* WiFi connect */
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
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

/* MQTT connection */
void reconnect() {
  while (!client.connected()) {
    Serial.print("Trying MQTT connection...");
    if (client.connect("ESP32_DHT21", MQTT_USER, MQTT_PASS)) {
      Serial.println("success!");
    } else {
      Serial.print("error, rc=");
      Serial.print(client.state());
      Serial.println(" retrying in 5s...");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  setup_wifi();
  client.setServer(MQTT_SERVER, MQTT_PORT);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  float h = dht.readHumidity();
  float t = dht.readTemperature();

  // Check for errors
  if (isnan(h) || isnan(t)) {
    Serial.println("Couldn't read from DHT21");
    return;
  }

  // JSON payload
  char payload[100];
  snprintf(payload, sizeof(payload), "{\"temperature\": %.1f, \"humidity\": %.1f}", t, h);
  Serial.print("Sending: ");
  Serial.println(payload);

  client.publish(topic, payload);

  delay(10000); 
}
