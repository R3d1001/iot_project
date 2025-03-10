import ssl
import time
import json
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# HiveMQ Cloud MQTT Credentials
MQTT_BROKER = "yoururl.s1.eu.hivemq.cloud"
MQTT_PORT = 8883  # Secure MQTT (TLS)
MQTT_USER = "abcd1234"
MQTT_PASSWORD = "Abcd1234"
MQTT_TOPICS = [("pi_data", 0), ("esp32/dustsensor", 0)]  # Topics to subscribe

# InfluxDB Config
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "mytoken"
INFLUX_ORG = "myorg"
INFLUX_BUCKET = "project"

# Initialize InfluxDB Client
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

# ✅ Fixed on_connect function signature
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connected to HiveMQ Cloud successfully!")
        client.subscribe(MQTT_TOPICS)
    else:
        print(f"Connection failed with reason code {reason_code}")

def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload = msg.payload.decode("utf-8")

        print(f"Received message on {topic}: {payload}")

        # Parse JSON payload
        data = json.loads(payload)

        # Create an InfluxDB point
        point = Point("sensor_data").tag("topic", topic)

        # Add each field dynamically (only numeric values)
        for key, value in data.items():
            if isinstance(value, (int, float)):
                point = point.field(key, value)

        # Write to InfluxDB
        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
        print(f"Written to InfluxDB: {topic} -> {data}")

    except json.JSONDecodeError:
        print(f"Error: Received invalid JSON format: {payload}")
    except Exception as e:
        print(f"Error processing message: {e}")

# MQTT Client Setup
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # ✅ Fixes deprecation warning
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
mqtt_client.tls_set(cert_reqs=ssl.CERT_NONE)  # Use SSL but ignore verification
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Connect to HiveMQ Cloud
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()

# Keep script running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Disconnecting...")
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    write_api.close()
    client.close()
    print("Exited gracefully.")
