from enum import Enum
import yaml
import busio
import digitalio
from digitalio import DigitalInOut as DIO
import board
import struct
import time
import os
import sys

sys.path.append('/home/pi/rf-communications/code/transceiver')
from transceiver_fsk import RFM9X_FSK as TRX


class AmpMode(Enum):
	DISABLED = 'D'
	BYPASS	 = 'B'
	TRANSMIT = 'T'
	RECEIVE  = 'R'


class Command(Enum):
	NULL = 0
	SHUTDOWN = 100
	START = 101
	STOP = 102
	PAUSE = 103
	RESUME = 104


class Radio_FSK:

	DATA_TYPES = {'int8':'b', 'int16':'h', 'int32':'i', 'int64':'q',
	  'uint8':'B', 'uint16':'H', 'uint32':'I', 'uint64':'Q',
	  'float32':'f', 'float64':'d', 'bool':'?'}


	'''
	Constructs a Radio_FSK object with the given configuration.
	
	Parameters:
		config_filename:	the path to a valid radio config file

	Returns:
		None
	'''
	def __init__(self, config_filename):

		print("Radio initializing...")

		# Import configuration from config file
		with open(config_filename, 'r') as stream:
			self.config = yaml.safe_load(stream)

		# Save configuration info
		self.frequency = self.config['frequency']
		self.fdev = self.config['fdev']
		self.bitrate = self.config['bitrate']
		self.tx_power = self.config['tx_power']
		self.amp_mode = AmpMode(self.config['amp_mode'])
		self.timeout = self.config['timeout']
		self.packet_delay = self.config['packet_delay']
		self.self_address = self.config['self_address']
		self.dest_address = self.config['dest_address']
		self.accept_broad = self.config['accept_broad']
		self.verbose = self.config['verbose']
		self.log_name = self.config['log_name']
		self.log_dir = self.config['log_dir']
		self.pins_trx = self.config['pins']['transceiver']
		self.pins_swA = self.config['pins']['switch_A']
		self.pins_swB = self.config['pins']['switch_B']
		self.send_pkt_num = self.config['send_pkt_num']
		self.send_time = self.config['send_time']
		self.call_sign = self.config['call_sign']
		self.packet_def = self.config['packet_def']

		# Declare transceiver
		cs = DIO(getattr(board, self.pins_trx['cs']))
		reset = DIO(getattr(board, self.pins_trx['reset']))
		sck = getattr(board, self.pins_trx['sck'])
		mosi = getattr(board, self.pins_trx['mosi'])
		miso = getattr(board, self.pins_trx['miso'])
		spi = busio.SPI(clock=sck, MOSI=mosi, MISO=miso)

		# Initialize transceiver
		self.trx = TRX(spi, cs, reset, self.frequency, node=self.self_address, 
		 destination=self.dest_address)
		self.trx.frequency_deviation = self.fdev
		self.trx.bitrate = self.bitrate
		self.trx.tx_power = self.tx_power

		# Initialize RF Switches
		self.set_amp_mode(AmpMode(self.amp_mode))

		# Calculate packet size
		self.packet_size = 0

		if self.send_pkt_num:
			self.packet_size += struct.calcsize(Radio_FSK.DATA_TYPES['uint32'])
		if self.send_time:
			self.packet_size += struct.calcsize(Radio_FSK.DATA_TYPES['uint64'])
		if self.call_sign != None:
			self.packet_size += len(bytes(self.call_sign, 'ascii'))
		
		for var_def in self.packet_def:
			var_type = list(var_def.values())[0]
			self.packet_size += struct.calcsize(Radio_FSK.DATA_TYPES[var_type])

		if self.packet_size > 62:
			raise Exception(f"Packet size too large: {self.packet_size} > 62 bytes")
		
		# Initialize sent packet counters
		self.packets_sent = 0
		self.packets_received = 0

		# Initialize log directory and filename
		if self.log_name != None:
			self.log_name = f"{self.log_name}_{time.time()}.yaml"

		print("Radio initialization complete.")


	'''
	Switches the amplifier mode to the given mode.

	Parameters:
		mode: the AmpMode to switch to. It is not possible to switch from a non-disabled mode
			  to the disabled mode

	Returns:
		None
	'''
	def set_amp_mode(self, mode):

		if mode == AmpMode.DISABLED:
			if self.amp_mode != AmpMode.DISABLED:
				print("Cannot switch non-disabled amplifier mode to disabled")
			return
		
		self.amp_mode = mode

		swA_ctrl1 = DIO(getattr(board, self.pins_swA['ctrl1']))
		swA_ctrl2 = DIO(getattr(board, self.pins_swA['ctrl2']))
		swB_ctrl1 = DIO(getattr(board, self.pins_swB['ctrl1']))
		swB_ctrl2 = DIO(getattr(board, self.pins_swB['ctrl2']))

		swA_ctrl1.direction = digitalio.Direction.OUTPUT
		swA_ctrl2.direction = digitalio.Direction.OUTPUT
		swB_ctrl1.direction = digitalio.Direction.OUTPUT
		swB_ctrl2.direction = digitalio.Direction.OUTPUT

		ctrls = {}
		ctrls[AmpMode.BYPASS] = [False, True, False, True]
		ctrls[AmpMode.TRANSMIT] = [True, False, True, True]
		ctrls[AmpMode.RECEIVE] = [True, True, True, False]

		swA_ctrl1.value, swA_ctrl2.value, swB_ctrl1.value, swB_ctrl2.value = ctrls[self.amp_mode]


	'''
	Transmits a packet containing the given data.
	
	Parameters:
		data: a dictionary formatted according to the packet definition specified by the config 
		  file provided on init
		
	Returns:
		None
	'''
	def send(self, data):

		data_bytes = bytearray()

		if self.send_pkt_num:
			data_bytes.extend(struct.pack(f">{Radio_FSK.DATA_TYPES['uint32']}", self.packets_sent))
		if self.send_time:
			data_bytes.extend(struct.pack(f">{Radio_FSK.DATA_TYPES['uint64']}", time.time_ns()))

		for var_def in self.packet_def:
			var_name = list(var_def.keys())[0]
			var_type = list(var_def.values())[0]
			packed_val = struct.pack(f">{Radio_FSK.DATA_TYPES[var_type]}", data[var_name])
			data_bytes.extend(packed_val)

		if self.call_sign != None:
			data_bytes.extend(bytes(self.call_sign, 'ascii'))

		if len(data_bytes) != self.packet_size:
			print(f"Packet size {len(data_bytes)} is invalid for config size {self.packet_size}")
			return
		
		self.trx.send(bytes(data_bytes))
		self.packets_sent += 1
		if self.verbose:
			print("Packet transmitted successfully.")
		time.sleep(self.packet_delay)


	'''
	Receives a single packet and returns its interpreted contents.
	
	Parameters:
		None

	Returns:
		A dictionary with keys adhering to the packet definition specified by the config file
		provided on init, plus '_rssi' and possibly '_pkt_num', and/or '_time' as appropriate, and
		with values extracted from the received packet.
	'''
	def receive(self):

		packet = self.trx.receive(timeout=self.timeout, accept_broadcasts=self.accept_broad)

		if packet is None:
			if self.verbose:
				print("No packets received.")
			return None
		
		if len(packet) != self.packet_size:
			print(f"Received packet size {len(packet)} invalid for config size {self.packet_size}")
			return None
		
		data = {}

		if self.send_pkt_num:
			type = Radio_FSK.DATA_TYPES['uint32']
			pkt_num_raw = packet[:struct.calcsize(type)]
			data['_pkt_num'] = struct.unpack(f">{type}", pkt_num_raw)[0]
			packet = packet[struct.calcsize(type):]

		if self.send_time:
			type = Radio_FSK.DATA_TYPES['uint64']
			time_raw = packet[:struct.calcsize(type)]
			data['_time'] = struct.unpack(f">{type}", time_raw)[0]
			packet = packet[struct.calcsize(type):]

		for var_def in self.packet_def:
			var_name = list(var_def.keys())[0]
			var_type = Radio_FSK.DATA_TYPES[list(var_def.values())[0]]
			packed_val = packet[:struct.calcsize(type)]
			data[var_name] = struct.unpack(f"{type}", packed_val)[0]
			packet = packet[struct.calcsize(type):]

		if self.call_sign != None:
			call_sign = str(packet[:len(bytes(self.call_sign, 'ascii'))], 'ascii')
			if call_sign != self.call_sign:
				print(f"Packet with call sign {call_sign} invalid for config with {self.call_sign}")
				return None

		data['_rssi'] = self.trx.rssi

		self.packets_received += 1
		if self.verbose:
			print("Packet received successfully.")
		return data
	

	def send_and_log(self, data):

		if data is not None:
			data['_source'] = 'transmitted'
		
		path = ""

		if self.log_name != None:
			if self.log_dir != None:
				path += f"{self.log_dir}/"
				if not os.path.exists(self.log_dir):
					os.makedirs(self.log_dir)
			path += self.log_name
			
			with open(path, 'a', buffering=1) as log_file:
				yaml.dump([data], log_file)
				log_file.flush()

			if self.verbose:
				print("Transmitted data successfully written to log file.")

		elif self.verbose:
			print("Cannot log with non-logging config")

		if data is not None:
			data.pop('_source')
		self.send(data)

		
	def receive_and_log(self):

		data = self.receive()
		if data is not None:
			data['_source'] = 'received'

		path = ""

		if self.log_name != None:
			if self.log_dir != None:
				path += f"{self.log_dir}/"
				if not os.path.exists(self.log_dir):
					os.makedirs(self.log_dir)
			path += self.log_name
			
			with open(path, 'a', buffering=1) as log_file:
				yaml.dump([data], log_file)
				log_file.flush()

			if self.verbose:
				print("Received data successfully written to log file.")

		elif self.verbose:
			print("Cannot log with non-logging config")

		if data is not None:
			data.pop('_source')
		return data
