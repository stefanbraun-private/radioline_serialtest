#!/usr/bin/env python
# encoding: utf-8
"""
radioline_serialtest/crc16_ifs.py

calculate CRC-16/IFS checksum.

(it seems that there exists many CRC implementations... :-/
but as "IO Ninja" showed and tested on https://crccalc.com/
RF modules *RAD-868-IFS* (c) by Phoenix Contact use the Modbus variant of CRC-16
but only using the lower byte of 16bit CRC value
)

Copyright (C) 2019 Stefan Braun



changelog:
v0.0.0, January 3th 2019 -- preparing start of project.



This program is free software: you can redistribute it and/or modify it under the terms of the
GNU General Public License as published by the Free Software Foundation, either version 2 of the License,
or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.
If not, see <http://www.gnu.org/licenses/>.
"""


def calc_crc(data):
    ''' calculate CRC-16 in IFS-variant '''

    # special thanks to Kevin Herron
    # from https://stackoverflow.com/questions/39101926/port-modbus-rtu-crc-to-python-from-c-sharp
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for i in range(8):
            if ((crc & 1) != 0):
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1

    # difference to CRC16 as used in Modbus: only using lower byte
    return crc & 0xFF



if __name__ == '__main__':

    # test: telegram "80 42 02 C1" must have checksum "0x49"
    assert calc_crc(bytearray.fromhex("80 42 02 C1")) == 0x49

    # test: telegram "80 04 00 70 00 04 EE" must have checksum "0x03"
    assert calc_crc(bytearray.fromhex("80 04 00 70 00 04 EE")) == 0x03

    # test: telegram "80 04 00 10 00 08 EE" must have checksum "0x18"
    assert calc_crc(bytearray.fromhex("80 04 00 10 00 08 EE")) == 0x18

    # test: telegram "80 42 02 01 08 01 1C 00 00 00 00 51 05 EA ED 14 A9" must have checksum "0xA9"
    assert calc_crc(bytearray.fromhex("80 42 02 01 08 01 1C 00 00 00 00 51 05 EA ED 14")) == 0xA9