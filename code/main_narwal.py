import sys
import os.path

full_path = os.path.realpath(__file__)
projectdir = os.path.dirname(os.path.dirname(full_path))
importdir = os.path.join(projectdir, "fsk")
sys.path.insert(0, importdir)

import radio_fsk

CONFIG_FILENAME = "config_narwal.yaml"

trx = radio_fsk.Radio_FSK(CONFIG_FILENAME)

while True:
    data = trx.receive_and_log()
    print(f"{data}\n")