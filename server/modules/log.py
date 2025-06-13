import time
from config import DEBUG_MODE


def log(msg):
    if DEBUG_MODE:
        timestamp = time.strftime('%H:%M:%S')
        print(f"[{timestamp}] {msg}")
