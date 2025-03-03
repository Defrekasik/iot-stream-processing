import paho.mqtt.client as mqtt
import random
import time
import json

BROKER = "mqtt"
PORT = 1883
TOPIC = "sensor/data"

client = mqtt.Client()
client.connect(BROKER, PORT, 60)

# Начальные значения датчиков (10 штук)
sensor_values = {i: {"temperature": 25.0, "humidity": 50.0} for i in range(1, 11)}

def generate_sensor_data(sensor_id):
    """Генерация данных с редкими аномалиями."""
    global sensor_values

    # Обычные колебания (небольшие изменения)
    sensor_values[sensor_id]["temperature"] += random.uniform(-0.2, 0.2)
    sensor_values[sensor_id]["humidity"] += random.uniform(-0.5, 0.5)

    # Ограничиваем в нормальных пределах
    sensor_values[sensor_id]["temperature"] = max(20.0, min(30.0, sensor_values[sensor_id]["temperature"]))
    sensor_values[sensor_id]["humidity"] = max(40.0, min(80.0, sensor_values[sensor_id]["humidity"]))

    # 1% вероятность аномального скачка
    if random.random() < 0.01:
        sensor_values[sensor_id]["temperature"] += random.uniform(-2, 2)  # Мягкий скачок
        sensor_values[sensor_id]["humidity"] += random.uniform(-5, 5)

    # Окончательные границы (чтобы значения не были нереалистичными)
    sensor_values[sensor_id]["temperature"] = max(0.0, min(50.0, sensor_values[sensor_id]["temperature"]))
    sensor_values[sensor_id]["humidity"] = max(10.0, min(90.0, sensor_values[sensor_id]["humidity"]))

    return {
        "sensor_id": sensor_id,
        "temperature": round(sensor_values[sensor_id]["temperature"], 2),
        "humidity": round(sensor_values[sensor_id]["humidity"], 2),
        "timestamp": time.time()
    }

while True:
    for sensor_id in range(1, 11):  # 10 датчиков
        data = generate_sensor_data(sensor_id)
        client.publish(TOPIC, json.dumps(data))
        print("Sent:", data)
        time.sleep(0.1)  # Задержка для плавности

    time.sleep(1)  # Пауза перед следующим циклом
