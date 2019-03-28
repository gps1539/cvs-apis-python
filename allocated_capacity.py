#!/usr/bin/env python3
import requests
import json
import argparse
import sys
import os
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

parser = argparse.ArgumentParser()
parser.add_argument("-c","--config", nargs='+', help="path to .conf config files")
args = parser.parse_args()

if args.config:
	if len(args.config)!=1:
		print('a config file is required')
		sys.exit(1)
else:
	print('a config file is required')
	sys.exit(1)

standard={}
premium={}
extreme={}
volumes={}

# read config files for keys and api endpoint
def config(file):
	for line in file:
		if 'apikey' in line:
			apikey=(line.split("=")[1].rstrip('\n'))
		if 'secretkey' in line:
			secretkey=(line.split("=")[1].rstrip('\n'))
		if 'url' in line:
			url=str(line.split("=")[1].rstrip('\n'))
	# create header
	headers = {}
	headers['api-key'] = apikey
	headers['secret-key'] = secretkey
	headers['content-type'] = 'application/json'
	command = 'FileSystems'
	url = url+command
	# get filesystems
	req = requests.get(url, headers = headers)
	if req.status_code != 200:
		print("Please check the config file")
		print(req)
		sys.exit(1)
	vols=(len(req.json()))
	for vol in range(0, vols):
		mountpoint=((req.json()[vol])['creationToken'])
		allocated=(((req.json()[vol])['quotaInBytes'])/1000000000000)
		service_level=((req.json()[vol])['serviceLevel'])
		if ((req.json()[vol])['serviceLevel']) == 'extreme':
			extreme.update({mountpoint:allocated})
		if ((req.json()[vol])['serviceLevel']) == 'standard':
			premium.update({mountpoint:allocated})
			service_level='premium'
		if ((req.json()[vol])['serviceLevel']) == 'basic':
			standard.update({mountpoint:allocated})
			service_level='standard'
		print(mountpoint, allocated, service_level)

path = args.config[0]

for f in os.listdir(path):
	if f.endswith(".conf"):
		print()
		print(f)
#	conf=args.config[0]
		file = open(f, 'r')
		config(file)

total_volumes=(len(standard))+(len(premium))+(len(extreme))

print()
print("Results")
print()
print("Standard Service Level: Volumes : "+(str(len(standard)))+ ", Terabytes allocated: "+(str(round(sum(standard.values()),4))))
print("Premium Service Level:  Volumes : "+(str(len(premium)))+ ", Terabytes allocated: "+(str(round(sum(premium.values()),4))))
print("Extreme Service Level:  Volumes : "+(str(len(extreme)))+ ", Terabytes allocated: "+(str(round(sum(extreme.values()),4))))
total_volumes=(len(standard))+(len(premium))+(len(extreme))
print("All Service Levels:     Volumes : "+(str(total_volumes))+", Terabytes allocated: "+(str(round(sum(standard.values()),4)+round(sum(premium.values()),4)+round(sum(extreme.values()),4))))
