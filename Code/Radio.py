import board
import busio
import digitalio
import adafruit_rfm9x
from collections.abc import Iterable
import struct
# import yaml
# import time

# Unified class for sending and receiving data
# Much from:
# https://learn.adafruit.com/adafruit-rfm69hcw-and-rfm96-rfm95-rfm98-lora-packet-padio-breakouts/circuitpython-for-rfm9x-lora


class Radio:
    def __init__(self):
        # NOTICE: A new Radio will NOT work!! You must load a config!!
        self.radio_freq_mhz = 433.0
        self.packets_per_transmit = 1
        self.transmit_per_second = 1  # Not sure how useful this will be on the rocket, but it's good for testing
        self.packet_size_bytes = 0
        self.data_types = {}
        self.data_order = []
        self.callsign = "CLSIGN"

        # Initialize SPI
        self.spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

        # Define CS and RST pins connected to the radio
        self.cs = digitalio.DigitalInOut(board.D5)
        self.reset = digitalio.DigitalInOut(board.D6)

        # Define the onboard LED
        # self.LED = digitalio.DigitalInOut(board.D13)
        # self.LED.direction = digitalio.Direction.OUTPUT

        # Create an instance of RFM9x
        self.rfm9x = adafruit_rfm9x.RFM9x(self.spi, self.cs, self.reset, self.radio_freq_mhz, baudrate=10000000)
        # Optional parameter baudrate of connection between rfm9x and SPI (baudrate is equal to bitrate)
        # Default baud rate is 10MHz but that may be too fast
        # If issues arise, decrease to 1MHz

        # Adjust transmitting power (dB)
        self.rfm9x.tx_power = 23

    def send(self, data):
        """
        Sends data through the RFM9X radio.

        Parameters:
            data: a list of numbers conforming to the order and types described in the loaded config file

        Returns:
            None
        """

        # Bitrate Budget:
        # https://docs.google.com/spreadsheets/d/1BNU0LOl0tzaBlsRqHiAFNp9Y_h9E01Kwud-uezHMNdA/edit#gid=1938337728

        # The length of each value in data is determined by its position and the config
        # Remember, packets can't be longer than 252 bytes!

        # If data is shorter than self.data_order refuse to send packet
        if len(self.data_order) != len(data):
            print("Send data is not the appropriate length; check the config")
            return

        # 6-Byte FCC License Callsign - required for every packet
        # Callsign is not in data_order because it is required for every packet
        callsign = bytes(self.callsign, 'ASCII')

        data_bytearray = bytearray()
        data_bytearray.extend(callsign)

        for name, val in zip(self.data_order, data):
            data_type = self.data_types[name]
            data_bytearray.extend(struct.pack(f">{data_type}", val))

        # To send a message, call send()
        self.rfm9x.send(bytes(data_bytearray))
        # return bytes(data_bytearray)

    def send_flight_data(self, acceleration, gyro, magnetic, altitude, gps, temperature):
        """
        Helper for send() function, designed to ensure that flight data is sent in the correct order.

        Parameters:
            acceleration: 3-tuple of floats
            gyro: 3-tuple of floats
            magnetic: 3-tuple of loats
            altitude: float
            gps: 2-tuple of floats
            temperature: float

        Returns:
            None
        """
        data = (acceleration, gyro, magnetic, altitude, gps, temperature)
        flat_data = []
        for item in data:
            if isinstance(item, Iterable):
                flat_data.extend(item)
            else:
                flat_data.append(item)
        self.send(flat_data)

    def receive(self):
        """
        Receives data through the RFM9X radio and returns it as a dictionary,
        including signal-to-noise ratio and last received signal strength

        Parameters:
            None

        Returns:
            Dictionary w/ all keys in the config data_types, along with 'rssi' and 'snr'
        """
        # packet = self.rfm9x.receive()
        # Optionally change the receive timeout (how long until it gives up) from its default of 0.5 seconds:
        packet = self.rfm9x.receive(timeout=1/self.transmit_per_second)
        # If no packet was received during the timeout then None is returned.
        if packet is None:
            # Packet has not been received
            # self.LED.value = False
            return None
        else:
            # Received a packet!
            # self.LED.value = True

            # Cut off callsign; we don't need it (maybe check to make sure it's our packet?)
            encoded_data = packet[6:]

            # Build a list of all the data we've received
            return_dict = {}
            for name in self.data_order:
                data_type = self.data_types[name]
                bytes_size = struct.calcsize(data_type)
                this_data = encoded_data[:bytes_size]
                encoded_data = encoded_data[bytes_size:]
                unpacked_data = struct.unpack(f">{data_type}", this_data)[0]
                return_dict[name] = unpacked_data

            # Also read the RSSI (signal strength) of the last received message, in dB
            return_dict["rssi"] = self.rfm9x.last_rssi

            # Also read the SNR (Signal-to-Noise Ratio) of the last message
            return_dict["snr"] = self.rfm9x.last_snr

            return return_dict

    def load_config(self, config_dict):
        """
        Takes a dictionary of config values and applies them to the current radio object
        Data types are in the format of struct - https://docs.python.org/3/library/struct.html

        Parameters:
            config_dict - a dictionary of configuration information, likely from a config YAML file

        Returns:
            None
        """

        self.callsign = config_dict["callsign"]
        self.packets_per_transmit = config_dict["packets_per_transmit"]
        self.transmit_per_second = config_dict["transmit_per_second"]
        self.data_types = config_dict["data_types"]
        self.data_order = config_dict["data_order"]
        # data_order should be composed solely of all keys from data_sizes!
        # (and vice versa)
        self.packet_size_bytes = 6
        for val in self.data_types.values():
            self.packet_size_bytes += struct.calcsize(val)

        if self.packet_size_bytes >= 252:
            print("PACKET SIZE TOO LARGE! DO NOT CONTINUE!")
            return

        print(f"Radio configuration loaded! Now configured for {self.packet_size_bytes}-byte packets!")

#
# with open("testconfig.yaml", "r") as stream:
#     config_dict = yaml.safe_load(stream)
#
# radio = Radio()
# radio.load_config(config_dict)
# tn = time.time_ns()
# packet = radio.send((tn, 2, 3, 4, 5))
# print(packet)
# print(len(packet))
# received = radio.receive(packet)
# print(received)
# print(tn)