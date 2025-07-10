#include <WiFi.h>
#include <WebServer.h>
#include "secrets.h"

WebServer server(80);

String relayState = "off";

void handleGetState() {
  server.send(200, "application/json", "{\"state\": \"" + relayState + "\"}");
}

void handlePostRelay() {
  if (server.hasArg("plain") == false) {
    server.send(400, "application/json", "{\"error\": \"No body\"}");
    return;
  }

  String body = server.arg("plain");
  if (body.indexOf("\"state\":\"on\"") != -1) {
    digitalWrite(RELAY_PIN, HIGH);
    relayState = "on";
  } else if (body.indexOf("\"state\":\"off\"") != -1) {
    digitalWrite(RELAY_PIN, LOW);
    relayState = "off";
  } else {
    server.send(400, "application/json", "{\"error\": \"Invalid state\"}");
    return;
  }

  server.send(200, "application/json", "{\"state\": \"" + relayState + "\"}");
}

void setup() {
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);

  Serial.begin(115200);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" connected!");
  Serial.println(WiFi.localIP());

  server.on("/state", HTTP_GET, handleGetState);
  server.on("/relay", HTTP_POST, handlePostRelay);
  server.begin();
}

void loop() {
  server.handleClient();
}