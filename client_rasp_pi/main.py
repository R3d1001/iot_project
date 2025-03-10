import Adafruit_DHT
import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
import json
import numpy as np
import tensorflow as tf

# === 1. Setup DHT22 and MQ-135 ===
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_GPIO = 4
MQ135_GPIO = 27

# === 2. MQTT Broker Settings ===
MQTT_BROKER = "90b29742af9a4082b6ba911301a453be.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USER = "abcd1234"
MQTT_PASSWORD = "Abcd1234"
MQTT_TOPIC = "esp32/dht11"

# === 3. Setup GPIO ===
GPIO.setmode(GPIO.BCM)
GPIO.setup(MQ135_GPIO, GPIO.IN)

# === 4. MQTT Callback ===
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to HiveMQ!")
    else:
        print(f"❌ Connection failed with code {rc}")

# === 5. Setup MQTT Client ===
client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
client.tls_set()
client.on_connect = on_connect

# Connect to broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

# === 6. Load TFLite Model for Anomaly Detection ===
interpreter = tf.lite.Interpreter(model_path="tensorflow/output/autoencoder_anomaly.tflite")
interpreter.allocate_tensors()

# Get input/output details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# === 7. Load Anomaly Threshold ===
with open("tensorflow/output/anomaly_threshold.txt", "r") as f:
    threshold = float(f.read())

print(f"✅ Anomaly Detection Threshold Loaded: {threshold}")

# === 8. Continuous Data Collection + Inference + Publishing ===
while True:
    # === Read DHT22 Data ===
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_GPIO)

    if humidity is None or temperature is None:
        print("⚠️ Failed to read sensor data. Retrying...")
        time.sleep(2)
        continue

    # === Read Air Quality (MQ-135) ===
    air_quality_status = "Normal Air" if GPIO.input(MQ135_GPIO) == GPIO.HIGH else "High Pollution Detected!"

    # === Prepare Data for Anomaly Detection ===
    input_data = np.array([[temperature, humidity]], dtype=np.float32)

    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    reconstructed = interpreter.get_tensor(output_details[0]['index'])

    # Calculate reconstruction error (MSE)
    mse = np.mean(np.power(input_data - reconstructed, 2))

    # Check anomaly status
    if mse > threshold:
        anomaly_status = "Anomaly"
        alert = "🚨 Anomaly Detected!"
    else:
        anomaly_status = "Normal"
        alert = "✅ Normal"

    # === Create JSON Payload ===
    sensor_data = {
        "temperature": round(temperature, 2),
        "humidity": round(humidity, 2),
        "air_quality": air_quality_status,
        "status": anomaly_status
    }

    # === Publish to MQTT ===
    client.publish(MQTT_TOPIC, json.dumps(sensor_data))
    print(f"📤 Published: {sensor_data} | MSE: {mse:.5f} | {alert}")

    # Wait before next read
    time.sleep(5)  # Every 5 seconds
