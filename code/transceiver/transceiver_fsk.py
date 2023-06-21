import random
import time
import adafruit_bus_device.spi_device as spidev
from micropython import const

HAS_SUPERVISOR = False

try:
    import supervisor

    HAS_SUPERVISOR = hasattr(supervisor, "ticks_ms")
except ImportError:
    pass

try:
    from typing import Callable, Optional, Type
    from circuitpython_typing import WriteableBuffer, ReadableBuffer
    from digitalio import DigitalInOut
    from busio import SPI
except ImportError:
    pass


# Registers:
_REG_FIFO = const(0x00)
_REG_OP_MODE = const(0x01)
_REG_BITRATE_MSB = const(0x02)
_REG_BITRATE_LSB = const(0x03)
_REG_FDEV_MSB = const(0x04)
_REG_FDEV_LSB = const(0x05)
_REG_FRF_MSB = const(0x06)
_REG_FRF_MID = const(0x07)
_REG_FRF_LSB = const(0x08)
_REG_PA_CONFIG = const(0x09)
_REG_PA_RAMP = const(0x0A)
_REG_OCP = const(0x0B)
_REG_LNA = const(0x0C)
_REG_RX_CONFIG = const(0x0D)
_REG_RSSI_CONFIG = const(0x0E)
_REG_RSSI_COLLISION = const(0x0F)
_REG_RSSI_THRESH = const(0x10)
_REG_RSSI_VALUE = const(0x11)
_REG_RX_BW = const(0x12)
_REG_AFC_BW = const(0x13)
_REG_OOK_PEAK = const(0x14)
_REG_OOK_FIX = const(0x15)
_REG_OOK_AVG = const(0x16)
_REG_RESERVED_17 = const(0x17)
_REG_RESERVED_18 = const(0x18)
_REG_RESERVED_19 = const(0x19)
_REG_AFC_FEI = const(0x1A)
_REG_AFC_MSB = const(0x1B)
_REG_AFC_LSB = const(0x1C)
_REG_FEI_MSB = const(0x1D)
_REG_FEI_LSB = const(0x1E)
_REG_PREAMBLE_DETECT = const(0x1F)
_REG_RX_TIMEOUT_1 = const(0x20)
_REG_RX_TIMEOUT_2 = const(0x21)
_REG_RX_TIMEOUT_3 = const(0x22)
_REG_RX_DELAY = const(0x23)
_REG_OSC = const(0x24)
_REG_PREAMBLE_MSB = const(0x25)
_REG_PREAMBLE_LSB = const(0x26)
_REG_SYNC_CONFIG = const(0x27)
_REG_SYNC_VALUE_1 = const(0x28)
_REG_SYNC_VALUE_2 = const(0x29)
_REG_SYNC_VALUE_3 = const(0x2A)
_REG_SYNC_VALUE_4 = const(0x2B)
_REG_SYNC_VALUE_5 = const(0x2C)
_REG_SYNC_VALUE_6 = const(0x2D)
_REG_SYNC_VALUE_7 = const(0x2E)
_REG_SYNC_VALUE_8 = const(0x2F)
_REG_PACKET_CONFIG_1 = const(0x30)
_REG_PACKET_CONFIG_2 = const(0x31)
_REG_PAYLOAD_LENGTH = const(0x32)
_REG_NODE_ADRS = const(0x33)
_REG_BROADCAST_ADRS = const(0x34)
_REG_FIFO_THRESH = const(0x35)
_REG_SEQ_CONFIG_1 = const(0x36)
_REG_SEQ_CONFIG_2 = const(0x37)
_REG_TIMER_RESOL = const(0x38)
_REG_TIMER_1_COEF = const(0x39)
_REG_TIMER_2_COEF = const(0x3A)
_REG_IMAGE_CAL = const(0x3B)
_REG_TEMP = const(0x3C)
_REG_LOW_BAT = const(0x3D)
_REG_IRQ_FLAGS_1 = const(0x3E)
_REG_IRQ_FLAGS_2 = const(0x3F)
_REG_DIO_MAPPING_1 = const(0x40)
_REG_DIO_MAPPING_2 = const(0x41)
_REG_VERSION = const(0x42)
_REG_PLL_HOP = const(0x44)
_REG_TCXO = const(0x4B)
_REG_PA_DAC = const(0x4D)
_REG_FORMER_TEMP = const(0x5B)
_REG_BIT_RATE_FRAC = const(0x5D)
_REG_AGC_REF = const(0x61)
_REG_AGC_THRESH_1 = const(0x62)
_REG_AGC_THRESH_2 = const(0x63)
_REG_AGC_THRESH_3 = const(0x64)
_REG_PLL = const(0x70)

