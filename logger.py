import threading
from collections import deque
import datetime

class LogBuffer:
    def __init__(self, maxlen=100):
        self.logs = deque(maxlen=maxlen)
        self.lock = threading.Lock()

    def log(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{timestamp}] {message}"
        with self.lock:
            self.logs.append(formatted)
            # Also print to stdout
            print(formatted)
        
        # Save dynamically to the SQLite database to avoid circular import issues
        try:
            import database
            database.insert_log(message)
        except Exception:
            pass

    def get_logs(self):
        # Retrieve persistent logs from SQLite if available, otherwise fall back to in-memory deque
        try:
            import database
            db_logs = database.get_recent_logs(limit=100)
            if db_logs:
                return db_logs
        except Exception:
            pass
        
        with self.lock:
            return list(self.logs)

# Global shared log buffer
system_log = LogBuffer(maxlen=100)

