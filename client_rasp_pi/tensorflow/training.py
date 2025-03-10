import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
import matplotlib.pyplot as plt
import os

# === 1. Generate Synthetic Normal Sensor Data ===
np.random.seed(42)

# Base values from your data stream
BASE_TEMP = 23.2
BASE_HUMIDITY = 42.8

# Generate 1000 normal samples with minimal variance
temperature_data = np.random.normal(BASE_TEMP, 0.2, 1000)
humidity_data = np.random.normal(BASE_HUMIDITY, 0.5, 1000)

# Combine into a feature matrix
X_train = np.column_stack((temperature_data, humidity_data))

print(f"Training data shape: {X_train.shape}")

# === 2. Build a Simple Autoencoder ===
input_dim = X_train.shape[1]  # 2 features: temperature, humidity
encoding_dim = 2  # compressed representation

# Define the model
input_layer = layers.Input(shape=(input_dim,))
encoded = layers.Dense(encoding_dim, activation='relu')(input_layer)
decoded = layers.Dense(input_dim, activation='linear')(encoded)

autoencoder = models.Model(inputs=input_layer, outputs=decoded)

autoencoder.compile(optimizer='adam', loss='mse')

autoencoder.summary()

# === 3. Train the Autoencoder ===
history = autoencoder.fit(
    X_train, X_train,
    epochs=50,
    batch_size=16,
    shuffle=True,
    validation_split=0.1,
    verbose=1
)

# === 4. Plot Training Loss (optional) ===
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.legend()
plt.title("Autoencoder Training Loss")
plt.xlabel("Epochs")
plt.ylabel("Loss (MSE)")
plt.show()

# === 5. Calculate Reconstruction Losses ===
reconstructions = autoencoder.predict(X_train)
mse = np.mean(np.power(X_train - reconstructions, 2), axis=1)

# Set threshold at the 95th percentile of MSE
threshold = np.percentile(mse, 95)
print(f"Anomaly Detection Threshold (95 percentile): {threshold}")

# === 6. Save Threshold Value ===
with open("anomaly_threshold.txt", "w") as f:
    f.write(str(threshold))
print("Threshold saved to anomaly_threshold.txt")

# === 7. Convert Autoencoder Model to TensorFlow Lite ===
converter = tf.lite.TFLiteConverter.from_keras_model(autoencoder)
tflite_model = converter.convert()

# Create an output directory
os.makedirs("output", exist_ok=True)

# Save the TFLite model
tflite_model_path = "output/autoencoder_anomaly.tflite"
with open(tflite_model_path, "wb") as f:
    f.write(tflite_model)

print(f"TFLite model saved to {tflite_model_path}")

print("\n✅ Training complete! Ready for inference.")
