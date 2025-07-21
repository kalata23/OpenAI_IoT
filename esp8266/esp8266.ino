#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <DHT.h>
#include "secrets.h"

#define DHTTYPE DHT21
DHT dht(DHTPIN, DHTTYPE);
ESP8266WebServer server(80);

void handleRoot() {
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  String json = String("{\"temperature\":") + t + ",\"humidity\":" + h + "}";
  server.send(200, "application/json", json);
}

void handleTemp() {
  float t = dht.readTemperature();
  server.send(200, "application/json", String("{\"temperature\":") + t + "}");
}

void handleHum() {
  float h = dht.readHumidity();
  server.send(200, "application/json", String("{\"humidity\":") + h + "}");
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  Serial.println();
  Serial.print("Connecting to WiFi...");

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("SUCCESSFULL");
  Serial.println(WiFi.localIP());

  server.on("/", HTTP_GET, handleRoot);
  server.on("/temperature", HTTP_GET, handleTemp);
  server.on("/humidity", HTTP_GET, handleHum);
  server.begin();
}

void loop() {
  server.handleClient();
}
