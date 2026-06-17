import database
from config import DATABASE_TYPE

def reset_system():
    print(f"Starting system reset. Current database engine: {DATABASE_TYPE.upper()}")
    
    conn = database.get_db_connection()
    cursor = database.get_cursor(conn)
    
    try:
        # Drop existing tables
        print("Dropping tables 'sensor_readings' and 'system_logs' if they exist...")
        cursor.execute("DROP TABLE IF EXISTS sensor_readings")
        cursor.execute("DROP TABLE IF EXISTS system_logs")
        conn.commit()
        print("Tables dropped successfully.")
    except Exception as e:
        print(f"Error dropping tables: {e}")
    finally:
        conn.close()
        
    # Re-initialize the database (this recreates tables and seeds initial 24h history)
    print("Re-initializing and seeding database...")
    database.init_db()
    print("System reset complete. Fresh 24-hour history seeded successfully.")

if __name__ == "__main__":
    reset_system()
