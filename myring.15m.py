#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# <bitbar.title>MyRing</bitbar.title>
# <bitbar.version>v1.0</bitbar.version>
# <bitbar.author>pvdabeel@mac.com</bitbar.author>
# <bitbar.author.github>pvdabeel</bitbar.author.github>
# <bitbar.desc>Control your Ring Doorbell from the Mac OS X menubar</bitbar.desc>
# <bitbar.dependencies>python</bitbar.dependencies>
#
# Credits: Python Ring Door Bell library
#
# Licence: GPL v3

# Installation instructions: 
# -------------------------- 
# Execute in terminal.app before running : 
#    sudo easy_install keyring ring_doorbell
#
# Ensure you have bitbar installed https://github.com/matryer/bitbar/releases/latest
# Ensure your bitbar plugins directory does not have a space in the path (known bitbar bug)
# Copy this file to your bitbar plugins folder and chmod +x the file from your terminal in that folder
# Run bitbar


try:   # Python 3 dependencies
    from urllib.parse import urlencode
    from urllib.request import Request, urlopen, build_opener
    from urllib.request import ProxyHandler, HTTPBasicAuthHandler, HTTPHandler, HTTPError, URLError
except: # Python 2 dependencies
    from urllib import urlencode
    from urllib2 import Request, urlopen, build_opener
    from urllib2 import ProxyHandler, HTTPBasicAuthHandler, HTTPHandler, HTTPError, URLError

import ast
import json
import sys
import datetime
import calendar
import base64
import math
import keyring      # Access token is stored in OS X keychain
import getpass      # Getting password without showing chars in terminal.app
import time
import os
import subprocess
import ring_doorbell

from datetime import date
from ring_doorbell import Ring

# Nice ANSI colors
CEND    = '\33[0m'
CRED    = '\33[31m'
CGREEN  = '\33[32m'
CYELLOW = '\33[33m'
CBLUE   = '\33[34m'

# Support for OS X Dark Mode
DARK_MODE=os.getenv('BitBarDarkMode',0)


# Logo for both dark mode and regular mode
def app_print_logo():
    if bool(DARK_MODE):
        print ('|image=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')
    else:
        print ('|image=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')
    print('---')


# The init function: Called to store your username and access_code in OS X Keychain on first launch

def init():
    # Here we do the setup
    # Store access_token in OS X keychain on first run
    print ('Enter your ring.com username:')
    init_username = raw_input()
    print ('Enter your ring.com password:')
    init_password = getpass.getpass()

    try:
        c = Ring(init_username,init_password)
        if not c.is_connected:
           print('Error logging in. Try again later')
           time.sleep(0.5)
           return
    except Exception as e:
        print ('Error: An error was returned. Try again later.')
        print e
        return
    keyring.set_password("myring-bitbar","username",init_username)
    keyring.set_password("myring-bitbar","password",init_password)


# The main function

def main(argv):

    # CASE 1: init was called 
    if 'init' in argv:
       init()
       return
  

    # CASE 2: init was not called, keyring not initialized
    if DARK_MODE:
        color = '#FFDEDEDE'
        info_color = '#808080'
    else:
        color = 'black' 
        info_color = '#808080'

    USERNAME = keyring.get_password("myring-bitbar","username")
    PASSWORD = keyring.get_password("myring-bitbar","password")
    
    if not USERNAME:   
       # restart in terminal calling init 
       app_print_logo()
       print ('Login to Ring.com | refresh=true terminal=true bash="\'%s\'" param1="%s" color=%s' % (sys.argv[0], 'init', color))
       return


    # CASE 3: init was not called, keyring initialized, no connection 
    try:
       # create connection to ring account
       c = Ring(USERNAME,PASSWORD)
       if not c.is_connected :
          app_print_logo()
          print ('Login to Ring.com | refresh=true terminal=true bash="\'%s\'" param1="%s" color=%s' % (sys.argv[0], 'init', color))
          return
    except: 
       app_print_logo()
       print ('Login to tesla.com | refresh=true terminal=true bash="\'%s\'" param1="%s" color=%s' % (sys.argv[0], 'init', color))
       return


    # CASE 4: all ok, specific command for a specific device received
    if len(sys.argv) > 1:
       # not implemented yet (examples: turn on ring floodlights, sound chimes, ...)
       return


    # CASE 5: all ok, all other cases
    app_print_logo()
    prefix = ''
    devices = c.doorbells
 
    if len(devices) > 1:
        # Create a submenu for every device
        prefix = '--'

    # loop through devices, print menu with relevant info       
    for i, device in enumerate(devices):
        if prefix:
           print device.name

        # get all device data
        device.update() 

        # get the data for the vehicle       
        ring_name = device.name
        ring_addr = device.address
        ring_wifi = device.wifi_name
        ring_wfst = device.wifi_signal_strength

        events = device.history(limit=5) 
  
        url = device.recording_url(device.last_recording_id)


        # print the data for the vehicle
        print ('%sDoorbell name: \t%s | color=%s' % (prefix, ring_name, color))
        print ('%sDoorbell wifi: \t%s | color=%s' % (prefix, ring_wifi, color))

        print ('%s---' % prefix)

        for event in events:
           # print('%sID:        %s | color=%s' % (prefix, event['id'], color))
           print('%s%s - %s | href=%s color=%s' % (prefix, event['kind'], event['created_at'], device.recording_url(event['id']), color))
           # print('%sAnswered:  %s | color=%s' % (prefix, event['answered'], color))

        # print ('%s---' % prefix)
        # print ('%sView last recording | href="%s" color=%s' % (prefix, url,color))
        # print ('%s' % device.last_recording_id)

def run_script(script):
    return subprocess.Popen([script], stdout=subprocess.PIPE, shell=True).communicate()[0].strip()


if __name__ == '__main__':
    main(sys.argv)
