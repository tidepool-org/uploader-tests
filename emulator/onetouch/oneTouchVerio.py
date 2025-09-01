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
import struct
import os
import sys

from facedancer import main
from facedancer.devices.umass import USBMassStorageDevice
from facedancer.devices.umass import RawDiskImage

from crc import calc_crc_a

start = 0x02
end = 0x03

class VerioImage(RawDiskImage):
    def buildFrame(self, appData):
        length = len(appData) + 6
        data = struct.pack('<BH4sB', start, length, appData, end)
        crc_bytes = struct.pack('<H', calc_crc_a(data))
        final = data + crc_bytes
        print("Frame:", final.hex())
        return final


    def put_data(self, address, data):
        if self.verbose > 1:
            blocks = int(len(data) / self.block_size)
            print("--> writing {} blocks at lba {}".format(blocks, address))

        match(data[4]):
            case 0xE6:
                # Query
                if(data[6] == 0x00):
                    print("Serial number request")
                    data = bytes([ 0x02, 0x1A,0x00, 0x04, 0x06, 0x5A, 0x00, 0x41, 0x00, 0x48, 0x00, 0x4C, 0x00, 0x47, 0x00, 0x48, 0x00, 0x36, 0x00, 0x43, 0x00, 0x00, 0x00, 0x03, 0x7C, 0x69])
                if(data[6] == 0x01):
                    print("Device model request")
                    data = bytes([0x02, 0x1E, 0x00, 0x04, 0x06, 0x56, 0x00, 0x65, 0x00, 0x72, 0x00, 0x69, 0x00, 0x6F, 0x00, 0x20, 0x00, 0x46, 0x00, 0x6C, 0x00, 0x65, 0x00, 0x78, 0x00, 0x00, 0x00, 0x03, 0xE2, 0xEE])
            case 0x20:
                if(data[5] == 0x02):
                    print("RTC request")
                    data = bytes([0x02, 0x0C, 0x00, 0x04, 0x06, 0x73, 0x06, 0x84, 0x2E, 0x03, 0x59, 0xE0])
                if(data[5] == 0x01):
                    print("RTC set request")
                    data = bytes([0x02, 0x08, 0x00, 0x04, 0x06, 0x03, 0x78, 0xC1])
            case 0x27:
                if(data[5] == 0x00):
                    print("Record count request")
                    recordCount = 1
                    data = self.buildFrame(struct.pack('<BBH', 0x04, 0x06, recordCount))
            case 0x31:
                print("Record data request")
                recNumber = struct.unpack_from('<H', data, 6)[0]
                print("Record number:", recNumber)
                data = bytes([0x02, 0x18, 0x00, 0x04, 0x06, 0x0E, 0x00, 0x00, 0x16, 0x00, 0x29, 0xE3, 0xA7, 0x28, 0x32, 0x00, 0x00, 0x00, 0x93, 0x0B, 0x00, 0x03, 0x61, 0x17])
            case _:
                pass

        if address == 2 or address == 212:
            # Windows tries to write to the device, which will checkDevice fail as it expects
            # the device to be completely empty at start
            print("don't write")
            data = bytes([0x00])

        padded_data = data + b'\x00' * (self.block_size - len(data))

        super().put_data(address, padded_data)


# usage instructions
if len(sys.argv)==1:
    print("Usage: onetouchVerio.py disk.img")
    sys.exit(1)

# get disk image filename and clear arguments
filename = sys.argv[1]
sys.argv = [sys.argv[0]]

# open our disk image
disk_image = VerioImage(filename, 512, verbose=3)

# create the device
device = USBMassStorageDevice(disk_image,
            vendor_id=0x2766,
            product_id=0x0004,
            manufacturer_string="LifeScan",
            product_string="Verio Flex",
            serial_number_string="1234567890")


async def hello():
    logging.info("Waiting for the host to connect.")
    await device.wait_for_host()
    logging.info("Host connected!")

main(device, hello())


# Creating a disk image for testing:
#
#    dd if=/dev/zero of=disk.img bs=1M count=100
#    mkfs.fat -F 16 -n LIFESCAN disk.img
#    mount -t vfat -o loop disk.img /mnt
#
# On MacOS:
#
#    hdiutil create -o disk.dmg -size 100m -fs "MS-DOS FAT16" -volname "LIFESCAN"
#    dd if=/dev/zero of=zeros.bin bs=1 count=10
#    dd if=zeros.bin of=disk.dmg bs=1 seek=1024 conv=notrunc
