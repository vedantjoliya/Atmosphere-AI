import os
from dotenv import load_dotenv

# Load optional .env file if it exists
load_dotenv()

# Database setup
DATABASE_PATH = os.environ.get("DATABASE_PATH", "atmosphere_ai.db")

# OpenWeatherMap Settings
# Set this in your environment or in an .env file.
# If empty, the backend will return simulated live weather matching the coordinate's diurnal patterns.
OPENWEATHERMAP_API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY", "")

# Default location settings (coordinates) if geolocation fails or manual override is used.
# Defaults to New York City
DEFAULT_LAT = float(os.environ.get("DEFAULT_LAT", "40.7128"))
DEFAULT_LON = float(os.environ.get("DEFAULT_LON", "-74.0060"))

# Sensor configuration
# Port for serial connection on the Raspberry Pi
SENSOR_SERIAL_PORT = os.environ.get("SENSOR_SERIAL_PORT", "/dev/ttyS0")
SENSOR_BAUDRATE = int(os.environ.get("SENSOR_BAUDRATE", "9600"))

# Network credentials for Admin Block Device
DEVICE_NAME = os.environ.get("DEVICE_NAME", "ADMIN BLOCK DEVICE")
SENSOR_IP = os.environ.get("SENSOR_IP", "192.168.1.242")
SENSOR_USER = os.environ.get("SENSOR_USER", "admin")
SENSOR_PASSWORD = os.environ.get("SENSOR_PASSWORD", "thingspeak")

# Remote SSH Debian device configurations (Debian Bookworm at 192.168.1.242)
SSH_HOST = os.environ.get("SSH_HOST", "192.168.1.242")
SSH_USER = os.environ.get("SSH_USER", "admin")
SSH_PORT = int(os.environ.get("SSH_PORT", "22"))

# Poll interval in seconds for data pipeline
POLL_INTERVAL_SECONDS = int(os.environ.get("POLL_INTERVAL_SECONDS", "10"))

# Enable simulated fallback data when physical/SSH/network sensors are unconfigured.
# If a real sensor is configured but goes offline, should the system fall back to simulator?
# Set to False to keep the last database records when the system is offline.
SIMULATOR_FALLBACK = os.environ.get("SIMULATOR_FALLBACK", "False").lower() in ("true", "1", "yes")

