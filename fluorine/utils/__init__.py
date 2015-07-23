# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'

#import hashlib
import os
#import copy
import frappe


meteor_config = None

#react = {"Reactive Web": "web", "Reactive App": "app", "Both": "both"}
assets_public_path = "/assets/fluorine/js/react"

def get_encoding():
	return "utf-8"


def check_dev_mode():
	from fluorine.utils.file import get_path_reactivity, get_fluorine_conf

	path_reactivity = get_path_reactivity()
	if not meteor_config:
		get_meteor_configuration_file(path_reactivity)

	if meteor_config:
		devmode = meteor_config.get("developer_mode") or 0
		if devmode:
			return True

		return False

	#common_site_config = os.path.join(path_reactivity, "common_site_config.json")
	#print "path_reactivity {}".format(common_site_config)
	#if os.path.exists(common_site_config):
	#	dev = get_fluorine_conf("developer_mode")
	#	if dev == 1:
	#		return True

	return False

"""
def get_js_paths():
	meteor_path = "/assets/fluorine/js/meteor.devel.js" if check_dev_mode() else "/assets/js/meteor.js"
	paths = ["/assets/fluorine/js/meteor_config.js", "/assets/fluorine/js/before_fluorine_helper.js", meteor_path, "/assets/fluorine/js/after_fluorine_helper.js"]
	return paths
"""

"""
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
"""

"""
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
"""

def jquery_include():
	return True

def get_Frappe_Version(version=None):
	version = version or frappe.__version__
	import semantic_version as sv
	return sv.Version(version)


def get_meteor_configuration_file(path_reactivity):

	#path_reactivity = get_path_reactivity()

	global meteor_config

	conf = None

	try:
		config_path = os.path.join(path_reactivity, "common_site_config.json")
		if os.path.exists(config_path):
			conf = frappe.get_file_json(config_path)
			meteor_config = conf
	except:
		pass

	return conf

if check_dev_mode():
	frappe_conf = frappe.get_site_config()
	frappe_developer_mode = frappe_conf.developer_mode

	if frappe_developer_mode:
		print "Enter Reactivity State!!!"
		import spacebars_template
		import reactivity
