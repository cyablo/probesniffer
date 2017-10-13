```                                                         
 _____            _                   _  ___  ___
|  _  | ___  ___ | |_  ___  ___  ___ |_||  _||  _| ___  ___ 
|   __||  _|| . || . || -_||_ -||   || ||  _||  _|| -_||  _|
|__|   |_|  |___||___||___||___||_|_||_||_|  |_|  |___||_|
```
### This is still in developement and considered as BETA code. ###

Multi-adapter, multi-threaded wifi probe request sniffer. Needs at least 1 wifi adapter supporting monitor-mode.
High-performance because I'm using RAW-sockets and custom packet parser instead of scapy (other scripts use that for simplicity, but scapy has INSANELY high CPU overhead for e.g. a RasPi 1 to handle).

### Install on fresh Raspbian Stretch lite: ###

```
sudo ap-get update && sudo apt-get install git python-pip
sudo pip install python-wifi
```

CPU usage is about 30-40% average with 2 WiFi-Adapters on RasPi 1 set to Turbo mode (1 GHz) running Raspian Stretch lite.

BTW: Try looking for Atheros AR9271 Chipset devices. There are pretty good and pretty cheap 2,4 GHz Adapters on Aliexpress but sadly the Firmware can't initialize more than 2 Devices at the same time. Ralink RT3572/RT3070 Chipset seems to be a good alternative because AR9271 is getting pretty rare.
