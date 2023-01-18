import yaml
import time
import sys
import os.path

full_path = os.path.realpath(__file__)
projectdir = os.path.dirname(os.path.dirname(full_path))
radiodir = os.path.join(projectdir, "Radio")
sys.path.insert(0, radiodir)

from Radio import Radio
print("Radio.py located")

radio = Radio()
with open("transmissionTestConfig.yaml", "r") as stream:
    config_dict = yaml.safe_load(stream)
radio.load_config(config_dict)

test_cases = []
# each test case is a 3-tuple (bandwidth, spreading factor, transmission power)
for bandwidth in (62500, 125000, 250000, 500000):
    for spreading_factor in range(7, 13):
        for tx_power in (23, 20, 17):
            for i in range(10):
                test_cases.append((bandwidth, spreading_factor, tx_power))

print("Tests loaded")

test_record = []

c_idx = 0
while c_idx < len(test_cases):

    if c_idx % 10 == 0:
        print(f"Tests {100 * (c_idx / len(test_cases))}% completed")

    config = test_cases[c_idx]

    if c_idx >= len(test_record):
        test_record.append(None)

    radio.rfm9x.signal_bandwidth = config[0]
    radio.rfm9x.spreading_factor = config[1]
    radio.rfm9x.tx_power = config[2]

    print(f"Radio now configured for: Bandwidth {config[0]}, Spreading Factor {config[1]}, Tx Power {config[2]}")

    attempts = 0
    ack_success = False
    ack_pack = None
    while attempts < 3 or not ack_success:
        send_time = time.time_ns()
        radio.send((send_time, 0, config[0], config[1], config[2], c_idx, 0, 0))

        ack_pack = radio.receive()

        if ack_pack is not None:
            ack_success = True
        else:
            print(f"No acknowledgement received for test {c_idx} {config}")
            attempts += 1

    print(f"Packet: {ack_pack}")

    if ack_success:
        ack_pack["final_time"] = time.time_ns()
        test_record[c_idx] = ack_pack
        c_idx += 1
    else:
        print(f"Redoing test {c_idx}; no acknowledgement")

with open('log.yaml', 'w') as file:
    log = yaml.dump(test_record, file)

print("Tests completed")