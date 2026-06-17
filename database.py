import sqlite3
import datetime
import math
import random
import os
from config import DATABASE_PATH, SUPABASE_DB_URL, DATABASE_TYPE

def get_db_connection():
    """Establishes connection to either SQLite or PostgreSQL database based on configuration."""
    if DATABASE_TYPE == "postgres":
        import psycopg2
        import urllib.parse
        
        parsed = urllib.parse.urlsplit(SUPABASE_DB_URL)
        username = parsed.username
        password = urllib.parse.unquote(parsed.password) if parsed.password else None
        db_name = parsed.path[1:] if parsed.path else None
        hostname = parsed.hostname
        port = parsed.port
        
        conn = psycopg2.connect(
            database=db_name,
            user=username,
            password=password,
            host=hostname,
            port=port
        )
        return conn
    else:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def get_cursor(conn, dict_cursor=False):
    """Returns cursor. For PostgreSQL, returns a RealDictCursor if dict_cursor is True."""
    if DATABASE_TYPE == "postgres":
        if dict_cursor:
            from psycopg2.extras import RealDictCursor
            return conn.cursor(cursor_factory=RealDictCursor)
        return conn.cursor()
    return conn.cursor()

# Dynamic query formatting based on engine
PLACEHOLDER = "%s" if DATABASE_TYPE == "postgres" else "?"
PRIMARY_KEY_AUTO = "SERIAL PRIMARY KEY" if DATABASE_TYPE == "postgres" else "INTEGER PRIMARY KEY AUTOINCREMENT"

def init_db():
    """Initializes the SQLite/PostgreSQL database and seeds historical data if empty."""
    conn = get_db_connection()
    cursor = get_cursor(conn)
    
    # Create the sensor readings table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id {PRIMARY_KEY_AUTO},
            timestamp TIMESTAMP NOT NULL,
            pm2_5 REAL NOT NULL,
            pm10 REAL NOT NULL,
            co2 REAL NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL
        )
    """)
    
    # Create the system logs table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS system_logs (
            id {PRIMARY_KEY_AUTO},
            timestamp TIMESTAMP NOT NULL,
            message TEXT NOT NULL
        )
    """)
    
    # Check if table is empty
    cursor.execute("SELECT COUNT(*) FROM sensor_readings")
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("Database is empty. Seeding 24 hours of historical sensor readings...")
        seed_historical_data(conn)
    
    conn.commit()
    conn.close()
    print("Database initialization check complete.")

def insert_log(message):
    """Inserts a system log entry into the database."""
    try:
        conn = get_db_connection()
        cursor = get_cursor(conn)
        timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(f"""
            INSERT INTO system_logs (timestamp, message)
            VALUES ({PLACEHOLDER}, {PLACEHOLDER})
        """, (timestamp_str, message))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving log to DB: {e}")

