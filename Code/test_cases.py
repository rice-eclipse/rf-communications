test_cases = []
# each test case is a 3-tuple (bandwidth, spreading factor, transmission power)
for bandwidth in (7800, 10400, 15600, 20800, 31250, 41700, 62500, 125000, 250000):
  for spreading_factor in range(7,13):
    for tx_power in range(5, 24):
      test_cases.append((bandwidth, spreading_factor, tx_power))

for config in test_code:
  rfm9x.signal_bandwidth = config[0]
  rfm9x.spreading_factor = config[1]
  rfm9x.tx_power = config[2]


test_radio_object = Radio()
