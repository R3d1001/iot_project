import time
import random
import json
import numpy as np
import tensorflow as tf

# === 1. Load TFLite Model ===
interpreter = tf.lite.Interpreter(model_path="tensorflow/output/autoencoder_anomaly.tflite")
interpreter.allocate_tensors()

# Get input and output tensor details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# === 2. Load Anomaly Detection Threshold ===
with open("tensorflow/output/anomaly_threshold.txt", "r") as f:
    threshold = float(f.read())

print(f"✅ Loaded TFLite model and threshold ({threshold})")

# === 3. Base reference values for simulation ===
base_temperature = 23.2
base_humidity = 42.8
air_quality_options = ["Normal Air", "High Pollution Detected!"]

# Timer to introduce anomalies every 30 seconds
start_time = time.time()

# === 4. Fake data streaming + anomaly detection loop ===
while True:
    current_time = time.time()

    # === Generate normal sensor data ===
    temperature = round(base_temperature + random.uniform(-0.2, 0.2), 1)
    humidity = round(base_humidity + random.uniform(-0.5, 0.5), 1)

    # === Introduce an Anomaly Spike Every 30 Seconds ===
    if int(current_time - start_time) % 30 == 0:
        print("⚠️ Simulating Anomaly Spike!")
        temperature += random.uniform(2.5, 4.0)  # Big jump in temperature
        humidity += random.uniform(5.0, 8.0)  # Big jump in humidity

    air_quality = "Normal Air"  # Keeping it static

    # Create sensor data payload
    sensor_data = {
        "temperature": temperature,
        "humidity": humidity,
        "air_quality": air_quality
    }

    # === Prepare input for TFLite inference ===
    input_data = np.array([[temperature, humidity]], dtype=np.float32)

    # Run inference
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    reconstructed = interpreter.get_tensor(output_details[0]['index'])

    # === Calculate reconstruction error (MSE) ===
    mse = np.mean(np.power(input_data - reconstructed, 2))

    # === Determine if it's an anomaly ===
    if mse > threshold:
        status = "🚨 Anomaly Detected!"
    else:
        status = "✅ Normal"

    # === Print results ===
    print(f"📤 Published: {sensor_data} | MSE: {mse:.5f} | {status}")

    # Wait 1 second
    time.sleep(1)
