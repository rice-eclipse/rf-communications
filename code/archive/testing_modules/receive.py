import eclipse_radio_v1 as eradio

NUM_SENDS = 5

mode = input("Enter amplifier mode (D=disabled, B=bypass, R=recieve, T=transmit): ")
bandwidth = float(input("Enter bandwidth (500, 250, 125, 62.5): "))
spreading = int(input("Enter spreading factor (7-12): "))
log_num = input("Enter log file number: ")

trx = eradio.Radio("radio_config.yaml", f"logs/radio_log_{log_num}.yaml")
trx.set_amp_mode(eradio.AmpMode(mode))
trx.trx.signal_bandwidth = bandwidth * 10**3
trx.trx.spreading_factor = spreading

received = 0

while True:
    data = trx.receive_and_log()
    if data is not None:
        received += 1
    print(data)