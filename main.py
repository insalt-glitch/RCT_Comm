"""IP-Adresse: 192.168.43.136

Note: The ID describes the requested information
Command Examples:
Start   Command(read)   length  ID (400F015b)        Checksum(CRC)
0x2B    0x01            0x04    0x40 0x0F 0x01 0x5B    0x58 0xB4

One Hex Value:0x2B0104400F015B58B4
For CRC(no start and no crc):0x0104400F015B
CRC:        0x58B4
in binary:  0b0101100010110100
All ids that are not working:
[34, 103, 131, 151, 153, 154, 177, 182, 192, 202, 215, 225, 256, 265, 268,
280, 309, 322, 349, 361, 363, 379, 411, 414, 453, 477, 493, 533, 550, 551,
570, 576, 581, 605, 614, 636, 637, 647, 648, 689, 694, 702, 703, 710, 721,
756, 767, 777, 781, 798, 803, 808, 847, 849, 865, 870, 887]
"""
from rctcomm import RctPowerDevice
from data_handling import data_conversion
from id_catalog import make_table

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
    # 256 is not working dont know why
    requests = list(range(896))
    for data_request in requests:
        # get data and print it to cli
        data = 0
        try:
            #print(hex(idtable[data_request][0]))
            data = device.get(command, idtable[data_request][0])
        except ConnectionError:
            print("({}) No connection possible for ".format(data_request) +
            "{}, ".format(idtable[data_request][2]) +
            "this might be a internal device error!")
            device.renew_socket()
            continue
        # PROBLEM does not support int and enum
        data = data_conversion(data, idtable[data_request][1])
        print("({}) ".format(data_request) + idtable[data_request][2] + ": {:}".format(data))

if __name__ == "__main__":
    TCP_IP   = "192.168.43.175"
    TCP_PORT = 8899
    main(TCP_IP, TCP_PORT)
