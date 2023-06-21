import os

from sensors.altimeter import Altimeter
import sensors.gps
# import transceiver.radio_fsk
import transceiver.radio_lora


# CONFIG_FILE = 'config/config_rtr.yaml'
CONFIG_FILE = 'config/config_rtr_lora.yaml'

alt = Altimeter(bus=0)
gps = sensors.gps.GPS(sensors.gps.GPS_Mode.NORMAL)
# trx = transceiver.radio_fsk.Radio_FSK(CONFIG_FILE)
trx = transceiver.radio_lora.Radio_LoRa(CONFIG_FILE, None)

while True:
    pressure, temperature = alt.read()
    altitude = Altimeter.altitude(pressure, temperature)
    gps.update()
    if gps.time is not None:
        year, month, day, hour, minute, second = gps.time
    else:
        year, month, day, hour, minute, second = None, None, None, None, None, None

    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"Date: {year}/{month}/{day}\t\t\tTime: {hour}:{minute}:{second} UTC")
    print(f"Pressure: {pressure} mbar\t\tTemperature: {temperature} {chr(176)}C\t\tAltitude: {altitude} m")
    print(f"Fix Quality: {gps.gps.fix_quality}\t\t\tSatellites: {gps.gps.satellites}\t\t")
    print(f"Latitude: {gps.gps.latitude} {chr(176)}N\t\tLongitude: {gps.gps.longitude} {chr(176)}E")

    data = {'command': 0,#transceiver.radio_fsk.Command.NULL.value,
            'pressure': pressure,
            'temperature': temperature,
            'altitude': altitude,
            'latitude': gps.gps.latitude,
            'longitude': gps.gps.longitude,
            'fix_quality': gps.gps.fix_quality,
            'satellites': gps.gps.satellites,
            'year': year,
            'month': month,
            'day': day,
            'hour': hour,
            'minute': minute,
            'second': second}

    trx.send(data)