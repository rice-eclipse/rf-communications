# Simple demo of sending and recieving data with the RFM95 LoRa radio.
# much from https://learn.adafruit.com/adafruit-rfm69hcw-and-rfm96-rfm95-rfm98-lora-packet-padio-breakouts/circuitpython-for-rfm9x-lora

# initialize SPI connection with radio
import board
import busio
import digitalio
import adafruit_rfm9x


class Transmit():
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

        self.rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, RADIO_FREQ_MHZ)
        # Optional parameter baudrate
        # Default baud rate is 10MHz but that may be too fast
        # If issues arise, decrease to 1MHz

        # Adjust transmitting power (dB)
        self.rfm9x.tx_power = 23


    def send(self, acceleration, gyro, magnetic, altitude, gps, temperature):
        """
        Sends data:
            acceleration (3-tuple),
            gyro (3-tuple),
            magnetic (3-tuple),
            altitude (float?),
            gps (2-tuple),
            temperature (float?)
        """

        # Bitrate Budget https://docs.google.com/spreadsheets/d/1BNU0LOl0tzaBlsRqHiAFNp9Y_h9E01Kwud-uezHMNdA/edit#gid=1938337728
        # Must extend required headers and then include all required information from sensors

        # Every value should be an integer that can be stored in 4 bytes

        # 6-Byte FCC License Callsign - required for every packet
        callsign = bytes("CLSIGN", 'ASCII')

        # Byte array object with which to build our signal
        # It might be faster to build the bytearray all at once,
        # But building it over many extends is more readable
        data_bytearray = bytearray()
        data_bytearray.extend(callsign)

        for accel_val in acceleration:
            data_bytearray.extend(accel_val.to_bytes(4, 'big'))

        for gyro_val in gyro:
            data_bytearray.extend(gyro_val.to_bytes(4, 'big'))

        for mag_val in magnetic:
            data_bytearray.extend(mag_val.to_bytes(4, 'big'))

        for gps_val in gps:
            data_bytearray.extend(gps_val.to_bytes(4, 'big'))

        data_bytearray.extend(altitude.to_bytes(4, 'big'))

        data_bytearray.extend(temperature.to_bytes(4, 'big'))

        # To send a message, call send()
        self.rfm9x.send(bytes(data_bytearray))

        # Final message is 58 bytes
        # First 6 bytes is callsign
        # Rest of message is made of 4-byte numbers organized in this order:
        #   Acceleration value 1, acceleration value 2, acceleration value 3
        #   Gyro value 1, gyro value 2, gyro value 3
        #   Magnetic value 1, magnetic value 2, magnetic value 3
        #   Altitude value
        #   GPS value 1, GPS value 2
        #   Temperature value

        # This order is, of course, completely arbitrary

        # Note that the values are big-endian and will have to be decoded properly