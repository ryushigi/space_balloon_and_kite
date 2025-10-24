import serial
import pynmea2
import time

port = "/dev/serial0"
baudrate = 9600

while True:
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        while True:
            try:
                line = ser.readline().decode('ascii', errors='replace').strip()
                if not line:
                    continue
                if line.startswith('$GNGGA'):
                    try:
                        msg = pynmea2.parse(line)
                        print(f"Latitude: {msg.latitude}, Longitude: {msg.longitude}, Fix: {msg.gps_qual}")
                    except (pynmea2.ParseError, ValueError):
                        # 壊れた文は無視して続行
                        continue
            except serial.SerialException as e:
                # print("Serial read error:", e)
                break  # 一旦再接続
        ser.close()
    except serial.SerialException as e:
        # print("Serial open error:", e)
        time.sleep(1)  # 1秒待って再試行
