import os
import threading
import time
import datetime
import requests
from flask import Flask, render_template, jsonify, request
import database
import config
import ml_model
import iot_sensor_pipeline
from logger import system_log

app = Flask(__name__)

# Track last training time to avoid excessive CPU usage
LAST_TRAINED_TIME = 0.0
TRAIN_COOLDOWN_SECONDS = 300 # 5 minutes

def background_sensor_loop():
    """Background thread function that runs the IoT sensor data pipeline."""
    print("[Flask Thread] Initializing background sensor pipeline...")
    # Seed/init the database first
    database.init_db()
    # Train the ML model initially
    print("[Flask Thread] Running initial ML model training...")
    ml_model.train_forecasting_model()
    
    # Run the polling loop
    pipeline = iot_sensor_pipeline.SensorPipeline()
    pipeline.run_loop()

def start_background_threads():
    """Starts background threads for sensor polling if not already running."""
    # Flask in debug mode runs startup code twice due to auto-reloader.
    # WERKZEUG_RUN_MAIN ensures we only spawn the thread in the main process.
    is_main_process = os.environ.get("WERKZEUG_RUN_MAIN") == "true"
    is_debug = app.debug
    
    if is_main_process or not is_debug:
        thread = threading.Thread(target=background_sensor_loop, daemon=True)
        thread.start()
        print("[Flask] Spawned background sensor pipeline thread.")

def get_nearest_city(lat, lon):
    """Finds the nearest major city from a predefined list to provide clean city/country names in simulated mode."""
    cities = [
        {"name": "Parma", "country": "IT", "lat": 44.8015, "lon": 10.3279},
        {"name": "Rome", "country": "IT", "lat": 41.9028, "lon": 12.4964},
        {"name": "Milan", "country": "IT", "lat": 45.4642, "lon": 9.1900},
        {"name": "London", "country": "GB", "lat": 51.5074, "lon": -0.1278},
        {"name": "Paris", "country": "FR", "lat": 48.8566, "lon": 2.3522},
        {"name": "Berlin", "country": "DE", "lat": 52.5200, "lon": 13.4050},
        {"name": "Madrid", "country": "ES", "lat": 40.4168, "lon": -3.7038},
        {"name": "Athens", "country": "GR", "lat": 37.9838, "lon": 23.7275},
        {"name": "New York", "country": "US", "lat": 40.7128, "lon": -74.0060},
        {"name": "Los Angeles", "country": "US", "lat": 34.0522, "lon": -118.2437},
        {"name": "Chicago", "country": "US", "lat": 41.8781, "lon": -87.6298},
        {"name": "Toronto", "country": "CA", "lat": 43.6532, "lon": -79.3832},
        {"name": "Tokyo", "country": "JP", "lat": 35.6762, "lon": 139.6503},
        {"name": "Beijing", "country": "CN", "lat": 39.9042, "lon": 116.4074},
        {"name": "Shanghai", "country": "CN", "lat": 31.2304, "lon": 121.4737},
        {"name": "Mumbai", "country": "IN", "lat": 19.0760, "lon": 72.8777},
        {"name": "Delhi", "country": "IN", "lat": 28.6139, "lon": 77.2090},
        {"name": "Sydney", "country": "AU", "lat": -33.8688, "lon": 151.2093},
        {"name": "Cairo", "country": "EG", "lat": 30.0444, "lon": 31.2357},
        {"name": "Moscow", "country": "RU", "lat": 55.7558, "lon": 37.6173},
        {"name": "Dubai", "country": "AE", "lat": 25.2048, "lon": 55.2708},
        {"name": "Rio de Janeiro", "country": "BR", "lat": -22.9068, "lon": -43.1729},
        {"name": "Buenos Aires", "country": "AR", "lat": -34.6037, "lon": -58.3816},
        {"name": "Cape Town", "country": "ZA", "lat": -33.9249, "lon": 18.4241},
        {"name": "Singapore", "country": "SG", "lat": 1.3521, "lon": 103.8198}
    ]
    nearest = cities[0]
    min_dist = float('inf')
    for c in cities:
        dist = (c["lat"] - lat)**2 + (c["lon"] - lon)**2
        if dist < min_dist:
            min_dist = dist
            nearest = c
    return nearest

