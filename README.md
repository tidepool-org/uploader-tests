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


Linux: `mount -t vfat -o loop emulator/onetouch/disk.img /mnt`
MacOS: `hdiutil attach -mountpoint /mnt disk.img`

and then run: `python emulator/onetouch/oneTouchVerio.py`
