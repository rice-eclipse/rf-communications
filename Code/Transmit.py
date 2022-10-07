# Simple demo of sending and recieving data with the RFM95 LoRa radio.
# much from https://learn.adafruit.com/adafruit-rfm69hcw-and-rfm96-rfm95-rfm98-lora-packet-padio-breakouts/circuitpython-for-rfm9x-lora

# initialize SPI connection with radio
import board
import busio
import digitalio
import yaml

RADIO_FREQ_MHZ = 433.0

# Initialize SPI
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Define CS and RST pins connected to the radio
cs = digitalio.DigitalInOut(board.D5)
reset = digitalio.DigitalInOut(board.D6)

# Define the onboard LED
LED = digitalio.DigitalInOut(board.D13)
LED.direction = digitalio.Direction.OUTPUT

# Create an instance of RFM9x
import adafruit_rfm9x
rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, RADIO_FREQ_MHZ)
# Optional parameter baudrate
# Default baud rate is 10MHz but that may be too fast
# If issues arise, decrease to 1MHz

# Adjust transmitting power (dB)
rfm9x.tx_power = 23


def send_to_ground():
    """
    Reads a YAML file and sends the information to ground via radio
    """

    # Bitrate Budget https://docs.google.com/spreadsheets/d/1BNU0LOl0tzaBlsRqHiAFNp9Y_h9E01Kwud-uezHMNdA/edit#gid=1938337728
    # Must extend required headers and then include all required information from sensors

    filename = "filename.yaml"

    with open(filename) as file:
        data_from_file = yaml.load(file)

    # Should load a dictionary as such:
    # {
    # "acceleration"    :   (value1, value2, value3),
    # "gyro"            :   (value1, value2, value3),
    # "magnetic"        :   (value1, value2, value3),
    # "altitude"        :   (value),
    # "gps"             :   (value1, value2),
    # "temperature"     :   (value)
    # }

    # Every value should be an integer that can be stored in 4 bytes

    # 6-Byte FCC License Callsign - required for every packet
    callsign = bytes("CLSIGN", 'ASCII')

    # Byte array object with which to build our signal
    # It might be faster to build the bytearray all at once,
    # But building it over many extends is more readable
    data_bytearray = bytearray()
    data_bytearray.extend(callsign)

    for accel_val in data_from_file["acceleration"]:
        data_bytearray.extend(accel_val.to_bytes(4, 'big'))

    for gyro_val in data_from_file["gyro"]:
        data_bytearray.extend(gyro_val.to_bytes(4, 'big'))

    for mag_val in data_from_file["magnetic"]:
        data_bytearray.extend(mag_val.to_bytes(4, 'big'))

    for gps_val in data_from_file["gps"]:
        data_bytearray.extend(gps_val.to_bytes(4, 'big'))

    alt_val = data_from_file["altitude"][0]
    data_bytearray.extend(alt_val.to_bytes(4, 'big'))

    temp_val = data_from_file["temperature"][0]
    data_bytearray.extend(temp_val.to_bytes(4, 'big'))

    # To send a message, call send()
    rfm9x.send(bytes(data_bytearray))

    # Final message is 58 bytes
    # First 6 bytes is callsign
    # Rest of message is made of 4-byte numbers organized in this order:
    # Acceleration value 1, acceleration value 2, acceleration value 3
    # Gyro value 1, gyro value 2, gyro value 3
    # Magnetic value 1, magnetic value 2, magnetic value 3
    # Altitude value
    # GPS value 1, GPS value 2
    # Temperature value

    # This order is, of course, completely arbitrary

    # Note that the values are big-endian and will have to be decoded properly


# Testing - Must change function to accept an argument
# test_data = {
#     "acceleration"  :   (0, 1, 2),
#     "gyro"          :   (10, 11, 12),
#     "magnetic"      :   (20, 21, 22),
#     "altitude"      :   (30,),
#     "gps"           :   (40, 41),
#     "temperature"   :   (50,)
# }
#
# send_to_ground(test_data)
