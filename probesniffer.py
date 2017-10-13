#!/usr/bin/env python
# -.- coding: utf-8 -.-

from __future__ import print_function
import subprocess
import os
import sys
from pythonwifi.iwlibs import Wireless, getNICnames
import threading
import socket
import time
import urllib2
import struct
import Queue

# Variables
wifiif = ["wlan0", "wlan1"]
channels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
hop_delay = 0.25
collect_for_sec = 10

# Globals
chan = {}
current_chan = {}
startchanindex = -1
stack = Queue.Queue()

def checkroot():
 if os.getuid() == 0:
  return True
 else:
  return False

def checktool(name):
 try:
  devnull = open(os.devnull)
  subprocess.Popen([name], stdout=devnull, stderr=devnull).communicate()
 except OSError as e:
  if e.errno == os.errno.ENOENT:
   return False
 return True

def checkinterface(wif):
 found = False
 for iface in getNICnames():
  if iface == wif:
   found = True
 return found

def checkmode(wif):
 return Wireless(wif).getMode()

def switchtomonitor(wif):
 os.system("ifconfig " + wif + " down")
 Wireless(wif).setMode("Monitor")
 os.system("ifconfig " + wif + " up")

def startchhopper():
 for wif in wifiif:
  hopper = threading.Thread(target=chhopper, args=(wif,))
  hopper.daemon = True
  hopper.start()
  print("- [x] channel hopper started for " + wif + " with " + str(hop_delay) + "s delay")

def chhopper(wif):
 global startchanindex
 #global current_chan
 startchanindex += 1
 local_startchanindex = startchanindex
 while 1:
  for chanindex in range(local_startchanindex, len(channels), len(wifiif)):
   current_chan[wif] = str(channels[chanindex])
   #print(wif + " : " + current_chan[wif])
   #print("- change " + wif + " channel to " + str(channels[chanindex]))
   os.system("iwconfig " + wif + " channel " + str(channels[chanindex]) + " > /dev/null 2>&1")
   time.sleep(hop_delay)

def startpkthandler():
 for wif in wifiif:
  pkthandler = threading.Thread(target=pakethandler, args=(wif,))
  pkthandler.daemon = True
  pkthandler.start()
  print("- [x] sniffer started for " + wif)

def pakethandler(wif):
 rawSocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))
 rawSocket.bind((wif, 0x0003))
 while True:
  paketpos = 0
  pkt = rawSocket.recvfrom(2048)
  radiotap_lenght = pkt[0][0:3]
  radiotap_lenght = struct.unpack("!1B1B1B", radiotap_lenght)
  radiotap_lenght = int(radiotap_lenght[2])
  paketpos = radiotap_lenght
  wifi_header = pkt[0][paketpos:(paketpos + 24)]
  paketpos = paketpos + 24
  if len(wifi_header) == 24:
   wifi_header = struct.unpack("!2s2s6s6s6s2s", wifi_header)
   frame_control = wifi_header[0]
   frame_control = struct.unpack("!1B1B", frame_control)
   subtype = frame_control[0]
   if subtype == 64:
    mac = wifi_header[3].encode('hex')
    #print(wifi_header[2].encode('hex'))
    #print(wifi_header[4].encode('hex'))
    ssid_lenght = pkt[0][paketpos:(paketpos + 2)]
    paketpos = paketpos + 2
    ssid_lenght = struct.unpack("!1B1B", ssid_lenght)
    ssid_lenght = ssid_lenght[1]
    if ssid_lenght > 0:
     ssid = pkt[0][paketpos:(paketpos + int(ssid_lenght))]
     paketpos = paketpos + int(ssid_lenght)
    else:
     ssid = "NONE"
    stackprobe(wif,mac,ssid)

def stackprobe(wif,mac,ssid):
 request = urllib2.Request("https://macvendors.co/api/vendorname/" + mac, headers={'User-Agent' : 'API Browser'})
 response = urllib2.urlopen(request)
 vendor = response.read()
 vendor = vendor.decode("utf-8")
 ssid = ssid.decode("utf-8").encode("utf-8")
 print("- [x] " + wif + ": chan " + current_chan[wif] + " -> " + mac + " (" + vendor + ") -> " + ssid)
 item = (mac + ";" + ssid)
 if not item in stack.queue:
  stack.put(mac + ";" + ssid)

def main():
 print(" _____            _                   _  ___  ___           ")
 print("|  _  | ___  ___ | |_  ___  ___  ___ |_||  _||  _| ___  ___ ")
 print("|   __||  _|| . || . || -_||_ -||   || ||  _||  _|| -_||  _|")
 print("|__|   |_|  |___||___||___||___||_|_||_||_|  |_|  |___||_|  ")
 print("(c) Daniel Wandrei - cyablo@cyablo.de")
 print("")
 print("--- running system checks:")
 if checkroot():
  print("- [x] running as root, badass!")
 else:
  print("- [ ] not running as root, exiting...")
  exit(1)
 #if checktool("tcpdump"):
 # print("- [x] tcpdump found")
 #else:
 # print("- [ ] tcpdump not found, exiting...")
 # exit(1)
 for wif in wifiif:
  if checkinterface(wif):
   print("- [x] '" + wif + "' found")
  else:
   print("- [ ] '" + wif + "' not found, exiting...")
   exit(1)
 print("")
 print("--- checking wifi mode:")
 for wif in wifiif:
  if checkmode(wif) == "Managed":
   print("- [x] " + wif + " still in managed mode")
   print('- [ ] switching ' + wif + ' to monitor mode', end='\r')
   switchtomonitor(wif)
   if checkmode(wif) == "Monitor":
    print("- [x] " + wif + " successfully switched to monitor mode")
   else:
    print("- [ ] switching " + wif + " to monitor mode failed")
  elif checkmode(wif) == "Monitor":
   print("- [x] " + wif + " already in monitor mode")
 print("")
 print("--- starting channel hopping")
 startchhopper()
 print("")
 print("--- starting sniffer")
 startpkthandler()
 while 1:
  print("")
  print("--- (re)starting timer: " + str(collect_for_sec) + "s")
  end_timer = time.time() + collect_for_sec
  while time.time() < end_timer:
   time.sleep(0.1)
  global stack
  while not stack.empty():
   entry = stack.get()
   print(entry[0:12])
   print(entry[13:])
   stack.task_done()

if __name__ == "__main__":
 main()
