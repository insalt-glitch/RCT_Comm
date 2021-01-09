"""This module can be used to request data from a RCT Power-Storage

Note: The ID describes the requested information
Command Examples:
Start   Command(read)   length  ID (400F015b)        Checksum(CRC)
0x2B    0x01            0x04    0x40 0x0F 0x01 0x5B    0x58 0xB4

All ids that are not working:
[34, 103, 131, 151, 153, 154, 177, 182, 192, 202, 215, 225, 256, 265, 268,
280, 309, 322, 349, 361, 363, 379, 411, 414, 453, 477, 493, 533, 550, 551,
570, 576, 581, 605, 614, 636, 637, 647, 648, 689, 694, 702, 703, 710, 721,
756, 767, 777, 781, 798, 803, 808, 847, 849, 865, 870, 887]
"""
from rctcomm import RctPowerDevice
from data_handling import data_conversion
from id_catalog import make_table

def print_data_to_cli(data, request_id, idtable):
    """Prints the input data of the current request to cli

    Args:
        data: The recieved request from the Power-Storage
        data_request: The id of the current request.
        idtable: A nested list of all the ids and descriptions.
    """
    data = data_conversion(data, idtable[request_id][1])
    print("({}) ".format(request_id) + idtable[request_id][2] +
          ": {:}".format(data))

def main(tcp_ip, tcp_port):
    """Main method for this module.

    We create a device and request some data. Then we print it.

    Args:
        tcp_ip: The IP of the device.
        tcp_port: The Port of the device.
    """
    idtable = make_table("ID_table.txt")
    # create MSG
    command = 0x01
    # create device
    device = RctPowerDevice(tcp_ip, tcp_port)
    # Insert the ids of the data you want to have
    requests = list(range(20))

    # For each id we recieve the data and output to the CLI
    for request_id in requests:
        data = 0
        try:
            data = device.get(command, idtable[request_id][0])
        except ConnectionError:
            print("({}) No connection possible for ".format(request_id) +
            "{}.".format(idtable[request_id][2]))
            device.renew_socket()
            continue
        # PROBLEM does not support int and enum
        print_data_to_cli(data, request_id, idtable)

if __name__ == "__main__":
    TCP_IP   = "192.168.43.175"
    TCP_PORT = 8899
    main(TCP_IP, TCP_PORT)
