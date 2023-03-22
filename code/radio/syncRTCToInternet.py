import board
import time
i2c = board.I2C()
# We do have I^2C interface between Pi and RTC

# If things aren't working we might need this library:
# https://github.com/adafruit/Adafruit_CircuitPython_DS3231

# https://www.adafruit.com/product/3013

import adafruit_ds3231
ds3231 = adafruit_ds3231.DS3231(i2c)

"""
RTC does not have sub-second time
Can use raspberry pi to track that and sync with RTC every so often
time.clock_settime(clk_id, time: float) - Set the time of the specified clock clk_id. Currently, CLOCK_REALTIME is the only accepted value for clk_id.
(Use clock_settime_ns() to avoid the precision loss caused by the float type.)

Need to sync RTC with internet
import time
ds3231.datetime = time.struct_time((2017, 1, 1, 0, 0, 0, 6, 1, -1))

struct_time does not support fractions of a second
So syncing clocks will have to happen on the second
time.gmtime() returns a time_struct, as does time.localtime()
Thought is to use gmtime() for accuracy and then convert to local time string in timestamps 

Plan:
New script: syncRTCToInternet.py - syncs RTC to global correct time. Used when in internet range
Any script thats running will have to periodically update system time with time from RTC (on the second)
Scripts can then use time.time_ns() to get the time
"""

# Everyting is in UTC!!
previous_time = time.gmtime()
while True:
    # Assuming the Pi keeps its clock up-to-date when connected to internet
    current_time = time.gmtime()

    if current_time.tm_sec - previous_time.tm_sec == 1:
        # If something's really gone wrong and the difference is more that 1 sec, try again
        ds3231.datetime = time.struct_time(current_time)
        break

    previous_time = time.gmtime()
