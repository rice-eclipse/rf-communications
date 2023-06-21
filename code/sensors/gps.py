import adafruit_gps
import serial
from enum import Enum
import time


class GPS_Mode(Enum):
    DISABLED = b'PMTK314,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'
    MINIMUM = b'PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'
    NORMAL = b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'
    FULL = b'PMTK314,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0'


class FIX_QUALITY(Enum):
    NO_FIX = 0
    GPS_FIX = 1
    DIFFERENTIAL_FIX = 2
    PPS_FIX = 3
    RT_KINEMATIC = 4
    FLOAT_RTK = 5
    ESTIMATED = 6
    MANUAL_INPUT = 7
    SIMULATION = 8


class FIX_TYPE(Enum):
    NO_FIX = 1
    FIX_2D = 2
    FIX_3D = 3


class GPS:
    
    def __init__(self, mode: GPS_Mode = GPS_Mode.DISABLED):
        uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=30)
        self.gps = adafruit_gps.GPS(uart, debug=False)
        self.mode = mode
        self.gps.send_command(b"PMTK220,200")
        self.last_update_time = float('-inf')

    @property
    def mode(self):
        return self._current_mode
    
    @mode.setter
    def mode(self, new_mode: GPS_Mode):
        self.gps.send_command(new_mode.value)
        self._current_mode = new_mode

    def update(self, interval: float = 0):
        current_time = time.monotonic()
        if current_time - self.last_update_time > interval:
            try:
                self.gps.update()
                self.last_update_time = current_time
                return True
            except:
                print("GPS update exception")
        return False
    
    @property
    def time_since_update(self):
        return time.monotonic() - self.last_update_time

    @property
    def time(self):
        timestamp = self.gps.timestamp_utc
        return (timestamp.tm_year, timestamp.tm_mon, timestamp.tm_mday,
                timestamp.tm_hour, timestamp.tm_min, timestamp.tm_sec)
    
    @property
    def compressed_time(self):
        t = self.gps.timestamp_utc
        time = 0
        if t.tm_mon is not None:
            time += t.tm_mon
        if t.tm_mday is not None:
            time += t.tm_mday << 4
        if t.tm_hour is not None:
            time += t.tm_hour << 9
        if t.tm_min is not None:
            time += t.tm_min << 14
        if t.tm_sec is not None:
            time += t.tm_sec << 22
        if time == 0 and t.tm_mon is None:
            return None
        return time
    
    def uncompress_time(time):
        month = time & 0xF
        day = (time >> 4) & 0x1F
        hour = (time >> 9) & 0x1F
        min = (time >> 14) & 0x3F
        sec = (time >> 22) & 0x3F
        return month, day, hour, min, sec
