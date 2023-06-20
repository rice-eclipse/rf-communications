import time

import radio_fsk

CONFIG_FILENAME = "config_rtr.yaml"

trx = radio_fsk.Radio_FSK(CONFIG_FILENAME)

# while True:
#     packet = {}
#     packet['command'] = 0
#     packet['pressure'] = 1
#     packet['temperature'] = 2
#     packet['altitude'] = 4
#     packet['latitude'] = 7.8
#     packet['longitude'] = 11.12
#     packet['altitude_gps'] = 16.171819
#     packet['fix_quality'] = 3
#     packet['satellites'] = 120
#     trx.send(packet)

def main():
    while True:
        data = trx.receive_and_log()

        if data is not None:
            if data['command'] == radio_fsk.Command.NULL.value:
                print("NULL command received.")
            elif data['command'] == radio_fsk.Command.SHUTDOWN.value:
                print("SHUTDOWN command received.")
                exit()
            elif data['command'] == radio_fsk.Command.START.value:
                print("START command received.")
                break
            else:
                print(f"Command {data['command']} not implemented or invalid")
        else:
            print("No commands received.")

        time.sleep(10)

    while True:
        packet = {}
        packet['command'] = 0
        packet['pressure'] = 1
        packet['temperature'] = 2
        packet['altitude'] = 4
        packet['latitude'] = 7.8
        packet['longitude'] = 11.12
        packet['altitude_gps'] = 16.171819
        packet['fix_quality'] = 3
        packet['satellites'] = 120
        trx.send(packet)

if __name__ == None:
    main()