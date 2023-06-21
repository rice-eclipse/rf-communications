import sys
import os.path

from sensors.altimeter import Altimeter
import sensors.gps


altimeter = Altimeter(bus=0)
gps = sensors.gps.GPS(sensors.gps.GPS_Mode.NORMAL)

while True:
    pressure, temperature = altimeter.read()
    altitude = Altimeter.altitude(pressure, temperature)
    