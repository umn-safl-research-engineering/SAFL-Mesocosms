import serial
import time
import datetime
import os

s = serial.Serial()
s.port = ('COM4')
s.baudrate=115200
# s.dtr = 0

s.open()

for i in range(10):
    data_bytes = s.read_until(b'\r\n')
    print(data_bytes)
    time.sleep(0.200)
s.close()
