from flask import Flask, jsonify
import psycopg2
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

app = Flask(__name__)

# Инициализация Dash
dash_app = dash.Dash(__name__, server=app, routes_pathname_prefix="/dashboard/")

# Функция получения данных из базы
def get_data():
    conn = psycopg2.connect("dbname=sensor_data user=admin password=secret host=postgres")
    cur = conn.cursor()
    
    # Запросим данные за последние 30 минут
    cur.execute("""
        SELECT * FROM sensor_readings 
        WHERE timestamp >= NOW() - INTERVAL '30 minutes'
        ORDER BY timestamp ASC
    """)
    
    data = cur.fetchall()
    conn.close()

    # Преобразуем данные в DataFrame
    df = pd.DataFrame(data, columns=["id", "sensor_id", "temperature", "humidity", "timestamp"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])  # Конвертируем в datetime

    return df

# Маршрут для получения данных в формате JSON
@app.route('/data')
def data():
    df = get_data()
    return jsonify(df.to_dict(orient='records'))

# Макет Dash
dash_app.layout = html.Div([
    html.H1("IoT Sensor Dashboard"),
    
    # График для температуры
    dcc.Graph(id="temperature-graph"),
    
    # График для влажности
    dcc.Graph(id="humidity-graph"),
    
    dcc.Interval(
        id="interval-component",
        interval=3000,  # Обновление каждые 3 секунды
        n_intervals=0
    )
])

# Обновление графиков
@dash_app.callback(
    [Output("temperature-graph", "figure"),
     Output("humidity-graph", "figure")],
    Input("interval-component", "n_intervals")
)
def update_graph(n):
    df = get_data()
    
    if df.empty:
        return go.Figure(), go.Figure()

    # Группируем данные по sensor_id
    temp_fig = go.Figure()
    humidity_fig = go.Figure()

    for sensor_id, sensor_data in df.groupby("sensor_id"):
        temp_fig.add_trace(go.Scatter(
            x=sensor_data["timestamp"], 
            y=sensor_data["temperature"], 
            mode="lines", 
            name=f"Температура (датчик {sensor_id})"
        ))
        
        humidity_fig.add_trace(go.Scatter(
            x=sensor_data["timestamp"], 
            y=sensor_data["humidity"], 
            mode="lines", 
            name=f"Влажность (датчик {sensor_id})"
        ))

    # Настройки графиков
    temp_fig.update_layout(
        title="Температура (все датчики)",
        xaxis_title="Время",
        yaxis_title="Температура (°C)",
        yaxis=dict(range=[0, 50]),  # Устанавливаем диапазон Y
        template="plotly_dark",
        xaxis=dict(tickformat="%H:%M:%S")
    )

    humidity_fig.update_layout(
        title="Влажность (все датчики)",
        xaxis_title="Время",
        yaxis_title="Влажность (%)",
        yaxis=dict(range=[40, 80]),  # Устанавливаем диапазон Y
        template="plotly_dark",
        xaxis=dict(tickformat="%H:%M:%S")
    )

    return temp_fig, humidity_fig

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
