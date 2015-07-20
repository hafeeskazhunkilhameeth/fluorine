# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'

import hashlib, os
import copy, frappe


react = {"Reactive Web": "web", "Reactive App": "app", "Both": "both"}
assets_public_path = "/assets/fluorine/js/react"

def check_dev_mode():
	import file
	#config = {}
	#path_module = os.path.dirname(fluorine.__file__)
	#path_reactivity = os.path.realpath(os.path.join(path_module, "..", "..", ".."))#utils.file.get_path_reactivity()
	path_reactivity = file.get_path_reactivity()
	#common_site_config = os.path.join(path_reactivity, "reactivity", "common_site_config.json")
	common_site_config = os.path.join(path_reactivity, "common_site_config.json")
	print "path_reactivity {}".format(common_site_config)
	if os.path.exists(common_site_config):
		dev = file.get_fluorine_conf("developer_mode")
		if dev == 1:
			return True

	return False
		#config.update(frappe.get_file_json(common_site_config))
	#return frappe._dict(config)

def set_config(fobj):
	import file
	fobj = fobj or {}
	path_reactivity = file.get_path_reactivity()
	common_site_config = os.path.join(path_reactivity, "common_site_config.json")
	if os.path.exists(common_site_config):
		config = frappe.get_file_json(common_site_config)
		config.update(fobj)
	else:
		config = fobj

	file.save_js_file(common_site_config, config)

	return

def get_js_paths():
	meteor_path = "/assets/fluorine/js/meteor.devel.js" if check_dev_mode() else "/assets/js/meteor.js"
	paths = ["/assets/fluorine/js/meteor_config.js", "/assets/fluorine/js/before_fluorine_helper.js", meteor_path, "/assets/fluorine/js/after_fluorine_helper.js"]
	return paths

def start_hash(rootDir):
	hash = {}
	ignore_file = [".DS_Store"]
	for dirName, subdirList, fileList in os.walk(rootDir):
		print('Found directory: %s' % dirName)
		for fname in fileList:
			print('\t%s' % fname)
			if fname in ignore_file:
				continue
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
	import socket
	is_open = False
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	result = sock.connect_ex((ip,port))
	if result == 0:
		print "Port is open"
		is_open = True
	sock.close()
	return is_open


def addjs_file(path):
	import file
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

def meteor_autoupdate_version():
	return "128"

def meteor_autoupdate_version_freshable():
	return "128"

def meteor_url_path_prefix(whatfor):
	return os.path.join("assets", "fluorine",  whatfor, "webbrowser")

def jquery_include():
	return True

def get_Frappe_Version(version=None):
	version = version or frappe.__version__
	import semantic_version as sv
	return sv.Version(version)

def build_meteor_context(context, devmode, whatfor):
	from file import get_path_reactivity
	import random

	path_reactivity = get_path_reactivity()

	config_path = os.path.join(path_reactivity, "common_site_config.json")
	conf = frappe.get_file_json(config_path)
	if not devmode:
		add = 0
		meteor_dns = conf.get("meteor_dns") or {}
		all_dns = meteor_dns.get(whatfor)
		n = random.randint(0, len(all_dns) - 1)
		meteor = all_dns[n]
	else:
		meteor = conf.get("meteor_dev") or {}
		add = 80 if whatfor == "meteor_app" else 0

	context.mport = meteor.get("port", 3000) + add

	base_url = frappe.local.request.url
	burl = base_url.rsplit(":",1)
	if burl > 1:
		#port = burl[1]
		host_url = burl[0]
	else:
		host_url = base_url
		#port = ""

	host = meteor.get("host", host_url)
	meteor_host =  host + ":" + str(context.mport)
	context.meteor_root_url = host
	context.meteor_root_url_port = meteor_host
	context.meteor_url_path_prefix = meteor_url_path_prefix(whatfor)
	context.meteor_ddp_default_connection_url = meteor_host


if check_dev_mode():
	print "Enter Reactivity State !!!"
	import spacebars_template
	import reactivity
