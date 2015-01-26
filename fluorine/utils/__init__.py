from __future__ import unicode_literals
__author__ = 'luissaguas'

import hashlib, os
#import fluorine
from . import file
import copy

def start_hash(rootDir):
	hash = {}
	for dirName, subdirList, fileList in os.walk(rootDir):
		print('Found directory: %s' % dirName)
		for fname in fileList:
			print('\t%s' % fname)
			file = os.path.join(dirName, fname)
			hash[file] = make_hash(file)
	return hash

def make_hash(path):
	multi = False
	m = hashlib.md5()
	with open(path, "r") as f:
		for line in f:
			if line.startswith("//"):
				continue
			elif line.startswith("/*"):
				multi = True
				continue
			elif line.endswith("*/"):
				multi = False
				continue
			elif not multi:
				m.update(line)
		return m.hexdigest()

def is_open_port(ip="127.0.0.1", port=3000):
	import socket;
	is_open = False
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	result = sock.connect_ex((ip,port))
	if result == 0:
		print "Port is open"
		is_open = True
	sock.close()
	return is_open


def addjs_file(path):
	p = file.get_fluorine_server_conf()
	copy_assets = {}
	load = p.get("load", [])
	for obj in load:
		assets = copy.deepcopy(obj.get("assets", None))
		if assets:
			copy_assets.update(assets)
			break
	load.append({"path":path, "assets":copy_assets})
	print "asssets {}".format(p)
	return p

