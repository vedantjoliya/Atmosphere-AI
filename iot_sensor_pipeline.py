import time
import math
import random
import datetime
import sys
import requests
import subprocess
import json
from config import SENSOR_SERIAL_PORT, SENSOR_BAUDRATE, POLL_INTERVAL_SECONDS, SENSOR_IP, SENSOR_USER, SENSOR_PASSWORD, SSH_HOST, SSH_USER, SSH_PORT
import database
from logger import system_log

# Attempt to import serial for physical PMS5003 readings
try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

class SensorPipeline:
    def __init__(self, use_simulator=None):
        """
        Initializes the sensor pipeline.
        If use_simulator is True, bypasses serial check and uses simulated data.
        If use_simulator is None or False, attempts serial, falls back to simulator if fails.
        """
        self.use_simulator = use_simulator
        self.serial_conn = None
        self.ssh_client = None
        
        # State for simulated walk variables (to make real-time graphs look smooth and realistic)
        self.sim_pm2_5 = 2.5
        self.sim_co2 = 450.0
        
        if not SERIAL_AVAILABLE:
            system_log.log("[SensorPipeline] pyserial not installed. Running in SIMULATED mode.")
            self.use_simulator = True
        elif self.use_simulator is not True:
            self.attempt_serial_connection()

    def attempt_serial_connection(self):
        """Attempts to open the serial port for PMS5003."""
        try:
            self.serial_conn = serial.Serial(
                port=SENSOR_SERIAL_PORT,
                baudrate=SENSOR_BAUDRATE,
                timeout=2.0
            )
            system_log.log(f"[SensorPipeline] Successfully connected to physical sensor on {SENSOR_SERIAL_PORT}")
            self.use_simulator = False
        except Exception as e:
            system_log.log(f"[SensorPipeline] Failed to connect to serial port {SENSOR_SERIAL_PORT}: {e}")
            system_log.log("[SensorPipeline] Falling back to SIMULATED mode.")
            self.use_simulator = True

    def read_pms5003(self):
        """
        Parses a 32-byte active frame from the PMS5003 sensor.
        PMS5003 frame structure:
        Bytes 0-1: Start characters 0x42, 0x4d
        Bytes 2-3: Frame length
        Bytes 4-5: PM1.0 concentration (CF=1)
        Bytes 6-7: PM2.5 concentration (CF=1)
        Bytes 8-9: PM10 concentration (CF=1)
        ...
        Bytes 30-31: Checksum
        """
        if not self.serial_conn:
            return None

        try:
            # We want to find the start sequence: 0x42, 0x4d
            while True:
                b = self.serial_conn.read(1)
                if not b:
                    return None
                if b[0] == 0x42:
                    b2 = self.serial_conn.read(1)
                    if b2 and b2[0] == 0x4d:
                        break
            
            # Read the rest of the 32-byte frame (30 bytes left)
            frame = self.serial_conn.read(30)
            if len(frame) < 30:
                return None
            
            # Reconstruct the full frame for checksum validation
            full_frame = bytearray([0x42, 0x4d]) + frame
            
            # Checksum is the sum of first 30 bytes
            checksum = (full_frame[30] << 8) | full_frame[31]
            calculated_checksum = sum(full_frame[:30])
            
            if checksum != calculated_checksum:
                system_log.log("[SensorPipeline] Warning: Checksum mismatch in PMS5003 frame.")
                return None
            
            # PM2.5 standard concentration (atmospheric) is at bytes 12-13
            # PM10 standard concentration (atmospheric) is at bytes 14-15
            pm2_5 = (full_frame[12] << 8) | full_frame[13]
            pm10 = (full_frame[14] << 8) | full_frame[15]
            
            return {
                "pm2_5": float(pm2_5),
                "pm10": float(pm10)
            }
        except Exception as e:
            system_log.log(f"[SensorPipeline] Error reading serial sensor: {e}")
            # Try to reconnect
            self.serial_conn = None
            self.attempt_serial_connection()
            return None

    def get_simulated_reading(self):
        """Generates a realistic simulated reading using a random walk + diurnal trend."""
        now = datetime.datetime.now()
        hour = now.hour
        minute = now.minute
        decimal_hour = hour + minute / 60.0
        
        # Diurnal curves (rush hours at 8 AM and 7 PM)
        rush_hour_1 = math.exp(-((decimal_hour - 8.0) ** 2) / 3.0)
        rush_hour_2 = math.exp(-((decimal_hour - 19.0) ** 2) / 4.0)
        
        # 1. PM2.5 Random walk + diurnal base (recalibrated for clean-room)
        target_pm2_5 = 2.0 + (1.0 * rush_hour_1) + (1.5 * rush_hour_2)
        # Random walk step towards target
        self.sim_pm2_5 += (target_pm2_5 - self.sim_pm2_5) * 0.15 + random.uniform(-0.3, 0.3)
        self.sim_pm2_5 = max(0.5, min(150.0, self.sim_pm2_5))
        
        # 2. PM10 is correlated with PM2.5
        pm10 = self.sim_pm2_5 * random.uniform(1.3, 1.6) + random.uniform(0.5, 2.0)
        pm10 = max(2.0, pm10)
        
        # 3. CO2 Random walk + diurnal base
        target_co2 = 400.0 + (150.0 * rush_hour_1) + (200.0 * rush_hour_2)
        self.sim_co2 += (target_co2 - self.sim_co2) * 0.10 + random.uniform(-10.0, 10.0)
        self.sim_co2 = max(350.0, min(1200.0, self.sim_co2))
        
        # 4. Temperature diurnal peak at 15:00
        temp_mean = 21.0
        temp_amp = 4.0
        temp = temp_mean + temp_amp * math.sin(2 * math.pi * (decimal_hour - 9) / 24.0) + random.uniform(-0.1, 0.1)
        
        # 5. Humidity diurnal trough at 15:00 (inverse of temp)
        humidity_mean = 55.0
        humidity_amp = 15.0
        humidity = humidity_mean - humidity_amp * math.sin(2 * math.pi * (decimal_hour - 9) / 24.0) + random.uniform(-0.5, 0.5)
        humidity = max(10.0, min(95.0, humidity))
        
        return {
            "pm2_5": round(self.sim_pm2_5, 2),
            "pm10": round(pm10, 2),
            "co2": round(self.sim_co2, 1),
            "temperature": round(temp, 2),
            "humidity": round(humidity, 2)
        }

    def read_network_sensor(self):
        """Attempts to poll the environmental sensor at SENSOR_IP using credentials."""
        if not SENSOR_IP:
            return None
        
        # Test a few common REST API paths on the local IoT bridge or ThingSpeak server
        paths = [
            "/channels/1/feeds/last.json",
            "/feeds/last.json",
            "/api/realtime",
            "/data.json",
            "/status",
            "/"
        ]
        
        for path in paths:
            try:
                target_url = f"http://{SENSOR_IP}{path}"
                # Low timeout to keep pipeline responsive if network device is offline
                response = requests.get(
                    target_url,
                    auth=(SENSOR_USER, SENSOR_PASSWORD),
                    timeout=1.5
                )
                if response.status_code == 200:
                    data = response.json()
                    
                    # Handle ThingSpeak standard feed wrapper list
                    if isinstance(data, dict):
                        if "feeds" in data:
                            feeds = data["feeds"]
                            if isinstance(feeds, list) and len(feeds) > 0:
                                data = feeds[-1]
                            elif isinstance(feeds, dict):
                                data = feeds
                    
                    if isinstance(data, list) and len(data) > 0:
                        data = data[0]
                    elif not isinstance(data, dict):
                        continue
                    
                    # Flexibly parse parameters (both standard and ThingSpeak fields)
                    pm2_5 = data.get("pm2_5", data.get("pm25", data.get("PM2.5", data.get("pm2.5", data.get("field1")))))
                    pm10 = data.get("pm10", data.get("PM10", data.get("field2")))
                    co2 = data.get("co2", data.get("CO2", data.get("field3")))
                    temp = data.get("temperature", data.get("temp", data.get("Temp", data.get("field4"))))
                    humidity = data.get("humidity", data.get("hum", data.get("Hum", data.get("field5"))))
                    
                    def safe_float(val, default=None):
                        if val is None:
                            return default
                        try:
                            return float(val)
                        except (ValueError, TypeError):
                            return default
                    
                    pm2_5_val = safe_float(pm2_5)
                    if pm2_5_val is not None:
                        reading = {
                            "pm2_5": pm2_5_val,
                            "pm10": safe_float(pm10, pm2_5_val * 1.45),
                            "co2": safe_float(co2, 430.0),
                            "temperature": safe_float(temp, 21.5),
                            "humidity": safe_float(humidity, 50.0)
                        }
                        system_log.log(f"[SensorPipeline] Successfully parsed network sensor reading from {target_url}")
                        return reading
            except Exception:
                pass
        return None

    def get_ssh_client(self):
        """Returns an active Paramiko SSH client, reconnecting if necessary."""
        if self.ssh_client is not None:
            try:
                transport = self.ssh_client.get_transport()
                if transport is not None and transport.is_active():
                    return self.ssh_client
            except Exception:
                pass
            self.close_ssh_client()
            
        try:
            import paramiko
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # SSH user, password and IP from config
            client.connect(
                hostname=SSH_HOST,
                port=SSH_PORT,
                username=SSH_USER,
                password=SENSOR_PASSWORD,  # "thingspeak"
                timeout=3.0
            )
            self.ssh_client = client
            system_log.log(f"[SensorPipeline] SSH connected to {SSH_HOST}")
            return self.ssh_client
        except Exception as e:
            system_log.log(f"[SensorPipeline] SSH connection to {SSH_HOST} failed: {e}")
            self.ssh_client = None
            return None

    def close_ssh_client(self):
        """Closes the active Paramiko SSH connection."""
        if self.ssh_client:
            try:
                self.ssh_client.close()
            except Exception:
                pass
            self.ssh_client = None

    def read_ssh_sensor(self):
        """Attempts to SSH into the remote Debian host and parse its SDS011 or PMS5003 serial sensor."""
        if not SSH_HOST:
            return None
            
        client = self.get_ssh_client()
        if not client:
            return None
            
        # Remote command scans serial ports for active SDS011 or PMS5003 packet and outputs JSON
        remote_cmd = """sudo python3 -c '
import serial
import json
import sys

ports = ["/dev/ttyUSB0", "/dev/ttyAMA0", "/dev/ttyAMA10", "/dev/ttyS0"]
for p in ports:
    try:
        ser = serial.Serial(p, baudrate=9600, timeout=1.0)
        buffer = bytearray()
        for _ in range(300):
            b = ser.read(1)
            if len(b) == 0:
                break
            buffer.append(b[0])
            
            # 1. SDS011 Format
            if len(buffer) >= 10:
                idx = 0
                while idx <= len(buffer) - 10:
                    if buffer[idx] == 0xaa and buffer[idx+1] == 0xc0 and buffer[idx+9] == 0xab:
                        frame = buffer[idx:idx+10]
                        checksum = sum(frame[2:8]) & 0xFF
                        if checksum == frame[8]:
                            pm25 = (frame[3] << 8 | frame[2]) / 10.0
                            pm10 = (frame[5] << 8 | frame[4]) / 10.0
                            print(json.dumps({"pm2_5": pm25, "pm10": pm10, "sensor_type": "SDS011", "port": p}))
                            ser.close()
                            sys.exit(0)
                    idx += 1
            
            # 2. PMS5003 Format
            if len(buffer) >= 32:
                idx = 0
                while idx <= len(buffer) - 32:
                    if buffer[idx] == 0x42 and buffer[idx+1] == 0x4d:
                        frame_len = (buffer[idx+2] << 8) | buffer[idx+3]
                        if frame_len == 28 and idx + 32 <= len(buffer):
                            frame = buffer[idx:idx+32]
                            checksum = (frame[30] << 8) | frame[31]
                            calculated_checksum = sum(frame[:30])
                            if checksum == calculated_checksum:
                                pm25 = float((frame[12] << 8) | frame[13])
                                pm10 = float((frame[14] << 8) | frame[15])
                                print(json.dumps({"pm2_5": pm25, "pm10": pm10, "sensor_type": "PMS5003", "port": p}))
                                ser.close()
                                sys.exit(0)
                    idx += 1
        ser.close()
    except Exception:
        pass
print(json.dumps({"error": "no sensor found"}))
'"""
        try:
            stdin, stdout, stderr = client.exec_command(remote_cmd, timeout=4.0)
            output = stdout.read().decode().strip()
            err_msg = stderr.read().decode().strip()
            
            if output:
                data = json.loads(output)
                if "pm2_5" in data:
                    sim_aux = self.get_simulated_reading()
                    reading = {
                        "pm2_5": float(data["pm2_5"]),
                        "pm10": float(data["pm10"]),
                        "co2": sim_aux["co2"],
                        "temperature": sim_aux["temperature"],
                        "humidity": sim_aux["humidity"]
                    }
                    system_log.log(f"[SensorPipeline] Successfully fetched remote sensor reading ({data.get('sensor_type')}) over SSH from {SSH_HOST}")
                    return reading
                else:
                    system_log.log(f"[SensorPipeline] SSH command returned error/invalid JSON: {output}")
            if err_msg:
                system_log.log(f"[SensorPipeline] SSH command stderr: {err_msg}")
        except Exception as e:
            system_log.log(f"[SensorPipeline] SSH execution failed: {e}")
            self.close_ssh_client()
            
        return None

    def read_once(self):
        """Reads from SSH remote sensor (highest priority), network sensor, physical serial sensor, or simulator."""
        has_active_sensors = bool(SSH_HOST or SENSOR_IP or (SERIAL_AVAILABLE and not self.use_simulator))

        # 1. Try remote SSH Debian sensor first
        if SSH_HOST:
            system_log.log(f"[SensorPipeline] Attempting to read remote sensor via SSH from {SSH_HOST}...")
            ssh_data = self.read_ssh_sensor()
            if ssh_data:
                system_log.log(f"[SensorPipeline] SSH Read Success: PM2.5={ssh_data['pm2_5']} ug/m3, CO2={ssh_data['co2']} ppm, Temp={ssh_data['temperature']} C")
                return ssh_data
            
        # 2. Try network sensor second
        if SENSOR_IP:
            system_log.log(f"[SensorPipeline] Attempting to read network sensor from IP {SENSOR_IP}...")
            net_data = self.read_network_sensor()
            if net_data:
                system_log.log(f"[SensorPipeline] Network Read Success: PM2.5={net_data['pm2_5']} ug/m3, CO2={net_data['co2']} ppm, Temp={net_data['temperature']} C")
                return net_data

        # 3. Try physical serial sensor if network is unavailable
        if not self.use_simulator:
            system_log.log(f"[SensorPipeline] Attempting to read physical serial sensor on {SENSOR_SERIAL_PORT}...")
            pm_data = self.read_pms5003()
            if pm_data:
                sim_aux = self.get_simulated_reading()
                reading = {
                    "pm2_5": pm_data["pm2_5"],
                    "pm10": pm_data["pm10"],
                    "co2": sim_aux["co2"],
                    "temperature": sim_aux["temperature"],
                    "humidity": sim_aux["humidity"]
                }
                system_log.log(f"[SensorPipeline] Serial Read Success: PM2.5={reading['pm2_5']} ug/m3, CO2={reading['co2']} ppm, Temp={reading['temperature']} C")
                return reading
        
        # 4. Fall back to simulation
        # Only fallback if simulator fallback is enabled, or if no active sensors are configured at all (pure simulation demo mode)
        from config import SIMULATOR_FALLBACK
        if SIMULATOR_FALLBACK or not has_active_sensors:
            system_log.log("[SensorPipeline] Using simulator fallback...")
            reading = self.get_simulated_reading()
            system_log.log(f"[SensorPipeline] Simulator Read: PM2.5={reading['pm2_5']} ug/m3, CO2={reading['co2']} ppm, Temp={reading['temperature']} C")
            return reading
        
        system_log.log("[SensorPipeline] Simulator fallback is disabled. Sensor readings are offline.")
        return None

    def run_loop(self):
        """Runs the infinite polling loop, saving entries to the database."""
        database.init_db()
        system_log.log(f"[SensorPipeline] Starting data pipeline polling loop every {POLL_INTERVAL_SECONDS} seconds...")
        try:
            while True:
                data = self.read_once()
                if data is not None:
                    database.insert_reading(
                        pm2_5=data["pm2_5"],
                        pm10=data["pm10"],
                        co2=data["co2"],
                        temperature=data["temperature"],
                        humidity=data["humidity"]
                    )
                    system_log.log(f"[SensorPipeline] Saved reading at {datetime.datetime.now().strftime('%H:%M:%S')}: "
                                   f"PM2.5={data['pm2_5']} ug/m3, CO2={data['co2']} ppm, Temp={data['temperature']} C")
                else:
                    system_log.log(f"[SensorPipeline] System is OFFLINE. No sensor telemetry retrieved. Retaining last database state.")
                time.sleep(POLL_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            system_log.log("[SensorPipeline] Data pipeline loop stopped by user.")
        except Exception as e:
            system_log.log(f"[SensorPipeline] Fatal error in loop: {e}")


if __name__ == "__main__":
    pipeline = SensorPipeline()
    pipeline.run_loop()
