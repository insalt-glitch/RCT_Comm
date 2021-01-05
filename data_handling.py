"""Module for handling the conversions of different types that come from the device

"""
def to_string_conv(data):
    str_data = ''
    for _ in range(len(hex(data))//2):
        str_data += chr(data & 0xFF)
        data >>= 8
    return str_data

def to_float_conv(n, sgn_len=1, exp_len=8, mant_len=23):
    """
    Converts an arbitrary precision Floating Point number.
    Note: Since the calculations made by python inherently use floats, the
        accuracy is poor at high precision.
    :param n: An unsigned integer of length `sgn_len` + `exp_len` + `mant_len`
        to be decoded as a float
    :param sgn_len: number of sign bits
    :param exp_len: number of exponent bits
    :param mant_len: number of mantissa bits
    :return: IEEE 754 Floating Point representation of the number `n`
    """
    if n >= 2 ** (sgn_len + exp_len + mant_len):
        raise ValueError("Number n is longer than prescribed parameters allows")

    sign = (n & (2 ** sgn_len - 1) * (2 ** (exp_len + mant_len))) >> (exp_len + mant_len)
    exponent_raw = (n & ((2 ** exp_len - 1) * (2 ** mant_len))) >> mant_len
    mantissa = n & (2 ** mant_len - 1)

    sign_mult = 1
    if sign == 1:
        sign_mult = -1

    if exponent_raw == 2 ** exp_len - 1:  # Could be Inf or NaN
        if mantissa == 2 ** mant_len - 1:
            return float('nan')  # NaN

        return sign_mult * float('inf')  # Inf

    exponent = exponent_raw - (2 ** (exp_len - 1) - 1)

    if exponent_raw == 0:
        mant_mult = 0  # Gradual Underflow
    else:
        mant_mult = 1

    for b in range(mant_len - 1, -1, -1):
        if mantissa & (2 ** b):
            mant_mult += 1 / (2 ** (mant_len - b))

    return sign_mult * (2 ** exponent) * mant_mult

def data_conversion(data, d_type):
    """Data conversion from int to the specified type.

    """
    if d_type == 'string':
        data = to_string_conv(data)
    elif d_type == 'float':
        data = to_float_conv(data)
    elif 'uint' in d_type:
        pass
    elif d_type == 'bool':
        data = bool(data)
    return data
