#include <WiFi.h>
#include <WebServer.h>
#include <DHT.h>
#include "secrets.h"

DHT dht(DHTPIN, DHTTYPE);
WebServer server(80);

void handleTemperature() {
  float temp = dht.readTemperature();
  if (isnan(temp)) {
    server.send(500, "application/json", "{\"error\": \"Temp read fail\"}");
    return;
  }
  server.send(200, "application/json", "{\"temperature\": " + String(temp, 1) + "}");
}

void handleHumidity() {
  float hum = dht.readHumidity();
  if (isnan(hum)) {
    server.send(500, "application/json", "{\"error\": \"Humidity read fail\"}");
    return;
  }
  server.send(200, "application/json", "{\"humidity\": " + String(hum, 1) + "}");
}

void handleAll() {
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();
  if (isnan(temp) || isnan(hum)) {
    server.send(500, "application/json", "{\"error\": \"Read fail\"}");
    return;
  }
  String response = "{\"temperature\": " + String(temp, 1) + ", \"humidity\": " + String(hum, 1) + "}";
  server.send(200, "application/json", response);
}

void setup() {
  Serial.begin(115200);
  dht.begin();

  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" connected!");
  Serial.println(WiFi.localIP());

  server.on("/temperature", HTTP_GET, handleTemperature);
  server.on("/humidity", HTTP_GET, handleHumidity);
  server.on("/", HTTP_GET, handleAll);
  server.begin();
}

void loop() {
  server.handleClient();
}
