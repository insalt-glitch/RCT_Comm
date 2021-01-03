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

import socket

def calc_crc(bitstream):
    """Calculate the CRC for the given input (int).

    We Calculate the CRC for the given integer. We use CRC-16 and initilize
    to 0xFFFF. In case of an odd number of bytes the userhas to add a padding
    at the end.

    Args:
        bitstream: The integer represting the binary to perform the crc on.
    Returns:
        crc: The integer resulting from the crc calculation.

    """
    # initilize crc
    crc = 0xFFFF
    # get bitstream length in bytes
    bytes_stream = len(hex(bitstream)) // 2
    for j in reversed(range(bytes_stream)):
        # for each byte calculate the crc and 'or' them together
        byte = (bitstream >> j * 8) & 0xFF
        for i in range(8):
            cond = (((crc >> 15) & 1) == 1) ^ ((byte >> (7-i) & 1) == 1)
            crc <<=1
            crc ^= 0x1021*cond
        crc &= 0xFFFF
    return crc

def _gen_request(command_byte, data_log_id):
    """Generate a valid request for the RctPowerDevice.

    This method will generate a string that when converted to a binary results
    in a valid package that can be send via tcp to the RctPowerDevice. It
    contains starts with '+' and then contains length, command_byte, id, crc
    in this specific order.
    IMPORTANT: At the moment this method only supports the command_byte '0x01'

    Args:
        command_byte: The Opertation that is to be performed. 1 byte hexvalue
        id: The data_id for the request. It is a 4 byte hex-value.
    Returns:
        request: A string that is can be used for tcp-communication with the
            right pattern already applied.
    """
    # create the stream containing command_byte, length, ID
    bstream = (command_byte << 8) + 4
    bstream = (bstream << 4 * 8) + data_log_id
    # calculate the length of the padded bitstream in binary
    l_bstream = len(hex(bstream)[2:])
    l_bstream = (l_bstream + (l_bstream) % 2) * 4
    # generate the full request
    request = (0x2B << l_bstream) + bstream
    request <<= 16
    request += calc_crc(bstream)
    # add padding if nessecary and return as string
    padding = '0' * (len(hex(request)) % 2)
    return padding + hex(request)[2:]

def _crc_check(response):
    """Checks wether a tcp-reponse is correcty recived using the _crc_check.

    Args:
        response: The full tcp-response as a integer.
    Returns:
        check: A binary true if the crc matches and false if not.
    """
    cut = 0
    #print("fullrepsonse: ", hex(response))
    for _ in range(len(hex(response)[4:])):
        cut = (cut << 4) + 0xF
    #print("cut-off", hex(cut))
    crc = response & 0xFFFF
    bstream = response  & cut
    #print("Bin-stream: ", bstream)
    #print("crc:", crc)
    bstream >>= 16
    bstream <<= (len(hex(response)[4:-4]) % 2) * 4
    return crc == calc_crc(bstream)

def _strip_data(package):
    """Get the actual data from the whole package.

    This will strip of everything except for the data part of the message.
    It will then return it as an integer.

    Args:
        data: The Integer represting the package data.
    Returns:
        data: The data from the tcp-package type int.
    """
    package >>= 16
    l_data = len(hex(package))-16
    cut = 0
    for _ in range(l_data):
        cut = (cut << 4) + 0xF
    return package & cut

class RctPowerDevice:
    """The RCT-Power device containing an interface for communication.

    This class represents the interface to tcp-communication with the
    RctPowerDevice, where data can be requested by calling the get method.

    Args:
        ip: The IP-Adress of the device in your network
        port: The port used for communication. This is usually 8899

    Raises:
        Connection-Error: If no connection can be estabished the method will
            time out and if the crc-checks fail we also raise an error.
    """
    __ip = None
    __port = None
    __soc = None
    def __init__(self, ip, port):
        """Constructor for RctPowerDevice

        Args:
            ip: The IP-Adress of the device in your network
            port: The port used for communication. This is usually 8899
        """
        # store ip and port
        self.__ip = ip
        self.__port = port
        # generate a socket of later use
        self.__soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #connect send and recieve
        self.__soc.connect((self.__ip, self.__port))

    def __del__(self):
        """Detructor for this class

        Delete the variables and close the socket.

        """
        self.__soc.close()
        del self.__ip
        del self.__port
        del self.__soc

    def get(self, command_byte, data_log_id):
        """Used to get request data from the device.

        This method communicates with the device via tcp and requests the data
        specified by the parameter id.

        Args:
            command_byte: The Opertation that is to be performed. 1 byte hexvalue
            id: The data_id for the request. It is a 4 byte hex-value.
        """
        # generate package
        package = bytes.fromhex(_gen_request(command_byte, data_log_id))
        data = self.__recieve_data(package)
        return _strip_data(data)

    def __recieve_data(self, package):
        """This method handles the tcp-communiation with the device.

        Here we perform the tcp-communiation using the socket of this class and
        do error checking. If we can not get a valid response with 5 tries then
        an error is raised.

        Args:
            package: The binary to send to the device.
        Returns:
            The data that was recieved from the device with dtype int (hex).

        Raises:
            Connection-Error: If no connection can be estabished the method will
                time out and if the crc-checks fail we also raise an error.
        """
        #init variables for communication
        data_log_id = 1024
        fails = 0
        data = 0
        #try package request until it failed 5 times
        while fails < 5:
            self.__soc.send(package)
            bin_response = self.__soc.recv(data_log_id)
            for val in bin_response:
                data = (data + val) << 8
            data >>= 8
            if _crc_check(data):
                break
            fails += 1
            data=0
        assert (not fails == 5), "Could not get data"
        return data
