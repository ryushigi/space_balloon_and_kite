#!/usr/bin/env python3
import time
import datetime
import socket
import smbus2
import bme280
import gpsd2 as gpsd
import gpiozero

#リモコンポート割り当て
#IC-T10の「mic S」設定を「SimPLE」にしておくこと
#GPIO22	RP_RC0 2.7k S1:CALL-CHの呼び出し
#GPIO23	RP_RC1 6.8k S2:モニター機能をON/OFF
#GPIO24	RP_RC2 15k  S3:M-CHの0CHを呼び出す
#GPIO27	RP_RC3 33k  S4:M-CHの1CHを呼び出す
rc = [gpiozero.OutputDevice(p, initial_value=0) for p in [22, 23, 24, 27]]
def rig_rc(s):
    rc[s].on()
    time.sleep(0.2)
    rc[s].off()

INTERVAL = 90   # 送信間隔（秒）
DATA_TYP = "!"  # Data type: Position without timestamp (no APRS messaging)
APRS_SYM = "O"  # APRSシンボル Balloon
FREQ = ["144.660MHz 1200bps", "431.040MHz 1200bsp"]
MY_CALLSIGN = "Jxxxxx-11"       # 自身のコールサインとSSID
APRS_TOCALL = "APDW18"         # 宛先(Direwolf識別コード)
APRS_PATH   = ["WIDE1-1", "WIDE2-1"] # 中継ルートを配列で指定します
DIREWOLF_HOST = "localhost"    # Direwolfが動いているホスト
DIREWOLF_PORT = 8001           # 標準のKISSPORT (デフォルトの8001)
bme_bus = smbus2.SMBus(5)   #BME280のI2Cバス
bme_adr = 0x76  # BME280のI2Cアドレス


# 緯度経度をAPRS標準フォーマットに変換
def convert_to_aprs_coords(lat, lon):
    lat_dir = "N" if lat >= 0 else "S"
    lat_abs = abs(lat)
    lat_deg = int(lat_abs)
    lat_min = (lat_abs - lat_deg) * 60
    lat_str = f"{lat_deg:02d}{lat_min:05.2f}{lat_dir}"

    lon_dir = "E" if lon >= 0 else "W"
    lon_abs = abs(lon)
    lon_deg = int(lon_abs)
    lon_min = (lon_abs - lon_deg) * 60
    lon_str = f"{lon_deg:03d}{lon_min:05.2f}{lon_dir}"
    
    return lat_str, lon_str

# コールサインとSSIDをAX.25の7バイトバイナリ形式に変換
def encode_callsign(call_ssid, is_last=False):
    if '-' in call_ssid:
        call, ssid = call_ssid.split('-')
        ssid = int(ssid)
    else:
        call = call_ssid
        ssid = 0
        
    call = call.upper().ljust(6)[:6]
    
    # 各文字を1ビット左シフトする (AX.25の厳格な基本ルール)
    encoded = bytearray([ord(c) << 1 for c in call])
    
    # SSIDバイトの組み立て
    ssid_byte = (0x60 | (ssid << 1))
    if is_last:
        ssid_byte |= 0x01 # 経路の最後のコールサインなら最下位ビットを1にする
    encoded.append(ssid_byte)
    
    return encoded

