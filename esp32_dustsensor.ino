#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>

// WiFi Credentials
const char* ssid = "TP-Link_71CA";
const char* password = "51064662";

// HiveMQ Cloud MQTT Credentials
const char* mqtt_server = "90b29742af9a4082b6ba911301a453be.s1.eu.hivemq.cloud";
const int mqtt_port = 8883;  // Secure MQTT (TLS)
const char* mqtt_user = "abcd1234";
const char* mqtt_password = "Abcd1234";

// MQTT Topic
const char* mqtt_topic_dust = "esp32/dustsensor";

// GP2Y10 Sensor Pins
#define LED_PIN 16      // LED Control
#define SENSOR_PIN 34   // GP2Y10 Analog Output

// Secure WiFi & MQTT Clients
WiFiClientSecure espClient;
PubSubClient client(espClient);

void setup_wifi() {
    Serial.print("Connecting to WiFi...");
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi Connected.");
}

void reconnect_mqtt() {
    while (!client.connected()) {
        Serial.print("Connecting to MQTT...");
        espClient.setInsecure();  // Skip TLS certificate validation
        if (client.connect("ESP32_Dust", mqtt_user, mqtt_password)) {
            Serial.println("Connected to MQTT!");
        } else {
            Serial.print("Failed, retrying...");
            delay(5000);
        }
    }
}

void setup() {
    Serial.begin(115200);
    setup_wifi();

    // MQTT Setup
    espClient.setInsecure();  // Ignore SSL cert verification
    client.setServer(mqtt_server, mqtt_port);

    pinMode(LED_PIN, OUTPUT);
}

void loop() {
    if (!client.connected()) {
        reconnect_mqtt();
    }
    client.loop();

    // Read Dust Sensor
    digitalWrite(LED_PIN, LOW);  // Turn LED ON
    delayMicroseconds(280);  // Recommended timing
    int dust_value = analogRead(SENSOR_PIN);  // Read analog output
    digitalWrite(LED_PIN, HIGH);  // Turn LED OFF

    // Publish data to MQTT
    String payload = "{\"dust_level\": " + String(dust_value) + "}";
    Serial.println("Publishing: " + payload);
    client.publish(mqtt_topic_dust, payload.c_str());

    delay(1000);  // Send data every 5 seconds
}
