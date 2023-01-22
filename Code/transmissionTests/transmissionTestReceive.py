import yaml
import time
import sys
import os.path

# Get the file Radio.py into PATH
full_path = os.path.realpath(__file__)
projectdir = os.path.dirname(os.path.dirname(full_path))
radiodir = os.path.join(projectdir, "Radio")
sys.path.insert(0, radiodir)

from Radio import Radio
print("Radio.py located")


def update_radio_with_config(radio, config):
    # This code is reused several times
    radio.rfm9x.signal_bandwidth = config[0]
    radio.rfm9x.spreading_factor = config[1]
    radio.rfm9x.tx_power = config[2]


with open("transmissionTestConfig.yaml", "r") as stream:
    config_dict = yaml.safe_load(stream)
radio = Radio(config_dict)

tests_per_config = 3

test_cases = []
# each test case is a 3-tuple (bandwidth, spreading factor, transmission power)
for bandwidth in (62500, 125000, 250000, 500000):
    for spreading_factor in range(7, 13):
        for tx_power in (23, 20, 17):
            for i in range(tests_per_config):
                test_cases.append((bandwidth, spreading_factor, tx_power))

print("Tests loaded")

config = test_cases[0]
update_radio_with_config(radio, config)

print(f"Radio now configured for: Bandwidth {config[0]}, Spreading Factor {config[1]}, Tx Power {config[2]}")

failures = 0
c_idx = 0
while True:
    packet = radio.receive()
    print(f"Packet: {packet}")
    if failures < 3:
        print (f"Failures: {failures})
        if packet is not None:
            radio.send((packet["send_time"],
                        time.time_ns()-packet["send_time"],
                        packet["bandwidth"],
                        packet["spreading"],
                        packet["tx_power"],
                        packet["test_num"],
                        packet["snr"],
                        packet["rssi"]))
            c_idx += 1
            config = test_cases[c_idx]
            update_radio_with_config(radio, config)
        else:
            failures += 1
    else:
        c_idx += 1
        config = test_cases[c_idx]
        update_radio_with_config(radio, config)
        failures = 0

    print(f"Radio now configured for: Bandwidth {config[0]}, Spreading Factor {config[1]}, Tx Power {config[2]}")
