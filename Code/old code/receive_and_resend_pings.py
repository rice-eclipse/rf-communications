import yaml
import time
from Radio import Radio

radio = Radio()
with open("pingtestconfig.yaml", "r") as stream:
    config_dict = yaml.safe_load(stream)
radio.load_config(config_dict)

while True:
    # Receive pings and bounce them back
    packet = radio.receive()
    if packet is not None:
        # Immediately bounce the packet back with new information
        radio.send((packet["send_time"],
                    time.time_ns(),
                    packet["bandwidth"],
                    packet["spreading"],
                    packet["tx_power"],
                    packet["packet_num"],
                    packet["snr"],
                    packet["rssi"]))
    # sleep some time? not sure
