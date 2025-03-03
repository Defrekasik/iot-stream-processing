import paho.mqtt.client as mqtt
import json
import psycopg2
import time

# Настройки MQTT
BROKER = "mqtt"
PORT = 1883
TOPIC = "sensor/data"

# Функция для подключения к базе данных с повторной попыткой
def connect_to_db():
    while True:
        try:
            print("Attempting to connect to PostgreSQL...")
            conn = psycopg2.connect(
                dbname="sensor_data", user="admin", password="secret", host="postgres"
            )
            print("Connected to the database.")
            return conn
        except Exception as e:
            print(f"Error connecting to database: {e}. Retrying in 5 seconds...")
            time.sleep(5)  # Ждем 5 секунд перед повторной попыткой

# Функция, которая будет вызываться при получении сообщения
def on_message(client, userdata, msg):
    try:
        # Получаем данные и выводим их
        data = json.loads(msg.payload.decode("utf-8"))
        print(f"Received data: {data}")

        # Подключение к базе данных
        conn = connect_to_db()

        # Открытие курсора и выполнение запроса
        with conn.cursor() as cur:
            # Подготовка SQL запроса для вставки данных
            query = """
            INSERT INTO sensor_readings (sensor_id, temperature, humidity, timestamp)
            VALUES (%s, %s, %s, to_timestamp(%s))
            """
            print(f"Inserting data into the database: {data}")
            cur.execute(
                query,
                (data["sensor_id"], data["temperature"], data["humidity"], data["timestamp"])
            )

            # Подтверждаем изменения
            conn.commit()
            print("Data inserted successfully!")

    except Exception as e:
        print(f"Error during message processing: {e}")
        
    finally:
        # Закрытие соединения
        if conn:
            conn.close()

# Настройка MQTT клиента
client = mqtt.Client()
client.on_message = on_message

# Подключаемся к MQTT брокеру
try:
    print("Connecting to MQTT broker...")
    client.connect(BROKER, PORT, 60)
    print("Connected to MQTT broker.")
except Exception as e:
    print(f"Error connecting to MQTT broker: {e}")
    exit(1)

# Подписываемся на топик
client.subscribe(TOPIC)

# Запуск обработки сообщений
print("Waiting for messages...")
client.loop_forever()

