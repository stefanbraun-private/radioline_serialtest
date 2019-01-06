#!/usr/bin/env python
# encoding: utf-8
"""
radioline_serialtest/main.py

*radioline_serialtest* is a small debugging tool for serial communication to
RF modules *RAD-868-IFS* (c) by Phoenix Contact via IFS dataport.


Copyright (C) 2019 Stefan Braun


changelog:
v0.0.1, January 6th 2019 -- Release v0.0.1
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

import serial
import sys
import struct
import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5 import uic
from radioline_serialtest.crc16_ifs import calc_crc


# help from https://pythonspot.com/pyqt5-buttons/
from PyQt5.QtCore import pyqtSlot

VERSION = '0.0.1'

#ui file
Form_Main, Base_Main = uic.loadUiType('UI/MainWindow.ui')

# timeout [s] for reading and writing
SERIAL_TIMEOUT = 3.0

# byte commands on IFS-dataport
# (reverse engineered: using "IO Ninja" for serial monitoring "PSI-CONF" talking to this RF modules)
# =>currently we only ask for serial number of RF-module,
#   this is the first action of "PSI-CONF" when establishing connection via IFS-dataport
IFS_GET_SERIAL = '80 42 02 C1 49'


class MainWindow(Base_Main, Form_Main):
    def __init__(self):
        super(Base_Main, self).__init__()
        self.setupUi(self)

        self.label_version.setText(VERSION)

        self._collect_comports()

        self.connect_button.clicked.connect(self.on_click)


    def _collect_comports(self):
        # scan on local system for available serial COM ports
        # help from https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
        ports = ['COM%s' % (i + 1) for i in range(255)]
        avail_ports = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                self.comboBox.addItem(port)
                avail_ports.append(port)
            except (OSError, serial.SerialException):
                pass
        if avail_ports:
            self.log_info('Available COM-ports: ' + ', '.join(avail_ports))
        else:
            self.log_error('No unused COM-ports found! Perhaps already in use by another program?')


    @pyqtSlot()
    def on_click(self):
        ''' connect and read from serial device '''

        port = self.comboBox.itemText(self.comboBox.currentIndex())

        # help from https://pyserial.readthedocs.io/en/latest/shortintro.html
        # and https://pyserial.readthedocs.io/en/latest/pyserial_api.html
        ser = serial.Serial()
        ser.port = port
        ser.baudrate = 115200
        ser.bytesize = serial.EIGHTBITS
        ser.parity = serial.PARITY_EVEN
        ser.stopbits = serial.STOPBITS_ONE
        ser.timeout = SERIAL_TIMEOUT   # timeout for reading
        ser.xonxoff = False
        ser.rtscts = False
        ser.dsrdtr = False
        ser.write_timeout = 0
        try:
            self.log_info(
                'Trying to open serialport "' + port + '" with settings "115200,8,E,1,no flow control,timeout 5s"...')
            ser.open()

            # help from https://stackoverflow.com/questions/32018993/how-can-i-send-a-byte-array-to-a-serial-port-using-python
            self.log_info('Trying to request serial number from attached RF-module...')
            self.log_info('')
            data = bytearray.fromhex(IFS_GET_SERIAL)
            self.log_info('Sending bytes "' + IFS_GET_SERIAL + '" [total ' + str(len(data)) + ' bytes] to IFS-dataport...')
            ser.write(data)

            self.log_info('Trying to receive 17 bytes from IFS-dataport...')
            # read() blocks until number of bytes were received or timeout is over
            frame = ser.read(17)
            if not frame:
                raise Exception('RF-module did not answer after ' + str(SERIAL_TIMEOUT) + ' seconds')


            # help from https://stackoverflow.com/questions/6624453/whats-the-correct-way-to-convert-bytes-to-a-hex-string-in-python-3
            # FIXME: simple solution for printing hex numbers "AABBDD" in readable format "AA BB DD"...? :-/
            mylist = []
            for idx, char in enumerate(frame.hex()):
                mylist.append(char)
                if idx % 2 == 1:
                    mylist.append(' ')
            frame_string = ''.join(mylist).strip()
            self.log_info('Received "' + frame_string + '" [total ' + str(len(frame)) + ' bytes]')
            self.log_info('')

            # interpretation of response
            # example:
            #  "PSI-CONF" sends command "80 42 02 c1 49"
            #  "RAD-868-IFS" answers with "80 42 02 01 08 01 1c 00 00 00 00 51 05 ea ed 14 a9"
            self.log_info('Validation of response...')

            assert len(frame) == 17, 'wrong frame length: expected 17 bytes, got ' + str(len(frame)) + ' bytes'

            # help from https://stackoverflow.com/questions/16414559/how-to-use-hex-without-0x-in-python
            assert frame[0] == 0x80, 'wrong frame start character: expected "80", got "' + format(frame[0], 'x') + '"'

            crc = calc_crc(frame[:-1])
            assert frame[-1] == crc, 'wrong checksum: expected "{}", got "{}"'.format(format(crc, 'x'), format(frame[-1], 'x'))

            self.log_info('Response from attached RF-module seems valid. :-)')

            # FIXME: byte-to-int conversion in Python 3: why does PyQt5 terminate with exit code 3, while in Python console it works as expected?!?
            # help from https://stackoverflow.com/questions/34009653/bytes-to-int-python-3
            #serial_int = int.from_bytes(frame[11:15], byteorder='big', signed=False)

            # workaround: help from https://www.delftstack.com/howto/python/how-to-convert-bytes-to-integers/
            serial_int = struct.unpack('>i', frame[11:15])[0]
            self.log_info('Serial number of the RF-module: ' + str(serial_int))
            self.log_info('')
            self.log_info('******** serial connection test was successful ********')
            self.log_info('')


        except Exception as ex:
            self.log_error('Got exception "' + str(ex) + '"!')
        finally:
            self.log_info('Closing serialport "' + port + '"')
            self.log_info('========================================================')
            self.log_info('')



        # todo: init serial port, write into text field, ..

    def log_error(self, msg):
        self._log('red', 'ERROR:\t{}'.format(msg))

    def log_info(self, msg):
        self._log('black', 'INFO:\t{}'.format(msg))

    def _log(self, color, msg):
        ''' append logmessage to textBrowser widget '''

        # help from https://stackoverflow.com/questions/311627/how-to-print-a-date-in-a-regular-format
        # and http://strftime.org/
        time_str = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        row = ' - '.join([time_str, msg])

        # help from https://stackoverflow.com/questions/49852012/python-pyqt5-set-text-to-qtextbrowser-with-different-colors
        self.textBrowser.append('''<span style="color: {};">{}</span>'''.format(color, row))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
