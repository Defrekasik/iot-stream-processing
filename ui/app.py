from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)

def create_table():
    # Подключение к базе данных PostgreSQL
    conn = psycopg2.connect("dbname=sensor_data user=admin password=secret host=postgres")
    cur = conn.cursor()
    
    # SQL-запрос для создания таблицы, если она не существует
    create_table_query = """
    CREATE TABLE IF NOT EXISTS sensor_readings (
        id SERIAL PRIMARY KEY,
        sensor_id INTEGER,
        temperature FLOAT,
        humidity FLOAT,
        timestamp TIMESTAMP
    );
    """
    
    cur.execute(create_table_query)
    conn.commit()
    conn.close()

def get_data():
    # Подключение к базе данных PostgreSQL
    conn = psycopg2.connect("dbname=sensor_data user=admin password=secret host=postgres")
    cur = conn.cursor()
    
    # Запрос к базе данных для получения последних 100 записей
    cur.execute("SELECT * FROM sensor_readings ORDER BY timestamp DESC LIMIT 100")
    data = cur.fetchall()
    
    conn.close()
    return data

@app.route("/data")
def data():
    # Возвращает данные в формате JSON
    return jsonify(get_data())

if __name__ == "__main__":
    # Создание таблицы перед запуском приложения
    create_table()
    
    # Запуск приложения Flask на порту 5000
    app.run(host="0.0.0.0", port=5000)

