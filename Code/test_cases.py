from Radio import Radio

test_cases = []
# each test case is a 3-tuple (bandwidth, spreading factor, transmission power)
for bandwidth in (7800, 10400, 15600, 20800, 31250, 41700, 62500, 125000, 250000):
    for spreading_factor in range(7, 13):
        for tx_power in range(5, 24):
            test_cases.append((bandwidth, spreading_factor, tx_power))

test_radio_object = Radio()
for config in test_cases:
    test_radio_object.rfm9x.signal_bandwidth = config[0]
    test_radio_object.rfm9x.spreading_factor = config[1]
    test_radio_object.rfm9x.tx_power = config[2]
    for msg_num in range(10):
        # Send multiple messages to ensure reception and also detect how many packets were dropped
        timestamp = 0
        test_radio_object.send((config[0], config[1], config[2], msg_num, timestamp))
        # We might need a pause here

# Multiple packets per test case
# Put timestamp in message and calculate time of travel
# What to do if packets drop? - Encoding format will detect certain errors automatically (ex. if bytes are chopped)

# Packets sent every 0.1-0.5 seconds