def get_simulated_weather(lat, lon):
    """
    Generates high-quality simulated weather data based on coordinate geography 
    and diurnal local time. Used as a fallback when OpenWeatherMap is unconfigured.
    """
    now = datetime.datetime.now()
    hour = now.hour
    
    # Estimate timezone offset from longitude (15 degrees ~ 1 hour)
    estimated_tz_offset = round(lon / 15.0)
    local_hour = (hour + estimated_tz_offset) % 24
    
    # Latitude-based base temperature (colder at poles, warmer near equator)
    # 0 at equator -> base 28C, 90 at poles -> base -15C
    abs_lat = abs(lat)
    base_temp = 28.0 - (abs_lat * 0.45)
    
    # Diurnal temperature cycle (warmest in afternoon, coolest in morning)
    diurnal_offset = 5.0 * math.sin(2 * math.pi * (local_hour - 9) / 24.0) if 'math' in globals() else 5.0 * (local_hour - 9)/12
    # Ensure math is imported inside function just in case
    import math
    diurnal_offset = 5.0 * math.sin(2 * math.pi * (local_hour - 9) / 24.0)
    
    temp = base_temp + diurnal_offset + random.uniform(-1.0, 1.0) if 'random' in globals() else base_temp + diurnal_offset
    import random
    temp = base_temp + diurnal_offset + random.uniform(-1.0, 1.0)
    temp = round(max(-30.0, min(50.0, temp)), 1)
    
    # Humidity (inverse relationship with temp)
    humidity = 60.0 - (diurnal_offset * 2.5) + random.uniform(-5.0, 5.0)
    humidity = round(max(10.0, min(98.0, humidity)))
    
    # Determine general weather description
    if abs_lat > 60:
        main_weather = "Snow" if temp <= 0 else "Clouds"
        description = "light snow" if temp <= 0 else "overcast clouds"
    elif humidity > 75:
        main_weather = "Rain"
        description = "moderate rain" if random.random() > 0.5 else "light drizzle"
    elif humidity > 55:
        main_weather = "Clouds"
        description = "broken clouds" if random.random() > 0.5 else "few clouds"
    else:
        main_weather = "Clear"
        description = "clear sky"
        
    wind_speed = round(random.uniform(1.0, 8.0), 1)
    wind_deg = random.randint(0, 360)
    
    city_info = get_nearest_city(lat, lon)
    
    return {
        "coord": {"lat": lat, "lon": lon},
        "weather": [{"id": 800 if main_weather == "Clear" else 803, "main": main_weather, "description": description, "icon": "01d"}],
        "main": {
            "temp": temp,
            "feels_like": round(temp + (0.1 * wind_speed) - 0.5, 1),
            "humidity": humidity,
            "pressure": 1013
        },
        "wind": {
            "speed": wind_speed,
            "deg": wind_deg
        },
        "name": city_info["name"],
        "sys": {"country": city_info["country"]},
        "dt": int(time.time())
    }

@app.route('/favicon.ico')
def favicon():
    """Serves the favicon icon."""
    return app.send_static_file('AI.png')

@app.route('/')
def home():
    """Serves the main dashboard page."""
    return render_template('index.html')


@app.route('/api/realtime', methods=['GET'])
def get_realtime():
    """Returns the latest sensor readings from the SQLite database."""
    latest = database.get_latest_reading()
    if latest:
        # Calculate AQI for PM2.5 in backend and bundle it
        latest['aqi'] = ml_model.pm25_to_aqi(latest['pm2_5'])
        latest['device_name'] = config.DEVICE_NAME
        return jsonify(latest)
    else:
        return jsonify({"error": "No sensor readings available"}), 500

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Returns the recent system logs from the sensor pipeline."""
    return jsonify(system_log.get_logs())

@app.route('/api/history', methods=['GET'])
def get_history():
    """Returns historical readings to pre-populate the charts on startup."""
    limit = request.args.get('limit', default=50, type=int)
    history = database.get_recent_readings(limit=limit)
    return jsonify(history)
def map_wmo_code(code):
    """Maps WMO weather codes to OpenWeatherMap compatible weather conditions and icon bases."""
    mapping = {
        0: ("Clear", "clear sky", "01"),
        1: ("Clear", "mainly clear", "02"),
        2: ("Clouds", "partly cloudy", "03"),
        3: ("Clouds", "overcast", "04"),
        45: ("Fog", "foggy", "50"),
        48: ("Fog", "depositing rime fog", "50"),
        51: ("Drizzle", "light drizzle", "09"),
        53: ("Drizzle", "moderate drizzle", "09"),
        55: ("Drizzle", "dense drizzle", "09"),
        61: ("Rain", "light rain", "10"),
        63: ("Rain", "moderate rain", "10"),
        65: ("Rain", "heavy rain", "10"),
        71: ("Snow", "light snow", "13"),
        73: ("Snow", "moderate snow", "13"),
        75: ("Snow", "heavy snow", "13"),
        80: ("Rain", "light rain showers", "09"),
        81: ("Rain", "moderate rain showers", "09"),
        82: ("Rain", "heavy rain showers", "09"),
        95: ("Thunderstorm", "thunderstorm", "11"),
        96: ("Thunderstorm", "thunderstorm with light hail", "11"),
        99: ("Thunderstorm", "thunderstorm with heavy hail", "11"),
    }
    return mapping.get(code, ("Clouds", "broken clouds", "03"))

def get_open_meteo_weather(lat, lon):
    """Fetches accurate weather data from Open-Meteo free API and formats it in OpenWeatherMap structure."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,weather_code,pressure_msl,wind_speed_10m,wind_direction_10m",
        "timezone": "auto"
    }
    try:
        response = requests.get(url, params=params, timeout=4.0)
        if response.status_code == 200:
            data = response.json()
            current = data.get("current", {})
            wmo_code = current.get("weather_code", 0)
            main_weather, description, icon_base = map_wmo_code(wmo_code)
            
            wind_speed_kmh = current.get("wind_speed_10m", 0.0)
            wind_speed_ms = round(wind_speed_kmh / 3.6, 1)
            
            city_info = get_nearest_city(lat, lon)
            
            return {
                "coord": {"lat": lat, "lon": lon},
                "weather": [{
                    "id": 800 if main_weather == "Clear" else 803,
                    "main": main_weather,
                    "description": description,
                    "icon": f"{icon_base}d"
                }],
                "main": {
                    "temp": current.get("temperature_2m", 15.0),
                    "feels_like": current.get("apparent_temperature", current.get("temperature_2m", 15.0)),
                    "humidity": current.get("relative_humidity_2m", 60),
                    "pressure": current.get("pressure_msl", 1013)
                },
                "wind": {
                    "speed": wind_speed_ms,
                    "deg": current.get("wind_direction_10m", 0)
                },
                "name": city_info["name"],
                "sys": {"country": city_info["country"]},
                "dt": int(time.time())
            }
    except Exception as e:
        print(f"[Flask] Open-Meteo request failed: {e}")
    return None