# Other internal constants:
_PA_DAC_DISABLE = const(0x04)
_PA_DAC_ENABLE = const(0x07)
_FX_OSC = 32e6 # Crystal oscillator frequency
_FSTEP = _FX_OSC / 524288 # Frequency synthesizer step (524288 is 2^19)
_RH_BROADCAST_ADDRESS = const(0xFF) # Broadcast address
_RH_FLAGS_ACK = const(0x80) # Acknowledgement bits in FLAGS
_RH_FLAGS_RETRY = const(0x40) # Retry bits in FLAGS
_TICKS_PERIOD = const(1 << 29)
_TICKS_MAX = const(_TICKS_PERIOD - 1)
_TICKS_HALFPERIOD = const(_TICKS_PERIOD // 2)

# User facing constants:
SLEEP_MODE = 0b000
STANDBY_MODE = 0b001
FS_TX_MODE = 0b010
TX_MODE = 0b011
FS_RX_MODE = 0b100
RX_MODE = 0b101


def ticks_diff(ticks1: int, ticks2: int) -> int:
    """Compute the signed difference between two ticks values
    assuming that they are within 2**28 ticks
    """
    diff = (ticks1 - ticks2) & _TICKS_MAX
    diff = ((diff + _TICKS_HALFPERIOD) & _TICKS_MAX) - _TICKS_HALFPERIOD
    return diff


def check_timeout(flag: Callable, limit: float) -> bool:
    """test for timeout waiting for specified flag"""
    timed_out = False
    if HAS_SUPERVISOR:
        start = supervisor.ticks_ms()
        while not timed_out and not flag():
            if ticks_diff(supervisor.ticks_ms(), start) >= limit * 1000:
                timed_out = True
    else:
        start = time.monotonic()
        while not timed_out and not flag():
            if time.monotonic() - start >= limit:
                timed_out = True
    return timed_out


class RFM9X_FSK:

    # Global buffer for SPI commands
    _BUFFER = bytearray(4)

    class _RegisterBits:

        def __init__(self, address: int, *, offset: int = 0, bits: int = 1) -> None:
            assert 0 <= offset <= 7
            assert 1 <= bits <= 8
            assert (offset + bits) <= 8
            self._address = address
            self._mask = 0
            for _ in range(bits):
                self._mask <<= 1
                self._mask |= 1
            self._mask <<= offset
            self._offset = offset

        def __get__(self, obj: "RFM9X_FSK", objtype: Type["RFM9X_FSK"]) -> int:
            reg_value = obj._read_u8(self._address)
            return (reg_value & self._mask) >> self._offset
        
        def __set__(self, obj: "RFM9X_FSK", val: int) -> None:
            reg_value = obj._read_u8(self._address)
            reg_value &= ~self._mask
            reg_value |= (val & 0xFF) << self._offset
            obj._write_u8(self._address, reg_value)

    operation_mode = _RegisterBits(_REG_OP_MODE, bits=3)
    low_frequency_mode = _RegisterBits(_REG_OP_MODE, offset=3, bits=1)
    modulation_type = _RegisterBits(_REG_OP_MODE, offset=5, bits=2)
    long_range_mode = _RegisterBits(_REG_OP_MODE, offset=7, bits=1)

    output_power = _RegisterBits(_REG_PA_CONFIG, bits=4)
    max_power = _RegisterBits(_REG_PA_CONFIG, offset=4, bits=3)
    pa_select = _RegisterBits(_REG_PA_CONFIG, offset=7, bits=1)

    pa_ramp = _RegisterBits(_REG_PA_RAMP, bits=4)
    modulation_shaping = _RegisterBits(_REG_PA_RAMP, offset=5, bits=2)

    lna_boost_hf = _RegisterBits(_REG_LNA, bits=2)
    lna_boost_lf = _RegisterBits(_REG_LNA, offset=3, bits=2)
    lna_gain = _RegisterBits(_REG_LNA, offset=5, bits=3)

    agc_auto_on = _RegisterBits(_REG_RX_CONFIG, offset=3, bits=1)

    rx_bw_exponent = _RegisterBits(_REG_RX_BW, bits=3)
    rx_bw_mantissa = _RegisterBits(_REG_RX_BW, offset=3, bits=2)

    afc_bw_exponent = _RegisterBits(_REG_AFC_BW, bits=3)
    afc_bw_mantissa = _RegisterBits(_REG_AFC_BW, offset=3, bits=2)

    sync_size = _RegisterBits(_REG_SYNC_CONFIG, bits=3)
    sync_on = _RegisterBits(_REG_SYNC_CONFIG, offset=4, bits=1)

    address_filter = _RegisterBits(_REG_PACKET_CONFIG_1, offset=1, bits=2)
    crc_auto_clear_off = _RegisterBits(_REG_PACKET_CONFIG_1, offset=3, bits=1)
    crc_on = _RegisterBits(_REG_PACKET_CONFIG_1, offset=4, bits=1)
    dc_free = _RegisterBits(_REG_PACKET_CONFIG_1, offset=5, bits=2)
    packet_format = _RegisterBits(_REG_PACKET_CONFIG_1, offset=7, bits=1)

    mode_ready = _RegisterBits(_REG_IRQ_FLAGS_1, offset=7, bits=1)

    dio_0_mapping = _RegisterBits(_REG_DIO_MAPPING_1, offset=6, bits=2)

    pa_dac = _RegisterBits(_REG_PA_DAC, bits=3)

    def __init__(
        self,
        spi: SPI,
        cs: DigitalInOut,
        reset: DigitalInOut,
        frequency: int,
        *,
        preamble_length: int = 8,
        high_power: bool = True,
        baudrate: int = int(5e6),
        node: int = _RH_BROADCAST_ADDRESS,
        destination: int = _RH_BROADCAST_ADDRESS
    ) -> None:
        
        self._device = spidev.SPIDevice(spi, cs, baudrate=baudrate, polarity=0, phase=0)

        self.high_power = high_power
        self.tx_power = 13
        
        self._reset = reset
        self._reset.switch_to_output(value=True)
        self.reset()

        version = self._read_u8(_REG_VERSION)
        if version != 18:
            raise RuntimeError("Failed to find RFM9X with expected version!")
        
        self.sleep()
        time.sleep(0.01)
        self.long_range_mode = False
        if self.operation_mode != SLEEP_MODE or self.long_range_mode:
            raise RuntimeError("Failed to configure radio for FSK mode!")
        if frequency > 525:
            self.low_frequency_mode = 0
        self.idle()

        self.frequency_mhz = frequency
        self.preamble_length = preamble_length
        
        self.modulation_shaping = 0b01
        self.bitrate = int(250e3)
        self.frequency_deviation = int(250e3)

        self.rx_bw_exponent = 0b000
        self.rx_bw_mantissa = 0b00
        self.afc_bw_exponent = 0b000
        self.afc_bw_mantissa = 0b00

        self.dc_free = 0b10
        self.packet_format = 1

        self.last_rssi = 0.0
        self.last_snr = 0.0

        self.ack_wait = 0.5
        self.ack_retries = 5
        self.ack_delay = None

        self.receive_timeout = 0.5
        self.transmit_timeout = 2.0
        
        self.sequence_number = 0
        self.seen_ids = bytearray(256)

        self.node = node
        self.destination = destination

        self.identifier = 0
        self.flags = 0

    def _read_into(self, address: int, buf: WriteableBuffer, length: Optional[int] = None) -> None:
        # Read a number of bytes from the specified address into the provided
        # buffer.  If length is not specified (the default) the entire buffer
        # will be filled.
        if length is None:
            length = len(buf)
        with self._device as device:
            self._BUFFER[0] = address & 0x7F  # Strip out top bit to set 0
            # value (read).
            device.write(self._BUFFER, end=1)
            device.readinto(buf, end=length)

    def _read_u8(self, address: int) -> int:
        # Read a single byte from the provided address and return it.
        self._read_into(address, self._BUFFER, length=1)
        return self._BUFFER[0]
    
    def _write_from(self, address: int, buf: ReadableBuffer, length: Optional[int] = None) -> None:
        # Write a number of bytes to the provided address and taken from the
        # provided buffer.  If no length is specified (the default) the entire
        # buffer is written.
        if length is None:
            length = len(buf)
        with self._device as device:
            self._BUFFER[0] = (address | 0x80) & 0xFF  # Set top bit to 1 to
            # indicate a write.
            device.write(self._BUFFER, end=1)
            device.write(buf, end=length)  # send data

    def _write_u8(self, address: int, val: int) -> None:
        # Write a byte register to the chip.  Specify the 7-bit address and the
        # 8-bit value to write to that address.
        with self._device as device:
            self._BUFFER[0] = (address | 0x80) & 0xFF  # Set top bit to 1 to
            # indicate a write.
            self._BUFFER[1] = val & 0xFF
            device.write(self._BUFFER, end=2)

    def reset(self) -> None:
        """Perform a reset of the chip."""
        # See section 7.2.2 of the datasheet for reset description.
        self._reset.value = False  # Set Reset Low
        time.sleep(100e-6)  # 100 us
        self._reset.value = True  # set Reset High
        time.sleep(5e-3)  # 5 ms

    def idle(self) -> None:
        """Enter idle standby mode."""
        self.operation_mode = STANDBY_MODE

    def sleep(self) -> None:
        """Enter sleep mode."""
        self.operation_mode = SLEEP_MODE

    def listen(self) -> None:
        """Listen for packets to be received by the chip.  Use :py:func:`receive`
        to listen, wait and retrieve packets as they're available.
        """
        self.operation_mode = RX_MODE
        self.dio0_mapping = 0b00  # Interrupt on rx done.

    def transmit(self) -> None:
        """Transmit a packet which is queued in the FIFO.  This is a low level
        function for entering transmit mode and more.  For generating and
        transmitting a packet of data use :py:func:`send` instead.
        """
        self.operation_mode = TX_MODE
        self.dio0_mapping = 0b00  # Interrupt on tx done.

    @property
    def preamble_length(self) -> int:
        """The length of the preamble for sent and received packets, an unsigned 16-bit value.
        Received packets must match this length or they are ignored! Set to 4 to match the
        RadioHead RFM69 library.
        """
        msb = self._read_u8(_REG_PREAMBLE_MSB)
        lsb = self._read_u8(_REG_PREAMBLE_LSB)
        return ((msb << 8) | lsb) & 0xFFFF
    
    @preamble_length.setter
    def preamble_length(self, val: int) -> None:
        assert 0 <= val <= 65535
        self._write_u8(_REG_PREAMBLE_MSB, (val >> 8) & 0xFF)
        self._write_u8(_REG_PREAMBLE_LSB, val & 0xFF)

    @property
    def frequency_mhz(self) -> float:
        """The frequency of the radio in Megahertz. Only the allowed values for your radio must be
        specified (i.e. 433 vs. 915 mhz)!
        """
        # FRF register is computed from the frequency following the datasheet.
        # See section 6.2 and FRF register description.
        # Read bytes of FRF register and assemble into a 24-bit unsigned value.
        msb = self._read_u8(_REG_FRF_MSB)
        mid = self._read_u8(_REG_FRF_MID)
        lsb = self._read_u8(_REG_FRF_LSB)
        frf = ((msb << 16) | (mid << 8) | lsb) & 0xFFFFFF
        frequency = (frf * _FSTEP) / 1000000.0
        return frequency
    
    @frequency_mhz.setter
    def frequency_mhz(self, val: float) -> None:
        assert 290 <= val <= 1020
        # Calculate FRF register 24-bit value using section 6.2 of the datasheet.
        frf = int((val * 1000000.0) / _FSTEP) & 0xFFFFFF
        # Extract byte values and update registers.
        msb = frf >> 16
        mid = (frf >> 8) & 0xFF
        lsb = frf & 0xFF
        self._write_u8(_REG_FRF_MSB, msb)
        self._write_u8(_REG_FRF_MID, mid)
        self._write_u8(_REG_FRF_LSB, lsb)

    @property
    def tx_power(self) -> int:
        """The transmit power in dBm."""
        if self.high_power and self.pa_select:
            return self.output_power + 5
        elif self.high_power:
            return self.output_power + 2
        else:
            return self.output_power
    
    @tx_power.setter
    def tx_power(self, val: int) -> None:
        val = int(val)
        if self.high_power:
            if val < 2 or val > 20:
                raise RuntimeError("tx_power must be between 2 and 20")
            if val > 17:
                self.pa_dac = _PA_DAC_ENABLE
                val -= 3
            else:
                self.pa_dac = _PA_DAC_DISABLE
            self.pa_select = True
            self.output_power = (val - 2) & 0x0F
        else:
            if val < 0 or val > 15:
                raise RuntimeError("tx_power must be between 0 and 15")
            self.pa_select = False
            self.max_power = 0b111 # Allow max power output.
            self.output_power = val & 0x0F

    @property
    def rssi(self) -> float:
        """The received strength indicator (in dBm) of the last received message."""
        return self._read_u8(_REG_RSSI_VALUE) / -2.0
    
    @property
    def bitrate(self) -> float:
        msb = self._read_u8(_REG_BITRATE_MSB)
        lsb = self._read_u8(_REG_BITRATE_LSB)
        return _FX_OSC / ((msb << 8) | lsb)
    
    @bitrate.setter
    def bitrate(self, val: float) -> None:
        if val < _FX_OSC / 65535 or val > 32e6:
            raise RuntimeError(f"bitrate must be between {round(_FX_OSC / 65535, 1)} and {32e6}")
        bitrate = int((_FX_OSC / val) + 0.5) & 0xFFFF
        self._write_u8(_REG_BITRATE_MSB, bitrate >> 8)
        self._write_u8(_REG_BITRATE_LSB, bitrate & 0xFF)

    @property
    def frequency_deviation(self) -> float:
        msb = self._read_u8(_REG_FDEV_MSB)
        lsb = self._read_u8(_REG_FDEV_LSB)
        return _FSTEP * ((msb << 8) | lsb)
    
    @frequency_deviation.setter
    def frequency_deviation(self, val: float) -> None:
        if val <= 0 or val > _FSTEP * 16383:
            raise RuntimeError(f"frequency deviation must be between 0 and 16383")
        fdev = int((val / _FSTEP) + 0.5) & 0x3FFF
        self._write_u8(_REG_FDEV_MSB, fdev >> 8)
        self._write_u8(_REG_FDEV_LSB, fdev & 0xFF)

    def packet_sent(self) -> bool:
        return (self._read_u8(_REG_IRQ_FLAGS_2) & 0x8) >> 3
    
    def payload_ready(self) -> bool:
        return (self._read_u8(_REG_IRQ_FLAGS_2) & 0x4) >> 2
    
    def send(
        self,
        data: ReadableBuffer,
        *,
        keep_listening: bool = False,
        destination: Optional[int] = None,
    ) -> bool:
        if len(data) <= 0 or len(data) > 62:
            raise RuntimeError("payload length must be between 1 and 62 bytes")
        self.idle()
        payload = bytearray(2)
        payload[0] = 1 + len(data)
        if destination is None:
            payload[1] = self.destination
        else:
            payload[1] = destination
        payload = payload + data
        self._write_from(_REG_FIFO, payload)
        self.transmit()
        timed_out = check_timeout(self.packet_sent, self.transmit_timeout)
        if keep_listening:
            self.listen()
        else:
            self.idle()
        return not timed_out

    def receive(
        self,
        *,
        keep_listening: bool = True,
        timeout: Optional[float] = None,
        with_header: bool = False,
        accept_broadcasts: bool = False
    ) -> int:
        timed_out = False
        if timeout is None:
            timeout = self.receive_timeout
        if timeout is not None:
            self.listen()
            timed_out = check_timeout(self.payload_ready, timeout)
        packet = None
        self.last_rssi = self.rssi
        self.idle()
        if not timed_out:
            fifo_length = self._read_u8(_REG_FIFO)
            if fifo_length > 0:
                packet = bytearray(fifo_length)
                self._read_into(_REG_FIFO, packet, fifo_length)
            if fifo_length < 2:
                packet = None
            else:
                receivable_packet = packet[0] == self.node or self.node == _RH_BROADCAST_ADDRESS
                receivable_broadcast = packet[0] == _RH_BROADCAST_ADDRESS and accept_broadcasts
                if not receivable_packet and not receivable_broadcast:
                    packet = None
                if not with_header and packet is not None:
                    packet = packet[1:]
        if keep_listening:
            self.listen()
        else:
            self.idle()
        return packet