def get_recent_logs(limit=100):
    """Fetches the most recent system logs from the database, returned in chronological order."""
    try:
        conn = get_db_connection()
        cursor = get_cursor(conn, dict_cursor=True)
        cursor.execute(f"""
            SELECT timestamp, message 
            FROM system_logs 
            ORDER BY timestamp DESC 
            LIMIT {PLACEHOLDER}
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        # Format logs with string timestamps to ensure JSON compatibility in Flask
        formatted = []
        for row in reversed(rows):
            ts = row['timestamp']
            if isinstance(ts, datetime.datetime):
                ts = ts.strftime("%Y-%m-%d %H:%M:%S")
            formatted.append(f"[{ts}] {row['message']}")
        return formatted
    except Exception as e:
        print(f"Error fetching logs from DB: {e}")
        return []


def seed_historical_data(conn):
    """Seeds 24 hours of simulated sensor data at 10-minute intervals."""
    cursor = get_cursor(conn)
    now = datetime.datetime.now()
    interval = datetime.timedelta(minutes=10)
    
    # We want 144 points (24 hours * 6 points/hour)
    total_points = 144
    start_time = now - datetime.timedelta(hours=24)
    
    data_to_insert = []
    
    for i in range(total_points):
        point_time = start_time + (i * interval)
        hour = point_time.hour
        minute = point_time.minute
        decimal_hour = hour + minute / 60.0
        
        # Diurnal pattern for temperature (peak in afternoon 15:00, trough in morning 05:00)
        temp_mean = 21.0
        temp_amp = 4.0
        temp = temp_mean + temp_amp * math.sin(2 * math.pi * (decimal_hour - 9) / 24.0) + random.uniform(-0.5, 0.5)
        
        # Diurnal pattern for humidity (inversely correlated with temperature)
        humidity_mean = 55.0
        humidity_amp = 15.0
        humidity = humidity_mean - humidity_amp * math.sin(2 * math.pi * (decimal_hour - 9) / 24.0) + random.uniform(-2.0, 2.0)
        humidity = max(10.0, min(95.0, humidity))
        
        # CO2 peaks during daytime (people awake) and morning/evening activities
        co2_base = 400.0
        rush_hour_1 = math.exp(-((decimal_hour - 8.0) ** 2) / 3.0)
        rush_hour_2 = math.exp(-((decimal_hour - 19.0) ** 2) / 4.0)
        co2 = co2_base + (200.0 * rush_hour_1) + (250.0 * rush_hour_2) + random.uniform(-15.0, 15.0)
        
        # PM2.5 peaks similarly with human activity / traffic, but with baseline
        pm2_5_base = 2.0
        pm2_5_peak = 1.0 * rush_hour_1 + 1.5 * rush_hour_2
        pm2_5 = pm2_5_base + pm2_5_peak + random.uniform(-0.5, 0.5)
        pm2_5 = max(0.5, pm2_5)
        
        # PM10 is correlated with PM2.5 but higher
        pm10 = pm2_5 * random.uniform(1.3, 1.8) + random.uniform(1.0, 4.0)
        pm10 = max(2.0, pm10)
        
        # Format timestamp for SQLite/Postgres
        timestamp_str = point_time.strftime("%Y-%m-%d %H:%M:%S")
        
        data_to_insert.append((timestamp_str, pm2_5, pm10, co2, temp, humidity))
        
    cursor.executemany(f"""
        INSERT INTO sensor_readings (timestamp, pm2_5, pm10, co2, temperature, humidity)
        VALUES ({PLACEHOLDER}, {PLACEHOLDER}, {PLACEHOLDER}, {PLACEHOLDER}, {PLACEHOLDER}, {PLACEHOLDER})
    """, data_to_insert)

def insert_reading(pm2_5, pm10, co2, temperature, humidity):
    """Inserts a single sensor reading record into the database."""
    conn = get_db_connection()
    cursor = get_cursor(conn)
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(f"""
        INSERT INTO sensor_readings (timestamp, pm2_5, pm10, co2, temperature, humidity)
        VALUES ({PLACEHOLDER}, {PLACEHOLDER}, {PLACEHOLDER}, {PLACEHOLDER}, {PLACEHOLDER}, {PLACEHOLDER})
    """, (timestamp_str, pm2_5, pm10, co2, temperature, humidity))
    conn.commit()
    conn.close()

def get_latest_reading():
    """Fetches the absolute latest sensor reading."""
    conn = get_db_connection()
    cursor = get_cursor(conn, dict_cursor=True)
    cursor.execute("""
        SELECT timestamp, pm2_5, pm10, co2, temperature, humidity 
        FROM sensor_readings 
        ORDER BY timestamp DESC 
        LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()
    if row:
        row_dict = dict(row)
        if isinstance(row_dict.get('timestamp'), datetime.datetime):
            row_dict['timestamp'] = row_dict['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
        return row_dict
    return None

def get_recent_readings(limit=100):
    """Fetches the most recent readings, ordered chronologically (oldest to newest)."""
    conn = get_db_connection()
    cursor = get_cursor(conn, dict_cursor=True)
    cursor.execute(f"""
        SELECT timestamp, pm2_5, pm10, co2, temperature, humidity 
        FROM (
            SELECT id, timestamp, pm2_5, pm10, co2, temperature, humidity 
            FROM sensor_readings 
            ORDER BY timestamp DESC 
            LIMIT {PLACEHOLDER}
        ) AS temp_sub
        ORDER BY timestamp ASC
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    res = []
    for r in rows:
        r_dict = dict(r)
        if isinstance(r_dict.get('timestamp'), datetime.datetime):
            r_dict['timestamp'] = r_dict['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
        res.append(r_dict)
    return res

if __name__ == "__main__":
    init_db()
    print("Latest:", get_latest_reading())
