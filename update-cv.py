#!/usr/bin/env python3
import requests
import urllib.request
import json
import sys
import re
import argparse
import datetime
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

parser = argparse.ArgumentParser()
parser.add_argument("-c","--config", nargs='+', help="config file")
parser.add_argument("-m","--mountpoint", nargs='+', help="mountpoint")
parser.add_argument("-a","--allocation", type=int, help="allocated_size_in_GB (100 to 100000") 
parser.add_argument("-l","--service_level", nargs='+', help="service level <standard|premium|extreme>")
args = parser.parse_args()

if args.config:
	if len(args.config)!=1:
		print('a config file is required')
		sys.exit(1)
else:
	print('a config file is required')
	sys.exit(1)

if args.mountpoint:
	if len(args.mountpoint)!=1:
		print('a volume mountpoint is require')
		sys.exit(1)
else:
	print('a volume mountpoint is require')
	sys.exit(1)

if args.allocation:
	if (args.allocation)<100 or (args.allocation)>100000:
		print('Allocation size must be between 100 to 100000 GB')
		sys.exit(1)
	else:
		args.allocation = args.allocation * 1000000000

# word swap service levels to match UI
if args.service_level:
	if (args.service_level)[0] != 'standard' and (args.service_level)[0] != 'premium' and (args.service_level)[0] != 'extreme':
		print('Service level must be standard, premium or extreme')
		sys.exit(1)
	else:
		if (args.service_level)[0] == 'standard':
			(args.service_level)[0] = 'basic'
		elif (args.service_level)[0] == 'premium':
			(args.service_level)[0] = 'standard'
else:
		print('Service level must be standard, premium or extreme')
		sys.exit(1)

conf=args.config[0]
file = open(conf, 'r')
fsid = False

# read config files for keys and api endpoint
for line in file:
	if 'apikey' in line:
		apikey=(line.split("=")[1].rstrip('\n'))
	if 'secretkey' in line:
		secretkey=(line.split("=")[1].rstrip('\n'))
	if 'url' in line:
		url=str(line.split("=")[1].rstrip('\n'))

# create header
head = {}
head['api-key'] = apikey
head['secret-key'] = secretkey
head['content-type'] = 'application/json'

command = 'FileSystems'
url = url+command

# get filesystems
req = requests.get(url, headers = head)
vols=(len(req.json()))

# search for filesystemId
for vol in range(0, vols):
	if ((req.json()[vol])['creationToken']) == args.mountpoint[0]:
		fsid = ((req.json()[vol])['fileSystemId'])
		region = ((req.json()[vol])['region'])
if not fsid :
	print('Mountpoint '+args.mountpoint[0] + ' does not exist')
	sys.exit(1)

time=(datetime.datetime.utcnow())

# update volume 
def update(fsid, url, data, head):
	url = url+'/'+fsid
	data_json = json.dumps(data)
	req = requests.put(url, headers = head, data = data_json)
	details = json.dumps(req.json(), indent=4)
	print('Updated volume '+args.mountpoint[0])
	print(highlight(details, JsonLexer(), TerminalFormatter()))

data = {
	"creationToken": args.mountpoint[0],
	"region": region,
	"serviceLevel": args.service_level[0],
	"quotaInBytes": args.allocation
		}

update(fsid, url, data, head)


