import eclipse_radio_v1 as eradio

CONFIG_FILENAME = "/home/pi/rf/icarusLaunchTest/narwal_config_icarus.yaml"
LOG_FILENAME = "/home/pi/rf/icarusLaunchTest/narwal_log_icarus.yaml"

trx = eradio.Radio(CONFIG_FILENAME, LOG_FILENAME)

while True:
    data = trx.receive_and_log()
    print(f"{data}\n")