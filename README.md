This repo is meant for end-to-end testing of Tidepool Uploader.

You'll need a Facedancer board like the [Cynthion](https://greatscottgadgets.com/cynthion/) or [GreatFET One](https://greatscottgadgets.com/greatfet/one/) from Great Scott Gadgets.

### Setup

```
python -m venv venv
source venv/bin/activate
pip install cynthion
pip install facedancer
```

### Usage

Connect the CONTROL port on the Cynthion to your computer, the TARGET C port to the target device (which can also be your own computer, i.e., where Tidepool Uploader is running). Then run the script, e.g. to emulate a OneTouch Verio Flex meter to upload, run:

`python emulator/onetouch/oneTouchVerio.py disk.dmg`

If you don't have a disk.dmg, you can create one using the following command on MacOS:

```
hdiutil create -o disk.dmg -size 100m -fs "MS-DOS FAT16" -volname "LIFESCAN"
dd if=/dev/zero of=zeros.bin bs=1 count=10
dd if=zeros.bin of=disk.dmg bs=1 seek=1024 conv=notrunc
```
