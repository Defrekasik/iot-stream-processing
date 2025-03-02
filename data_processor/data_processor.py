import paho.mqtt.client as mqtt
import json

BROKER = "mqtt"
PORT = 1883
TOPIC = "sensor/data"

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode("utf-8"))
    print(f"Received: {data}")

client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.subscribe(TOPIC)

print("Waiting for messages...")
client.loop_forever()

