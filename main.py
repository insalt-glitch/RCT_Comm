"""IP-Adresse: 192.168.43.136

Note: The ID describes the requested information
Command Examples:
Start   Command(read)   length  ID (400F015b)        Checksum(CRC)
0x2B    0x01            0x04    0x40 0x0F 0x01 0x5B    0x58 0xB4

One Hex Value:0x2B0104400F015B58B4
For CRC(no start and no crc):0x0104400F015B
CRC:        0x58B4
in binary:  0b0101100010110100
"""
from time import sleep
from rctcomm import RctPowerDevice
from data_handling import int_to_float_conv

def main(tcp_ip, tcp_port):
    """Main method for this module.

    We create a device and request some data. Then we print it.

    Args:
        tcp_ip: The IP of the device.
        tcp_port: The Port of the device.
    """
    #create MSG
    command     = 0x01
    data_log_id = 0xAFDD6CF
    #create device
    device = RctPowerDevice(tcp_ip, tcp_port)
    #get data and print it to cli
    while True:
        data = device.get(command, data_log_id)
        print(int_to_float_conv(data))
        sleep(1)

if __name__ == "__main__":
    TCP_IP   = "192.168.43.175"
    TCP_PORT = 8899
    main(TCP_IP, TCP_PORT)
