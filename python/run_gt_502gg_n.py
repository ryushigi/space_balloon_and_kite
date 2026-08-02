#!/usr/bin/env python3
import gpsd
import time

gpsd.connect()

try:
    while True:
        packet = gpsd.get_current()
        print("lat :", packet.lat)
        print("lon :", packet.lon)
        print("alt :", packet.alt)
        time.sleep(1)
except Exception as e:
    print(e)
