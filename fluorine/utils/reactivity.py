from __future__ import unicode_literals
__author__ = 'luissaguas'

import os
from . import meteor_config
import frappe

start_db = False

def check_mongodb(conf):
	if not conf.get("meteor_mongo"):
		return False

def start_meteor():
	#import frappe
	#from fluorine.utils.mongodb.utils import is_mongodb_ready, set_frappe_users, save_mongodb_config
	#from file import get_common_config_file_json

	conf = meteor_config
	#check_mongodb(conf)

	#make_mongodb_default(conf)
	#mongo = conf.get("meteor_mongo") or {}
	#mghost = mongo.get("host") or "127.0.0.1"
	#mgport = mongo.get("port") or 3001#port of meteor local mongodb
	#mgdb = mongo.get("db") or "fluorine_test"

	frappesite = conf.get("site")

	extras_context_methods.update(get_extras_context_method(frappesite))

	#common_file = get_common_config_file_json()
	#if not is_mongodb_ready(common_file):
	#	set_frappe_users(mghost, mgport, mgdb)
	#	common_file["mongodb_users_ready"] = 1
	#	save_mongodb_config(common_file)

	global start_db

	if frappe.db and start_db:
		frappe.set_user("guest")
		frappe.db.commit()
		frappe.destroy()
		start_db = False

extras_context_methods = set([])

def get_extras_context_method(site):
	from fluorine.utils.fhooks import get_extras_context

	if not frappe.db:
		user = "Administrator"
		frappe.init(site=site)
		frappe.connect()
		frappe.set_user(user)
		global start_db
		start_db = True

	make_meteor_ignor_files()
	hooks = get_extras_context()

	return hooks

list_ignores = None

def process_permission_apps(apps):

	list_apps_add = []
	list_apps_remove = []

	for k, v in apps.iteritems():
		if v.get("remove", 0):
			if k not in list_apps_add:
				list_apps_remove.append(k)
		elif v.get("add", 0):
			if k not in list_apps_remove:
				list_apps_add.append(k)

	return list_apps_remove

def process_permission_files_folders(ff):
	#import frappe
	from fluorine.utils.fjinja2.utils import c

	list_ff_add = frappe._dict()
	list_ff_remove = frappe._dict()

	for k, v in ff.iteritems():
		remove = v.get("remove") or []
		for r in remove:
			if not list_ff_remove.get(k):
				list_ff_remove[k] = []
			pattern = c(r.get("pattern"))
			list_ff_remove[k].append(pattern)

		add = v.get("add") or []
		for a in add:
			if not list_ff_add.get(k):
				list_ff_add[k] = []
			pattern = c(a.get("pattern"))
			list_ff_add[k].append(pattern)

	return list_ff_add, list_ff_remove

def make_meteor_ignor_files():
	import file#, frappe
	path_reactivity = file.get_path_reactivity()
	perm_path = os.path.join(path_reactivity, "permission_files.json")

	if not os.path.exists(perm_path):
		file.save_js_file(perm_path, {"apps":{}, "files_folders":{}})

	conf = frappe.get_file_json(perm_path)

	list_apps_remove = process_permission_apps(conf.get("apps") or {})
	list_meteor_files_folders_add, list_meteor_files_folders_remove = process_permission_files_folders(conf.get("files_folders") or {})

	global list_ignores

	list_ignores = frappe._dict({
		"remove":{
			"apps": list_apps_remove,
			"files_folders": list_meteor_files_folders_remove
		},
		"add":{
			"apps": [],
			"files_folders": list_meteor_files_folders_add
		}
	})

	return list_ignores
	#print "list apps to remove {}".format(list_ignores)

"""
def is_open_port(ip="127.0.0.1", port=3070):
	import socket
	is_open = False
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	result = sock.connect_ex((ip,port))
	if result == 0:
		is_open = True
	sock.close()
	return is_open
"""

import sys

if any("--serve"==s or "--start"==s or "serve"==s for s in sys.argv) and not meteor_config.get("production_mode"):
	#import frappe
	#print "starting reactivity...{}".format(sys.argv)
	start_meteor()