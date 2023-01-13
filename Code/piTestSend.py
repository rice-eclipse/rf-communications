import yaml
from Radio import Radio

# Create Radio object
radio = Radio()

# Load config -- must be the same as loaded by the sending Radio
with open("pitestconfig.yaml", "r") as stream:
    config_dict = yaml.safe_load(stream)
radio.load_config(config_dict)

for i in range(10):
    radio.send((i))