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
parser.add_argument("-n","--name", nargs='+', help="name")
parser.add_argument("-m","--mountpoint", nargs='+', help="mountpoint")
parser.add_argument("-r","--region", nargs='+', help="region")
parser.add_argument("-a","--allocation", type=int, help="allocated_size_in_GB (100 to 100000") 
parser.add_argument("-l","--service_level", nargs='+', help="service level <standard|premium|extreme>")
parser.add_argument("-e","--export", nargs='+', help="provide valid CIDR for export, defaults to 0.0.0.0/0")
parser.add_argument("-w","--rw_ro", nargs='+', help="rw or ro")
parser.add_argument("-p","--protocol", nargs='+', help="<nfs3|smb|nfs3smb>")
parser.add_argument("-s","--snapshot", nargs='+', help="snapshotId (optional)")
parser.add_argument("-t","--tag", nargs='+', help="tag (optional)")
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
		print('a volume mountpoint is required')
		sys.exit(1)
else:
	print('a volume mountpoint is required')
	sys.exit(1)

if args.allocation:
	if (args.allocation)<100 or (args.allocation)>100000:
		print('Allocation size must be between 100 to 100000 GB')
		sys.exit(1)
	else:
		args.allocation = args.allocation * 1000000000

# check service level and word swap to match UI
if args.service_level:
	if (args.service_level)[0] != 'standard' and (args.service_level)[0] != 'premium' and (args.service_level)[0] != 'extreme':
		print('Service level must be standard, premium or extreme')
		sys.exit(1)
	else:
		if (args.service_level)[0] == 'standard':
			(args.service_level)[0] = 'basic'
		elif (args.service_level)[0] == 'premium':
			(args.service_level)[0] = 'standard'

# set export to default
export = '0.0.0.0/0'
if args.export:
	export = args.export[0]

if args.rw_ro:
	if (args.rw_ro)[0] != 'ro' and (args.rw_ro)[0] != 'rw':
		print('ro (read only) or rw (read write) must be provided')
		sys.exit(1)
	elif (args.rw_ro)[0] == 'ro':
		ro = True
		rw = False
	else:
		ro = False
		rw = True
else:
	print('ro (read only) or rw (read write) must be provided')
	sys.exit(1)

if args.region:
	if (args.region)[0] != 'us-east-1' and (args.region)[0] != 'us-west-1' and (args.region)[0] != 'us-west-2' and (args.region)[0] != 'eu-central-1' and (args.region)[0] != 'eu-west1' and (args.region)[0] != 'eu-west-2' and (args.region)[0] != 'ap-northeast-1' and (args.region)[0] != 'ap-southeast-2':
		print('Please select an available region')
		sys.exit(1)	
else:
	print('Please select an available region')
	sys.exit(1)

if args.protocol:
	if (args.protocol)[0] != 'nfs3' and (args.protocol)[0] !='smb' and (args.protocol)[0] != 'nfs3smb' :
		print('Please choose nfs3, smb or nfs3smb (dual)')
		sys.exit(1)
	elif (args.protocol)[0] == 'nfs3':
		nfs3 = True
		cifs = False
		rule = {"rules": [{"ruleIndex": 1,"allowedClients": export,"unixReadOnly": ro,"unixReadWrite": rw,"cifs": cifs,"nfsv3": nfs3,"nfsv4": False }]}
	elif (args.protocol)[0] == 'smb':
		nfs3 = False 
		cifs = True
		rule = {"rules": []}
	else:
		nfs3 = True 
		cifs = True
		rule = {"rules": [{"ruleIndex": 1,"allowedClients": export,"unixReadOnly": ro,"unixReadWrite": rw,"cifs": cifs,"nfsv3": nfs3,"nfsv4": False }]}

else:
	print('Please choose nfs3, smb or nfs3smb (dual)')
	sys.exit(1)

snapshot = ''
if args.snapshot:
	snapshot = args.snapshot[0]

tag = ''
if args.tag:
	tag = args.tag[0]

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

req = requests.get(url, headers = head)
vols=(len(req.json()))

# create volume
def create(fsid, url, data, head):
	data_json = json.dumps(data)
	req = requests.post(url, headers = head, data = data_json)
	details = json.dumps(req.json(), indent=4)
	print('Created volume '+args.mountpoint[0])
	print(highlight(details, JsonLexer(), TerminalFormatter()))

data = {
	"name": args.name[0],
	"creationToken": args.mountpoint[0],
	"region": args.region[0],
	"serviceLevel": args.service_level[0],
	"quotaInBytes": args.allocation,
	"exportPolicy": rule,
	"snapshotId": snapshot,
	"labels": [tag]
		}

create(fsid, url, data, head)
