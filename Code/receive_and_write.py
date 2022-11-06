import time
import yaml
from Radio import Radio

# Create Radio object
radio = Radio()

# Load config -- must be the same as loaded by the sending Radio
with open("testconfig.yaml", "r") as stream:
    config_dict = yaml.safe_load(stream)
radio.load_config(config_dict)

with open("log.tsv", 'a', buffering=1) as file:
    while True:
        packet = radio.receive()
        # packet = {"timestamp": int(time.time_ns()/1000)*1000, "thing_a": 12.00, "thing_b": 38, "thing_c": 99.999}
        if packet is not None:
            write_string = ""
            for key, value in packet.items():
                write_string += f"{key}: {value}\t"
            write_string += f"delta_time: {time.time_ns() - packet['timestamp']}\n"
            file.write(write_string)
            file.flush()
        time.sleep(0.5)
