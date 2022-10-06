# Simple demo of sending and recieving data with the RFM95 LoRa radio.
# much from https://learn.adafruit.com/adafruit-rfm69hcw-and-rfm96-rfm95-rfm98-lora-packet-padio-breakouts/circuitpython-for-rfm9x-lora

# initialize SPI connection with radio
import board
import busio
import digitalio

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


while True:

    # TODO Replace sample input with proper building of message based on sensor info
    # Sample input
    message_to_send = input("Message to send: ")
    message_bytes = bytes(message_to_send, "utf-8")  # You could save some bytes by only using ASCII

    # For the actual project:
    # Bitrate Budget https://docs.google.com/spreadsheets/d/1BNU0LOl0tzaBlsRqHiAFNp9Y_h9E01Kwud-uezHMNdA/edit#gid=1938337728
    # Must append required headers and then include all required information from sensors

    # To send a message, call send()
    rfm9x.send(message_bytes)
