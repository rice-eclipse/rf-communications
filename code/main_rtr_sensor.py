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

def reformat(num):
    if num < 10:
        return f"0{num}"
    else:
        return str(num)

while True:
    pressure, temperature = alt.read()
    altitude = Altimeter.altitude(pressure, temperature)
    gps.update()
    if gps.time is not None:
        year, month, day, hour, minute, second = gps.time
        hour -= 6
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

    os.system('cls' if os.name == 'nt' else 'clear')
    message = f"{data['year']}/{reformat(data['month'])}/{reformat(data['day'])}\n"
    message += f"{reformat(data['hour'])}:{reformat(data['minute'])}:{reformat(data['second'])}\n"
    message += "\n"
    message += f"Pressure:\t{round(data['pressure'], 1)} mbar\n"
    message += f"Temperature:\t{round(data['temperature'], 1)} {chr(176)}C\n"
    message += f"Altitude:\t{round(data['altitude'], 1)} m\n"
    message += "\n"
    message += f"Latitude:\t{round(data['latitude'], 6)}{chr(176)}\n"
    message += f"Longitude:\t{round(data['longitude'], 6)}{chr(176)}\n"
    message += "\n"
    message += f"Fix Quality:\t{data['fix_quality']}\n"
    message += f"Satellites:\t{data['satellites']}"
    print(message)

    trx.send(data)