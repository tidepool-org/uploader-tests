#!/usr/bin/env python3
# == BSD2 LICENSE ==
# Copyright (c) 2025, Tidepool Project
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the associated License, which is identical to the BSD 2-Clause
# License as published by the Open Source Initiative at opensource.org.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the License for more details.
#
# You should have received a copy of the License along with this program; if
# not, you can obtain one from Tidepool Project at tidepool.org.
# == BSD2 LICENSE ==

import logging
import string
from datetime import datetime
from functools import reduce

from facedancer import main
from facedancer.devices.ftdi import FTDIDevice

device = FTDIDevice()

async def setup():
    logging.info("Waiting for the host to connect.")
    await device.wait_for_host()
    logging.info("Host connected!")

def checksum(packet):
    chk = reduce(lambda s1, e: s1 + ord(e), packet, 0)
    return format(chk, '04X')

def received(endpoint, data):
    logging.info(f"Received: {repr(data)}")
    decoded = data.decode('ascii', errors='ignore')
    packet = ''.join(c for c in decoded if c in string.printable and c not in string.whitespace)
    logging.info(f"Parsed: {repr(packet)}")

    match packet:
        case "DMF":
            # Current date/time
            now = datetime.now()
            formatted = f'F "{now.strftime("%a").upper()}",' \
                        f'"{now.strftime("%m/%d/%y")}",' \
                        f'"{now.strftime("%H:%M:%S"): <11}"'
            tosend = f'{formatted} {checksum(formatted)}\r\n'
            logging.info(f'Sending: {repr(tosend)}')
            device.transmit(tosend)

            # TODO: send wrong date/time, and handle setting date/time
        case "DMP":
            # All records
            header = 'P 002,"ABCDE1234","MG/DL "' # Header shows number of records, serial number, and units
            device.transmit(f'{header} {checksum(header)}\r\n' \
                'P "FRI","07/14/17","10:31:12   ","  098 ","N","00", 00 09AE\r\n' \
                'P "FRI","07/14/17","10:10:53   ","  649 ","N","00", 00 09B2\r\n') # records show date, time, glucose value, status, flags and checksum
            logging.info("Sent records")
        case _:
            print('Unexpected packet')

device.handle_data_received = received
main(device, setup())
