# Installation & Setup Guide

## 1. Install Arduino IDE
- Download and install **Arduino IDE** from [official Arduino website](https://www.arduino.cc/en/software).
- Install **ESP32 board support**:
  - Open **Preferences** and add the following URL in the "Additional Board Manager URLs":
    ```
    https://dl.espressif.com/dl/package_esp32_index.json
    ```
  - Go to **Board Manager**, search for "ESP32", and install the package.

## 2. Set Up Raspberry Pi
- Install **Raspberry Pi OS** using **Raspberry Pi Imager**.
- Enable SSH for remote access.
- Install **Python 3** and required libraries:
  ```bash
  sudo apt update && sudo apt upgrade -y
  sudo apt install python3-pip -y
  pip3 install paho-mqtt influxdb-client
  ```

## 3. Install Docker & Docker Compose on Raspberry Pi
- Install **Docker**:
  ```bash
  curl -fsSL https://get.docker.com | sh
  sudo usermod -aG docker $USER
  ```
- Install **Docker Compose**:
  ```bash
  sudo apt install docker-compose -y
  ```

## 4. Run InfluxDB & Grafana with Docker Compose
- Create a `docker-compose.yml` file:
  ```yaml
  version: '3'
  services:
    influxdb:
      image: influxdb:latest
      container_name: influxdb
      ports:
        - "8086:8086"
      environment:
        - INFLUXDB_DB=air_quality
        - INFLUXDB_ADMIN_USER=admin
        - INFLUXDB_ADMIN_PASSWORD=adminpass
      volumes:
        - influxdb_data:/var/lib/influxdb

    grafana:
      image: grafana/grafana
      container_name: grafana
      ports:
        - "3000:3000"
      environment:
        - GF_SECURITY_ADMIN_PASSWORD=admin
      volumes:
        - grafana_data:/var/lib/grafana

  volumes:
    influxdb_data:
    grafana_data:
  ```
- Run the containers:
  ```bash
  docker-compose up -d
  ```

## 5. Run `main.py` on Raspberry Pi
- Navigate to the `client_rasp_pi` directory:
  ```bash
  cd ~/iot_project/client_rasp_pi
  ```
- Run the script to collect sensor data:
  ```bash
  python3 main.py
  ```

## 6. Program ESP32 with Arduino IDE
- Open `esp32_dustsensor.ino` in Arduino IDE.
- Select the **ESP32** board and the correct **COM port**.
- Install required libraries (`PubSubClient`, `WiFi`, etc.).
- Upload the sketch to the ESP32 to start reading dust sensor data and send it to **HiveMQTTFX**.

## 7. Run `server.py` to Process Data
- Navigate to the project directory:
  ```bash
  cd ~/iot_project/server
  ```
- Run the server script to fetch MQTT data and store it in **InfluxDB**:
  ```bash
  python3 server.py
  ```

## 8. Visualize Data in Grafana
- Access **Grafana** in a browser: `http://<raspberry-pi-ip>:3000`
- Login with:
  - **Username:** `admin`
  - **Password:** `admin`
- Add **InfluxDB** as a data source:
  - URL: `http://influxdb:8086`
  - Database: `air_quality`
- Create dashboards and visualize real-time IAQ data.




# Smart Air Quality & Ventilation Monitoring Project Report

## Problem Statement
Indoor air quality (IAQ) is a crucial factor affecting the health, comfort, and productivity of individuals in enclosed environments such as classrooms. Poor IAQ, caused by high levels of particulate matter (PM2.5), volatile organic compounds (VOCs), and inadequate ventilation, can lead to respiratory issues, fatigue, and reduced cognitive performance. This project aims to develop a smart air quality and ventilation monitoring system that provides real-time IAQ insights and predictive alerts.

## Proposed Solution
The proposed solution involves deploying an IoT-based monitoring system that continuously tracks temperature, humidity, PM2.5 levels, and VOC concentrations. The system utilizes machine learning (ML) models to predict deteriorating air quality conditions and provides recommendations for ventilation adjustments. Real-time and historical air quality data will be visualized through an interactive dashboard.

## Hardware & Software Details
### Hardware:
- **DHT22** – Temperature & Humidity Sensor
- **GP2y10** – Airborne Dust particulate matter detection
- **VOC Sensor (MQ-135)** – Volatile organic compound monitoring
- **Raspberry Pi 4-B** – Central processing unit
- **ESP32** – Wireless sensor nodes for data collection

### Software & Technology Stack:
- **InfluxDB** – Time-series database for air quality data logging
- **ThingsCloud** – IoT device management and cloud connectivity
- **Grafana** – Real-time dashboard for data visualization
- **TensorFlow Lite (AutoML)** – Machine learning model for air quality prediction
- **Edge Impulse** – AI processing on Raspberry Pi for real-time insights

## Implementation Steps
1. **Sensor Deployment:**
   - Install DHT22, PM2.5, and VOC sensors in classrooms.
   - Connect ESP32 modules to collect sensor data and transmit it to Raspberry Pi.
   
2. **Data Processing & Storage:**
   - Configure Raspberry Pi to aggregate real-time data from ESP32 sensors.
   - Store time-series data in InfluxDB.
   
3. **Machine Learning & Predictions:**
   - Train a TensorFlow Lite model on historical IAQ data to predict deteriorating air quality conditions.
   - Deploy the trained model on Raspberry Pi for real-time inference.
   
4. **Visualization & Alerts:**
   - Set up a Grafana dashboard for real-time monitoring and trend analysis.
   - Implement threshold-based alerts for poor air quality notifications.

5. **Testing & Optimization:**
   - Validate sensor accuracy and calibrate ML predictions.
   - Optimize power consumption and network efficiency for seamless operation.

## Results & Insights
- **Real-time air quality monitoring:** Successful tracking of temperature, humidity, and pollutant levels.
- **Predictive modeling:** ML models accurately forecasted periods of poor IAQ, allowing proactive ventilation adjustments.
- **User-friendly visualization:** Grafana dashboard displayed easy-to-interpret air quality trends and alerts.
- **Improved ventilation control:** The system provided actionable insights to optimize ventilation for better indoor air quality.

## Challenges Faced & Future Improvements
### Challenges:
- **Sensor Calibration:** PM2.5 and VOC sensors required recalibration to ensure accuracy.
- **Connectivity Issues:** Wireless communication between ESP32 nodes occasionally dropped.
- **Data Storage Optimization:** Efficiently managing large volumes of time-series data in InfluxDB.


### Future Improvements:
- **Integration with HVAC Systems:** Automate ventilation control based on IAQ insights.
- **Extended Deployment:** Expand the system to multiple buildings for a broader impact.
- **Mobile Application Support:** Develop a mobile app for remote IAQ monitoring and alert notifications.

This project provides a cost-effective, scalable solution for improving indoor air quality through real-time monitoring and predictive analytics.

# Below are some screenshots of the project
## A spike was seen and it was above the threshold hence flagged by ML
![<img src="https://raw.githubusercontent.com/R3d1001/iot_project/refs/heads/main/ml1.jpeg" alt="ML1" width="500">]

## Again a spike was seen but within MSE threshold
![<img src="https://raw.githubusercontent.com/R3d1001/iot_project/refs/heads/main/ml2.jpeg" alt="ML2" width="500">]

## Below is the grafana dashboard for monitoring all the values and detecting mean, last value and anomolies
![<img src="https://raw.githubusercontent.com/R3d1001/iot_project/refs/heads/main/grafana dashboard.png" alt="ML1" width="500">]

## Drive link for the videos of the iot sensors and raspberry pi
### https://drive.google.com/drive/folders/1RIWC57bZ8VgbIktY3kUbpnkH0SX6o98l?usp=sharing
