from enum import Enum
import yaml
import busio
from digitalio import DigitalInOut as dIO
import board
import adafruit_rfm9x
import struct
import time

class AmpMode(Enum):
	DISABLED = 'D'
	BYPASS	 = 'B'
	TRANSMIT = 'T'
	RECEIVE  = 'R'

class Radio:

	DATA_TYPES = {'int8':'b', 'int16':'h', 'int32':'i', 'int64':'q',
	  'uint8':'B', 'uint16':'H', 'uint32':'I', 'uint64':'Q',
	  'float32':'f', 'float64':'d', 'bool':'?'}

	def __init__(self, config_filename):

		print("Radio initializing...")

		# Import configuration from config file
		with open(config_filename, 'r') as stream:
			self.config = yaml.safe_load(stream)

		# Save configuration info
		self.frequency = self.config['frequency']
		self.bandwidth = self.config['bandwidth'] * 10**3
		self.spreading = self.config['spreading']
		self.tx_power = self.config['tx_power']
		self.amp_mode = AmpMode(self.config['amp_mode'])
		self.timeout = self.config['timeout']
		self.coding_rate = self.config['coding_rate']
		self.baudrate = self.config['baudrate'] * 10**6
		self.callsign = self.config['callsign']
		self.send_packet_n = self.config['send_packet_n']
		self.send_time = self.config['send_time']
		self.magic = self.config['magic']
		self.pins_trx = self.config['pins']['transceiver']
		self.pins_swA = self.config['pins']['switch_A']
		self.pins_swB = self.config['pins']['switch_B']
		self.packetdef = self.config['packetdef']

		# Declare transceiver
		cs = dIO(getattr(board, self.pins_trx['cs']))
		reset = dIO(getattr(board, self.pins_trx['reset']))
		sck_id = getattr(board, self.pins_trx['sck'])
		mosi_id = getattr(board, self.pins_trx['mosi'])
		miso_id = getattr(board, self.pins_trx['miso'])
		spi = busio.SPI(clock=sck_id, MOSI=mosi_id, MISO=miso_id)

		# Initialize transceiver
		self.trx = adafruit_rfm9x.RFM9x(spi, cs, reset, self.frequency, self.baudrate)
		self.trx.signal_bandwidth = self.bandwidth
		self.trx.spreading_factor = self.spreading
		self.trx.tx_power = self.tx_power
		self.trx.coding_rate = self.coding_rate

		# Declare & initialize RF switches
		if self.amp_mode != AmpMode.DISABLED:
			swA_ctrl1 = dIO(getattr(board, self.pins_swA['ctrl1']))
			swA_ctrl2 = dIO(getattr(board, self.pins_swA['ctrl2']))
			swB_ctrl1 = dIO(getattr(board, self.pins_swB['ctrl1']))
			swB_ctrl2 = dIO(getattr(board, self.pins_swB['ctrl2']))

			ctrls = {}
			ctrls[AmpMode.BYPASS] = [False, True, False, True]
			ctrls[AmpMode.TRANSMIT] = [True, False, True, True]
			ctrls[AmpMode.RECEIVE] = [True, True, True, False]

			swA_ctrl1.value, swA_ctrl2.value, swB_ctrl1.value, swB_ctrl2.value = ctrls[self.amp_mode]

		# Calculate packet size
		self.packet_size = 0

		if self.callsign != None:
			self.packet_size += len(bytes(self.callsign, 'ascii'))
		if self.send_packet_n:
			self.packet_size += struct.calcsize(Radio.DATA_TYPES['uint32'])
		if self.send_time:
			self.packet_size += struct.calcsize(Radio.DATA_TYPES['uint64'])
		if self.magic != None:
			self.packet_size += struct.calcsize(Radio.DATA_TYPES['uint8'])

		for _, var_type in self.packetdef:
			self.packet_size += struct.calcsize(Radio.DATA_TYPES[var_type])

		if self.packet_size >= 252:
			raise Exception(f"Packet size too large: {self.packet_size} > 252 bytes")
		
		# Initialize sent packet count
		self.packets_sent = 0
		self.packets_received = 0

		print("Radio initialization complete")


	def send(self, data):
		
		data_bytes = bytearray()

		if self.callsign != None:
			data_bytes.extend(bytes(self.callsign, 'ascii'))
		if self.send_packet_n:
			data_bytes.extend(struct.pack(f">{self.packets_sent}", Radio.DATA_TYPES['uint32']))
		if self.send_time:
			data_bytes.extend(struct.pack(f">{time.time_ns}", Radio.DATA_TYPES['uint64']))

		for var_name, var_type in self.packetdef:
			val = data[var_name]
			data_bytes.extend(struct.pack(f">{val}", Radio.DATA_TYPES[var_type]))

		if self.magic != None:
			data_bytes.extend(struct.pack(f">{self.magic}", Radio.DATA_TYPES['uint8']))

		if len(data_bytes) != self.packet_size:
			print(f"Packet of size {len(data_bytes)} is invalid for config with size {self.packet_size}")
			return

		self.trx.send(bytes(data_bytes))
		self.packets_sent += 1
		print("Packet transmitted successfully")
	

	def receive(self):

		packet = self.trx.receive(timeout=self.timeout)

		if packet is None:
			print("No packets received")
			return None
		
		if len(packet) != self.packet_size:
			print(f"Received packet of size {len(packet)} is invalid for config with size {self.packet_size}")
			return None
		
		data = {}

		if self.callsign != None:
			callsign = str(packet[:len(bytes(self.callsign, 'ascii'))], 'ascii')
			if callsign != self.callsign:
				print(f"Received packet with callsign {callsign} is invalid for config with callsign {self.callsign}")
				return None
			data['callsign'] = callsign
			packet = packet[len(bytes(self.callsign, 'ascii')):]
			
		if self.magic != None:
			magic = packet[-struct.calcsize(Radio.DATA_TYPES['uint8']):]
			if magic != self.magic:
				print(f"Received packet with magic {magic} is invalid for config with magic {self.magic}")
				return None
			data['magic'] = magic
			packet = packet[:-struct.calcsize(Radio.DATA_TYPES['uint8'])]

		for var_name, var_type in self.packetdef:
			pass

		print("Packet received successfully")

