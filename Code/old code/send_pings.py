import yaml
import time
from Radio import Radio

test_cases = []
# each test case is a 3-tuple (bandwidth, spreading factor, transmission power)
for bandwidth in (62500, 125000, 250000, 500000):
    for spreading_factor in range(7, 13):
        for tx_power in range(5, 24):  # 20
            test_cases.append((bandwidth, spreading_factor, tx_power))

radio = Radio()
with open("pingtestconfig.yaml", "r") as stream:
    config_dict = yaml.safe_load(stream)
radio.load_config(config_dict)

with open("log.tsv", 'a', buffering=1) as file:  # this is slow but we could probably put this inside for config in test_cases

    for config in test_cases:
        radio.rfm9x.signal_bandwidth = config[0]
        radio.rfm9x.spreading_factor = config[1]
        radio.rfm9x.tx_power = config[2]
        for msg_num in range(10):
            # Send multiple messages to ensure reception and also detect how many packets were dropped
            send_time = time.time_ns()
            # Some values are filled with 0 initially as a dummy, since we need something there for the config
            # I would use -1 as the dummy, but that might mess it up b/c of unsigned data types
            # Oh how quickly my clever configs hath fallen!
            radio.send((send_time, 0, config[0], config[1], config[2], msg_num, 0, 0))

            while time.time_ns() < send_time + 1 / radio.transmit_per_second:
                # Receive pings and write to file -- we might only be able to do this once
                packet = radio.receive()
                if packet is not None:
                    write_string = ""
                    # Maybe write the values in a specific order
                    # for key, value in packet.items():
                    #     write_string += f"{key}: {value}\t"
                    for key in radio.data_order.extend(["rssi", "snr"]):
                        write_string += f"{packet[key]}\t"
                    write_string += f"receive_time: {time.time_ns()}\n"
                    file.write(write_string)
                    file.flush()
