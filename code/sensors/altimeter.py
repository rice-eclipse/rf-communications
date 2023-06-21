from ms5803py import MS5803


class Altimeter:

    SEA_LEVEL_PRESSURE = 1008.4665 # mbar

    def __init__(self, bus=1, address=None):
        self.altimeter = MS5803(bus, address)

    def read(self):
        return self.altimeter.read()

    def altitude(pressure, temperature):
        return (Altimeter.SEA_LEVEL_PRESSURE / pressure) ** (1 / 5.257) - 1 * (temperature + 
                                                                               273.15) / 0.0065
