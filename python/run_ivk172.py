import serial
import pynmea2
import time

# --- デバイス設定 ---
# Raspberry Pi では通常 /dev/ttyACM0 または /dev/ttyUSB0 になります
port = "/dev/ttyACM0"
baudrate = 9600

print("Waiting for GPS data...")

while True:
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        while True:
            try:
                line = ser.readline().decode('ascii', errors='replace').strip()
                if not line:
                    continue

                # $GPGGA または $GNGGA に測位データが含まれる
                if line.startswith('$GPGGA') or line.startswith('$GNGGA'):
                    try:
                        msg = pynmea2.parse(line)
                        if msg.latitude and msg.longitude:
                            print(f"Latitude: {msg.latitude}, Longitude: {msg.longitude}, Fix: {msg.gps_qual}")
                    except (pynmea2.ParseError, ValueError):
                        # 壊れた文は無視
                        continue

            except serial.SerialException as e:
                # print("Serial read error:", e)
                break  # 再接続

        ser.close()

    except serial.SerialException as e:
        # print("Serial open error:", e)
        time.sleep(1)
