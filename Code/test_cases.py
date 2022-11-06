import yaml
import time
from Radio import Radio

test_cases = []
# each test case is a 3-tuple (bandwidth, spreading factor, transmission power)
for bandwidth in (7800, 10400, 15600, 20800, 31250, 41700, 62500, 125000, 250000):
    for spreading_factor in range(7, 13):
        for tx_power in range(5, 24):
            test_cases.append((bandwidth, spreading_factor, tx_power))

# It's gonna take like half an hour with all these tests - maybe we can cut down on pause time?

test_radio_object = Radio()
# I'm like very sure this will work fine, but for other scripts we might want to catch errors in loading the file.
# Although, on second thought, if the file doesn't load correctly, then nothing else will work
# So if we get errors in the file loading, we had better stop and fix them before moving on!
with open("testconfig.yaml", "r") as stream:
    config_dict = yaml.safe_load(stream)
test_radio_object.load_config(config_dict)

for config in test_cases:
    test_radio_object.rfm9x.signal_bandwidth = config[0]
    test_radio_object.rfm9x.spreading_factor = config[1]
    test_radio_object.rfm9x.tx_power = config[2]
    for msg_num in range(10):
        # Send multiple messages to ensure reception and also detect how many packets were dropped
        timestamp = time.time_ns()
        test_radio_object.send((timestamp, config[0], config[1], config[2], msg_num))
        # I made some of the data unsigned short ints, so if we get weird behavior maybe we should check that out
        # Smaller packets = smaller chance of error! I think!

        # Let's take some time to reflect
        time.sleep(1 / test_radio_object.transmit_per_second)


# Blog with nice floating precision chart https://blog.demofox.org/2017/11/21/floating-point-precision/

# TODO: Either keep track of stats and display after sending, or make a new script to read all the data in log.tsv and display it as some graphs
