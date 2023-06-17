import board
import time
import calendar
import os

# If things aren't working we might need this library:
# https://github.com/adafruit/Adafruit_CircuitPython_DS3231

# https://www.adafruit.com/product/3013
import adafruit_ds3231


class RTC:
    def __init__(self):
        i2c = board.I2C()
        # We do have I^2C interface between Pi and RTC
        self.rtc_hardware = adafruit_ds3231.DS3231(i2c)
        self.last_perf_time = time.perf_counter_ns()
        self.last_rtc_time = ds3231.datetime
        self.perf_resolution = time.get_clock_info('perf_counter').resolution
        self.system_resolution = time.get_clock_info('time').resolution

    # Everything is in UTC!! The displayed time on the system might not be accurate in this time zone!

    def force_system_network_sync(self):
        os.system(r'sudo timedatectl set-ntp true')
        # TODO: Might not update time immediately. Look for another solution?
        # TODO: Also maybe just switch system timezone to GMT?
        return

    def loop_sync_rtc_to_system(self):
        current_time = time.time()
        if current_time - int(current_time) < self.system_resolution:
            ds3231.datetime = time.struct_time(current_time)
            return True
        return False

    def force_sync_rtc_to_system(self):
        previous_time = time.gmtime()
        while not self.loop_sync_rtc_to_system():
            pass

    def loop_sync_system_to_rtc(self):
        current_RTC_time = ds3231.datetime
        if current_RTC_time.tm_sec != self.last_rtc_time.tm_sec:
            time.clock_settime(time.CLOCK_REALTIME, calendar.timegm(current_RTC_time))  # UTC!!
            return True
        self.last_rtc_time = ds3231.datetime
        return False

    def force_sync_system_to_rtc(self):
        while not self.loop_sync_system_to_rtc():
            pass


if __name__ == '__main__':
    rtc = RTC()
    rtc.force_sync_rtc_to_system()