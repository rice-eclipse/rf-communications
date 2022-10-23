from Radio import Radio

test_cases = []
# each test case is a 3-tuple (bandwidth, spreading factor, transmission power)
for bandwidth in (7800, 10400, 15600, 20800, 31250, 41700, 62500, 125000, 250000):
    for spreading_factor in range(7, 13):
        for tx_power in range(5, 24):
            test_cases.append((bandwidth, spreading_factor, tx_power))

test_radio_object = Radio()
for config in test_cases:
    test_radio_object.send_testing_data(config[0], config[1], config[2])
