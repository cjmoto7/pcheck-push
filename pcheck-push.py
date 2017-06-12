#!/usr/bin/env python

import os
import sys
import requests
import socket

try:
    import simplejson as json
except ImportError:
    try:
        import json
    except ImportError:
        sys.exit("Please install the simplejson library or upgrade to Python 2.6+")

with open('sp-data.json') as json_data:
    settings = json.load(json_data)


def send_push_notif(message, args):
    if len(message) > 512:
        return None
    payload = {
            "token": settings['config']['appkey'],
            "user" : settings['config']['userkey'],
            "message": message,
    }
    for key,value in args.iteritems():
        payload[key] = value
    r = requests.post("https://api.pushover.net/1/messages.json", data=payload )
    if not r.status_code == requests.codes.ok:
        raise r.raise_for_status()


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
for index, device in enumerate(settings['device']):
    try:
        s.connect((device['hostname'], device['port']))
        if device['isConnected'] == 'no':
            settings['device'][index]['isConnected'] = 'yes'
            send_push_notif(device['name'] + ' is now online', device['argsOn'])
    except socket.error:
        if device['isConnected'] == 'yes':
            settings['device'][index]['isConnected'] = 'no'
            send_push_notif(device['name'] + ' is now offline', device['argsOff'])
s.close()

with open('sp-data.json', 'w') as outfile:
    json.dump(settings, outfile, sort_keys=True, indent=4, separators=(',', ': '))
