#include <WiFi.h>
#include <WebServer.h>
#include "secrets.h"

WebServer server(80);
bool relayState = false;

void handleState() {
server.send(200, "application/json", String("{\"state\": \"") + (relayState ? "on" : "off") + "\"}");
}

void handleRelay() {
  if (server.hasArg("plain")) {
    String body = server.arg("plain");
    if (body == "on") {
      digitalWrite(RELAY_PIN, HIGH);
      relayState = true;
    } else if (body == "off") {
      digitalWrite(RELAY_PIN, LOW);
      relayState = false;
    }
    server.send(200, "application/json", "{\"status\":\"OK\"}");
  } else {
    server.send(400, "application/json", "{\"error\":\"Missing body\"}");
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);

  Serial.println();
  Serial.print("Connecting to WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  Serial.println("SUCCESSFUL");
  Serial.println(WiFi.localIP());

  server.on("/state", HTTP_GET, handleState);
  server.on("/relay", HTTP_POST, handleRelay);
  server.begin();
}

void loop() {
  server.handleClient();
}
