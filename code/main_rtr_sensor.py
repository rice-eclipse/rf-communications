from sensors.altimeter import Altimeter
import sensors.gps
import transceiver.radio_fsk


CONFIG_FILE = 'config/config_rtr.yaml'

alt = Altimeter(bus=0)
gps = sensors.gps.GPS(sensors.gps.GPS_Mode.NORMAL)
trx = transceiver.radio_fsk.Radio_FSK(CONFIG_FILE)

while True:
    pressure, temperature = alt.read()
    altitude = Altimeter.altitude(pressure, temperature)
    print(pressure, temperature, altitude)
    gps.update()
    print(gps.gps.has_fix, gps.gps.fix_quality, gps.gps.latitude, gps.gps.longitude, gps.time)

    data = {'command': transceiver.radio_fsk.Command.NULL.value,
            'pressure': pressure,
            'temperature': temperature,
            'altitude': altitude,
            'latitude': gps.gps.latitude,
            'longitude': gps.gps.longitude,
            'fix_quality': gps.gps.fix_quality,
            'satellites': gps.gps.satellites}

    trx.send_and_log(data)