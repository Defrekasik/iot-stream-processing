import paho.mqtt.client as mqtt
import json
import psycopg2

# Настройки MQTT
BROKER = "mqtt"
PORT = 1883
TOPIC = "sensor/data"

# Функция, которая будет вызываться при получении сообщения
def on_message(client, userdata, msg):
    try:
        # Получаем данные и выводим их
        data = json.loads(msg.payload.decode("utf-8"))
        print(f"Received: {data}")

        # Подключение к базе данных
        conn = psycopg2.connect(
            dbname="sensor_data", user="admin", password="secret", host="postgres"
        )

        # Открытие курсора и выполнение запроса
        with conn.cursor() as cur:
            # Подготовка SQL запроса для вставки данных
            query = """
            INSERT INTO sensor_readings (sensor_id, temperature, humidity, timestamp)
            VALUES (%s, %s, %s, to_timestamp(%s))
            """
            cur.execute(
                query,
                (data["sensor_id"], data["temperature"], data["humidity"], data["timestamp"])
            )

            # Подтверждаем изменения
            conn.commit()
            print("Data inserted successfully!")

    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        # Закрытие соединения
        if conn:
            conn.close()

# Настройка MQTT клиента
client = mqtt.Client()
client.on_message = on_message

# Подключаемся к MQTT брокеру
client.connect(BROKER, PORT, 60)

# Подписываемся на топик
client.subscribe(TOPIC)

# Запуск обработки сообщений
print("Waiting for messages...")
client.loop_forever()

