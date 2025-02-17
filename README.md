# Software Defined Radio (SDR) Code


To add **HackRF udev rules**:


Add the following rules to /etc/udev/rules.d in a file such as **52-hackrf.rules**

```bash
ATTR{idVendor}=="1d50", ATTR{idProduct}=="604b", SYMLINK+="hackrf-jawbreaker-%k", MODE="660", GROUP="plugdev"
ATTR{idVendor}=="1d50", ATTR{idProduct}=="6089", SYMLINK+="hackrf-one-%k", MODE="660", GROUP="plugdev"
ATTR{idVendor}=="1fc9", ATTR{idProduct}=="000c", SYMLINK+="hackrf-dfu-%k", MODE="660", GROUP="plugdev"
```
The content of the file instructs udev to look out for devices with Vendor ID and Product ID matching HackRF devices. It then sets the UNIX permissions to 660 and the group to plugdev and creates a symlink in /dev to the device.
to reload rules

After creating the rules file you can either reboot or run the command:

```bash
sudo usermod -G plugdev -a $USER
udevadm control --reload-rules
```
as root to instruct udev to reload all rule files. After replugging your HackRF board, you should be able to access the device with all utilities as a normal user. If you still can't access the device, make sure that you are a member of the **plugdev** group.


To install **GNU Radio** on Ubuntu use the following steps:

```bash
sudo apt install gnuradio
sudo apt install libcanberra-gtk-module libcanberra-gtk3-module
```

To install **Osmocom RTL2382U** Driver

```bash
git clone https://github.com/osmocom/rtl-sdr.git
mkdir build
cd build
cmake ../ -DINSTALL_UDEV_RULES=ON -DDETACH_KERNEL_DRIVER=ON
make
sudo make install
sudo ldconfig
```

To install **Osmocom GNU Radio Blocks** from source:

```bash
git clone git://git.osmocom.org/gr-osmosdr
cd gr-osmosdr/

mkdir build
cd build/
cmake ../

make
sudo make install
sudo ldconfig
```

To build API documentation:

```bash
cd build/
cmake ../ -DENABLE_DOXYGEN=1
make -C docs
```

To install the **Osmocom GNU Radio Source** Module:

```bash
sudo apt install gr-osmosdr
```
To install **HackRF**

```bash
sudo apt install hackrf
```
Building **HackRF tools from source**

```bash
git clone https://github.com/mossmann/hackrf.git
cd hackrf/host
mkdir build
cd build
cmake ..
make
sudo make install
sudo ldconfig
```

To install **GQRX-SDR**

```bash
sudo add-apt-repository -y ppa:myriadrf/drivers
sudo add-apt-repository -y ppa:myriadrf/gnuradio
sudo add-apt-repository -y ppa:gqrx/gqrx-sdr
sudo apt-get update
sudo apt install gqrx-sdr
```


To install **GQRX-SDR** from source

```bash
sudo apt install qt5-default
sudo apt install libqt5svg5

git clone https://github.com/csete/gqrx.git gqrx
cd gqrx
mkdir build
cd build
cmake ..
make
sudo make install
sudo ldconfig

gqrx --version
```
To install **RFCAT Client** from source

```bash
sudo apt install sdcc
sudo apt install python-usb
sudo apt install libusb-1.0-0
sudo apt install ipython

sudo apt install python-pip
pip install future
pip install pyside2

python -m pip install future
python -m pip install pyside2

git clone https://github.com/atlas0fd00m/rfcat.git

cd rfcat
sudo python setup.py install

cd firmware
make clean installRfCatYS1CCBootloader


sudo cp etc/udev/rules.d/20-rfcat.rules /etc/udev/rules.d
sudo usermod -G dialout -a $USER
sudo udevadm control --reload-rules


```

To install **Audacity**

```bash
sudo apt install audacity
```


To install **inspectrum**

```bash
sudo apt install inspectrum
```
