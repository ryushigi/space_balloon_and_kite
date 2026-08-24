from smbus2 import SMBus
from datetime import datetime
import pynmea2
import time

def log(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}", flush=True)

log("SAM-M10Q監視開始")

GPS_ADDR = 0x42

buffer = bytearray()

while True:

    try:
        log("I2C接続中...")
        bus = SMBus(1)

        log(f"I2C接続成功 (0x{GPS_ADDR:02X})")

        while True:

            data = bus.read_i2c_block_data(GPS_ADDR, 0xFF, 32)

            for b in data:

                if b == 0xFF:
                    continue

                buffer.append(b)

                if b == ord('\n'):

                    try:

                        line = buffer.decode('ascii').strip()

                        if line.startswith('$GNGGA') or line.startswith('$GPGGA'):

                            msg = pynmea2.parse(line)

                            # 測位できている場合のみ表示
                            if msg.gps_qual != 0:

                                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                                print(
                                    f"[{now}] "
                                    f"緯度={msg.latitude:.6f}, "
                                    f"経度={msg.longitude:.6f}, "
                                    f"高度={msg.altitude}m"
                                )
                            else :
                                print(
                                    f"[{now}] "
                                    f"緯度={msg.latitude:.6f}, "
                                    f"経度={msg.longitude:.6f}, "
                                    f"高度={msg.altitude}m"
                                )
                                

                    except Exception:
                        pass

                    buffer.clear()

    except OSError as e:

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"[{now}] I2Cエラー: {e}")
        print(f"[{now}] 1秒後に再接続します")

        try:
            bus.close()
        except:
            pass

        time.sleep(1)

    except KeyboardInterrupt:

        try:
            bus.close()
        except:
            pass

        break