# TNC2テキストを、AX.25(KISS)フレームに変形
def make_kiss_ui_frame(source, dest, paths, payload_str):
    ax25 = bytearray()
    
    # 1. アドレスフィールド (宛先 -> 送信元 -> 中継パスの順)
    ax25.extend(encode_callsign(dest, is_last=False))
    ax25.extend(encode_callsign(source, is_last=(len(paths) == 0)))
    
    for i, p in enumerate(paths):
        last_item = (i == len(paths) - 1)
        ax25.extend(encode_callsign(p, is_last=last_item))
        
    # 2. コントロールフィールド (0x03 = UIフレーム)
    ax25.append(0x03)
    # 3. PIDフィールド (0xF0 = No Layer 3 Protocol)
    ax25.append(0xF0)
    
    # 4. 本文データ
    ax25.extend(payload_str.encode('ascii'))
    
    # 5. KISSプロトコルのカプセル化 (先頭に0x00コマンド、特殊文字のエスケープ)
    kiss_body = bytearray([0x00]) # 0x00 = Data frame on Channel 0
    for b in ax25:
        if b == 0xC0:
            kiss_body.extend([0xDB, 0xDC])
        elif b == 0xDB:
            kiss_body.extend([0xDB, 0xDD])
        else:
            kiss_body.append(b)
            
    # 先頭と末尾を FEND (0xC0) で包む
    return bytearray([0xC0]) + kiss_body + bytearray([0xC0])

# APRSパケット送信
def aprs_send(aprs_payload):
    kiss_packet = make_kiss_ui_frame(MY_CALLSIGN, APRS_TOCALL, APRS_PATH, aprs_payload)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((DIREWOLF_HOST, DIREWOLF_PORT))
        s.sendall(kiss_packet)



bme_cal = None  #BME280 キャリブレーション情報

# GPSとBME280からデータを取得してAPRS情報生成
def make_aprs_payload(freqtxt):
        try:
            # 1. GPSデータの取得
            packet = gpsd.get_current()
            if packet.mode < 2:
                print("GPS signal not fixed. Waiting...")
                return None
                
            lat, lon = packet.position()
            speed_kmh = packet.speed() * 3.6
            if packet.mode >= 3:    #3D fixなら
                altitude_m = packet.altitude()
                track_deg = packet.track
                climb = packet.climb
            else:
                altitude_m = 0.0
                track_deg = 0.0

            # 2. BME280から気象データの取得
            bme_data = bme280.sample(bme_bus, bme_adr, bme_cal)
            temp_c = bme_data.temperature
            press_hpa = bme_data.pressure

            # 3. APRS規格（アメリカ単位）への変換
            aprs_lat, aprs_lon = convert_to_aprs_coords(lat, lon)
            course_val = int(track_deg) % 360
            speed_knots = int(speed_kmh / 1.852)
            altitude_ft = int(altitude_m * 3.28084)
            temp_f = int(temp_c * 1.8 + 32)
            press_formatted = int(press_hpa * 10)

            # 4. APRSデータコアの組み立て
            aprs_pos = f"{aprs_lat}/{aprs_lon}"
            aprs_telemetry = f"{course_val:03d}/{speed_knots:03d}/A={altitude_ft:06d}"
            aprs_telemetry += f" t{temp_f:03d}b{press_formatted:05d}"
            comment = f" climb={climb:.2f}m/s"
            aprs_payload = f"{DATA_TYP}{aprs_pos}{APRS_SYM}{freqtxt} {aprs_telemetry}{comment}"
            return aprs_payload

        except Exception as e:
            print(f"Acquisition error: {e}")
            return None


def main():
    try:
        gpsd.connect()
        print("Connected to gpsd.")
    except Exception as e:
        print(f"gpsd connection error: {e}")
        return

    try:
        bme_cal = bme280.load_calibration_params(bme_bus, bme_adr)
        print("Initialized BME280.")
    except Exception as e:
        print(f"BME280 initialization error: {e}")
        return

    print("Starting Pure KISS Direct APRS Tracker...")

    while True:
        for idx in range(2):
            print(FREQ[idx])
            rig_rc(idx + 2)
            time.sleep(INTERVAL - 10)
            aprs_payload = make_aprs_payload(FREQ[idx])

            # APRSパケット送信
            if aprs_payload:
                now = datetime.datetime.now()
                print(now.strftime("%Y-%m-%d %H:%M:%S"))    
                print(f'aprs_payload="{aprs_payload}"')
                aprs_send(aprs_payload)
            else:
                time.sleep(5)

            time.sleep(10)

if __name__ == "__main__":
    main()
