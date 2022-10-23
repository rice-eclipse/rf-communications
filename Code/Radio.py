import board
import busio
import digitalio
import adafruit_rfm9x
from collections.abc import Iterable
import struct

# Unified class for sending and receiving data
# Much from:
# https://learn.adafruit.com/adafruit-rfm69hcw-and-rfm96-rfm95-rfm98-lora-packet-padio-breakouts/circuitpython-for-rfm9x-lora


class Radio:
    def __init__(self):
        self.RADIO_FREQ_MHZ = 433.0

        # Initialize SPI
        self.spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

        # Define CS and RST pins connected to the radio
        self.cs = digitalio.DigitalInOut(board.D5)
        self.reset = digitalio.DigitalInOut(board.D6)

        # Define the onboard LED
        self.LED = digitalio.DigitalInOut(board.D13)
        self.LED.direction = digitalio.Direction.OUTPUT

        # Create an instance of RFM9x

        # signal bandwith
        # spreading factor
        # txpowers
        # record rssi and snr

        self.rfm9x = adafruit_rfm9x.RFM9x(self.spi, self.cs, self.reset, self.RADIO_FREQ_MHZ)
        # Optional parameter baudrate
        # Default baud rate is 10MHz but that may be too fast
        # If issues arise, decrease to 1MHz

        # Adjust transmitting power (dB)
        self.rfm9x.tx_power = 23

    def send(self, data):
        """
        Sends data through the RFM9X radio.

        Parameters:
            data: a list of floats of any length

        Returns:
            None
        """

        # Bitrate Budget:
        # https://docs.google.com/spreadsheets/d/1BNU0LOl0tzaBlsRqHiAFNp9Y_h9E01Kwud-uezHMNdA/edit#gid=1938337728

        # Every value should be an integer that can be stored in 4 bytes

        # 6-Byte FCC License Callsign - required for every packet
        callsign = bytes("CLSIGN", 'ASCII')

        data_bytearray = bytearray()
        data_bytearray.extend(callsign)

        for num in data:
            #data_bytearray.extend(num.to_bytes(4, 'big'))
            data_bytearray.extend(struct.pack('>f', float(num)))

        # To send a message, call send()
        self.rfm9x.send(bytes(data_bytearray))
        # return bytes(data_bytearray)  # for testing

    def send_flight_data(self, acceleration, gyro, magnetic, altitude, gps, temperature):
        """
        Wrapper for send() function, designed to ensure that data is sent in the correct order.

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
        return self.send(flat_data)

    def receive(self, packet):
        """
        Receives data through the RFM9X radio and returns it, along with last received signal strength

        Parameters:
            None

        Returns:
            Dictionary w/ keys:
                data: a tuple of floats
                rssi: signal strength, in dB
                snr: signal-to-noise ratio
        """
        # packet = self.rfm9x.receive()
        # Optionally change the receive timeout from its default of 0.5 seconds:
        # packet = rfm9x.receive(timeout=5.0)
        # If no packet was received during the timeout then None is returned.
        if packet is None:
            # Packet has not been received
            self.LED.value = False
            return None
        else:
            # Received a packet!
            self.LED.value = True

            # Assuming the received packet follows our encoding scheme, the first six bytes will be the callsign
            # and the rest of the packet will be integers, each occupying exactly four bytes
            # if (len(packet) - 6) % 4 != 0:
            #     print("Message is not appropriate length")
            # else:
            #     print("Message is appropriate length")

            encoded_data = packet[6:]
            data = []
            for idx in range(0, len(encoded_data), 4):
                #data.append(int.from_bytes(encoded_data[idx:idx + 4], 'big'))
                data.append(struct.unpack('>f', encoded_data[idx:idx+4])[0])

            # Also read the RSSI (signal strength) of the last received message, in dB
            rssi = self.rfm9x.last_rssi
            # rssi = 99

            # Also also read the SNR (Signal-to-Noise Ratio) of the last message
            snr = self.rfm9x.last_snr
            # snr = 0.9

            # Return data and other info
            return {
                "data": tuple(data),
                "rssi": rssi,
                "snr": snr
            }

    def reformat_as_flight_data(self, received_data):
        """
        Takes a dictionary from the receive() function and re-organizes it into flight variables
        This could be static I guess but it's nice to bundle it with Radio I think

        Parameters:
            received_data: a dictionary with keys data and rssi

        Returns:
            Dictionary with keys:
                acceleration: 3-tuple of floats
                gyro: 3-tuple, floats
                magnetic: 3-tuple, floats
                altitude: float
                gps: 2-tuple, floats
                temperature: float
        """
        data = received_data["data"]
        reorganized_data = {"acceleration": (data[0], data[1], data[2]),
                            "gyro": (data[3], data[4], data[5]),
                            "magnetic": (data[6], data[7], data[8]),
                            "altitude": data[9],
                            "gps": (data[10], data[11]),
                            "temperature": data[12],
                            "rssi": received_data["rssi"],
                            "snr": received_data["snr"]}
        return reorganized_data
