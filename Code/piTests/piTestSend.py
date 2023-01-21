import yaml
import sys
import os.path

# Get the file Radio.py into PATH
full_path = os.path.realpath(__file__)
projectdir = os.path.dirname(os.path.dirname(full_path))
radiodir = os.path.join(projectdir, "Radio")
sys.path.insert(0, radiodir)

from Radio import Radio
print("Radio.py located")

# Load config -- must be the same as loaded by the sending Radio
with open("piTestConfig.yaml", "r") as stream:
    config_dict = yaml.safe_load(stream)

# Create Radio object
radio = Radio(config_dict)

for i in range(10):
    radio.send((i,))