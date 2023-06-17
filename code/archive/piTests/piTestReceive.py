import yaml
import sys
import os.path

# Get the file Radio.py into PATH
full_path = os.path.realpath(__file__)
projectdir = os.path.dirname(os.path.dirname(full_path))
radiodir = os.path.join(projectdir, "radio")
sys.path.insert(0, radiodir)

from radio import Radio
print("radio.py located")

# Load config -- must be the same as loaded by the sending Radio
with open("piTestConfig.yaml", "r") as stream:
    config_dict = yaml.safe_load(stream)

# Create Radio object
radio = Radio(config_dict)

while True:
    packet = radio.receive()
    if packet is not None:
        print(packet)