@app.route('/api/weather', methods=['GET'])
def get_weather():
    """
    Fetches live weather data from OpenWeatherMap API based on query params.
    Falls back to Open-Meteo API or high-fidelity simulated weather if API key is unconfigured.
    """
    lat_param = request.args.get('lat')
    lon_param = request.args.get('lon')
    
    try:
        lat = float(lat_param) if lat_param is not None else config.DEFAULT_LAT
        lon = float(lon_param) if lon_param is not None else config.DEFAULT_LON
    except ValueError:
        lat = config.DEFAULT_LAT
        lon = config.DEFAULT_LON
        
    # Check if OpenWeatherMap API Key is configured
    if not config.OPENWEATHERMAP_API_KEY:
        # Attempt to get real weather from Open-Meteo (accurate keyless API)
        weather_data = get_open_meteo_weather(lat, lon)
        if weather_data:
            return jsonify(weather_data)
        # Return simulated weather if Open-Meteo fails
        return jsonify(get_simulated_weather(lat, lon))
        
    # Query OpenWeatherMap
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "units": "metric",
        "appid": config.OPENWEATHERMAP_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=5.0)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            print(f"[Flask] OpenWeatherMap returned status {response.status_code}: {response.text}")
            return jsonify(get_simulated_weather(lat, lon))
    except Exception as e:
        print(f"[Flask] OpenWeatherMap request failed: {e}")
        return jsonify(get_simulated_weather(lat, lon))

@app.route('/api/predict', methods=['GET'])
def get_predict():
    """
    Returns the next 6-hour AQI forecast.
    Triggers model retraining in a background thread if the cooldown period has elapsed.
    """
    global LAST_TRAINED_TIME
    
    # Check if we should trigger model retraining (rate-limited to avoid hogging resources)
    now = time.time()
    if now - LAST_TRAINED_TIME > TRAIN_COOLDOWN_SECONDS:
        print("[Flask] Cooldown elapsed. Spawning background ML model retraining...")
        # Train model in separate background thread to avoid blocking this HTTP request
        train_thread = threading.Thread(target=ml_model.train_forecasting_model)
        train_thread.start()
        LAST_TRAINED_TIME = now
        
    # Get current forecast prediction
    prediction_data = ml_model.predict_forecast()
    return jsonify(prediction_data)

@app.route('/api/retrain', methods=['POST'])
def force_retrain():
    """Force model retraining immediately."""
    global LAST_TRAINED_TIME
    success = ml_model.train_forecasting_model()
    LAST_TRAINED_TIME = time.time()
    return jsonify({"success": success, "trained_at": datetime.datetime.now().isoformat()})

if __name__ == '__main__':
    # Initialize background threads
    start_background_threads()
    
    # Run server on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
