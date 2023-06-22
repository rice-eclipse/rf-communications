import os
import time

from sensors.altimeter import Altimeter
import sensors.gps
# import transceiver.radio_fsk
import transceiver.radio_lora


# CONFIG_FILE = 'config/config_rtr.yaml'
CONFIG_FILE = '/home/pi/rf-communications/code/config/config_rtr_lora.yaml'

time.sleep(30)

alt = Altimeter(bus=0)
gps = sensors.gps.GPS(sensors.gps.GPS_Mode.NORMAL)
# trx = transceiver.radio_fsk.Radio_FSK(CONFIG_FILE)
trx = transceiver.radio_lora.Radio_LoRa(CONFIG_FILE, None)

def reformat(num):
    if num is None:
        return None
    elif num < 10:
        return f"0{num}"
    else:
        return str(num)

while True:
    pressure, temperature = alt.read()
    altitude = Altimeter.altitude(pressure, temperature)
    try:
        gps.update()
    except:
        continue
    if gps.time is not None:
        year, month, day, hour, minute, second = gps.time
        hour = int((hour - 6) % 24)
    else:
        year, month, day, hour, minute, second = None, None, None, None, None, None

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
    
    year = data['year']
    month = reformat(data['month'])
    day = reformat(data['day'])
    hour = reformat(data['hour'])
    minute = reformat(data['minute'])
    second = reformat(data['second'])
    pressure = round(data['pressure'], 1) if data['pressure'] is not None else None
    temperature = round(data['temperature'], 1) if data['temperature'] is not None else None
    altitude = round(data['altitude'], 1) if data['altitude'] is not None else None
    latitude = round(data['latitude'], 6) if data['latitude'] is not None else None
    longitude = round(data['longitude'], 6) if data['longitude'] is not None else None
    fix_quality = data['fix_quality']
    satellites = data['satellites']

    os.system('cls' if os.name == 'nt' else 'clear')

    message = f"{year}/{month}/{day}\n"
    message += f"{hour}:{minute}:{second}\n"
    message += "\n"
    message += f"Pressure:\t{pressure} mbar\n"
    message += f"Temperature:\t{temperature} {chr(176)}C\n"
    message += f"Altitude:\t{altitude} m\n"
    message += "\n"
    message += f"Latitude:\t{latitude}{chr(176)}\n"
    message += f"Longitude:\t{longitude}{chr(176)}\n"
    message += "\n"
    message += f"Fix Quality:\t{fix_quality}\n"
    message += f"Satellites:\t{satellites}\n"
    message += "\n"
    message += f"RSSI:\t\t{trx.trx.rssi} dBm\n"
    message += f"SNR:\t\t{trx.trx.snr:.2f} dB\n"
    print(message)

    trx.send(data)