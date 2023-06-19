import radio_fsk

CONFIG_FILENAME = "config_rtr.yaml"

trx = radio_fsk.Radio_FSK(CONFIG_FILENAME)

while True:
    packet = {}
    packet['pressure'] = 1
    packet['temperature'] = 2
    packet['altitude'] = 4
    packet['latitude'] = 7.8
    packet['longitude'] = 11.12
    packet['altitude_gps'] = 16.171819
    packet['fix_quality'] = 3
    packet['satellites'] = 120
    trx.send(packet)