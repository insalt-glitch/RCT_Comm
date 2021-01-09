"""This module handels communiation for the rct device

This module provides an easy to use interface to communicate with the
RctPowerStorage and perform crc-calculations.
"""
import socket
from time import sleep


def calc_crc(bitstream):
    """Calculate the CRC for the given input (int).

    We Calculate the CRC for the given integer. We use CRC-16 and initilize
    to 0xFFFF. In case of an odd number of bytes the necessary padding will be
    added automatically.

    Args:
        bitstream: The integer represting the binary to perform the crc on.
    Returns:
        crc: The integer resulting from the crc calculation.

    """
    # add padding
    bitstream <<= ((len(hex(bitstream))//2)%2)*8
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
    for _ in range(len(hex(response)[4:])):
        cut = (cut << 4) + 0xF
    # save the recieved checksum
    crc = response & 0xFFFF
    # remove parts of ther requests that dont belong to the crc
    bstream = response  & cut
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
        # connect send and recieve
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
        """Used to request data from the device.

        This method communicates with the device via tcp and requests the data
        specified by the parameter id.

        Args:
            command_byte: The Opertation that is to be performed. 1 byte hexvalue
            id: The data_id for the request. It is a 4 byte hex-value.
        """
        # generate package
        package = _gen_request(command_byte, data_log_id)
        package = bytes.fromhex(package)
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
        # init variables for communication
        buffer_size = 128
        fails = 0
        # try package request until it failed 5 times
        while fails < 5:
            data = 0
            self.__soc.send(package)
            bin_response = self.__soc.recv(buffer_size)
            # convert the byte obj back to an integer
            for val in bin_response:
                data = (data + val) << 8
            data >>= 8
            # check for error
            if _crc_check(data):
                return data
            # there was an error and we try again
            fails += 1

        if fails == 5:
            raise ConnectionError("No connection possible")

    def renew_socket(self):
        """ In case of connection problems with the device we renew the socket.
        """
        # wait to make sure connection can be closed properly
        sleep(10)
        self.__soc.close()
        # wait before esablishing a new connection on a new socket
        sleep(10)
        self.__soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__soc.connect((self.__ip, self.__port))
