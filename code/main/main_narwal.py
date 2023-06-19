import radio_fsk

CONFIG_FILENAME = "config_narwal.yaml"

trx = radio_fsk.Radio_FSK(CONFIG_FILENAME)

while True:
    data = trx.receive_and_log()
    print(f"{data}\n")