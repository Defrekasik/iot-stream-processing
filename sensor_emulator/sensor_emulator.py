import paho.mqtt.client as mqtt
import random
import time
import json

BROKER = "mqtt"
PORT = 1883
TOPIC = "sensor/data"

client = mqtt.Client()
client.connect(BROKER, PORT, 60)

def generate_sensor_data():
    return {
        "sensor_id": random.randint(1, 10),
        "temperature": round(random.uniform(20.0, 30.0), 2),
        "humidity": round(random.uniform(30.0, 60.0), 2),
        "timestamp": time.time()
    }

while True:
    data = generate_sensor_data()
    client.publish(TOPIC, json.dumps(data))
    print("Sent:", data)
    time.sleep(1)

