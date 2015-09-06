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
	from fluorine.commands_helpers import get_default_site

	frappesite = get_default_site()

	make_meteor_ignor_files()
	extras_context_methods.update(get_extras_context_method(frappesite))

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

"""
below app_name is a valid fluorine app.

Structure:

IN:
	ff = {
		"app_name":{
			remove:[{"pattern": "pattern_1"}, {"pattern": "pattern_2"}],
			add:[{"pattern": "pattern_1"}, {"pattern": "pattern_2"}]
		}
	}

OUT:
	list_ff_add and list_ff_remove = {
		"app_name":["pattern_1", "pattern_2"]
	}

"""
def process_permission_files_folders(ff):
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
	from fluorine.utils import whatfor_all, meteor_desk_app, meteor_web_app
	from fluorine.utils import get_attr_from_json

	global list_ignores

	list_ignores = frappe._dict({meteor_web_app:{}, meteor_desk_app:{}})

	for whatfor in whatfor_all:
		conf = get_permission_files_json(whatfor)
		list_apps_remove = process_permission_apps(conf.get("apps") or {})
		list_meteor_files_folders_add, list_meteor_files_folders_remove = process_permission_files_folders(conf.get("files_folders") or {})

		list_ignores.get(whatfor).update({
			"remove":{
				"apps": list_apps_remove,
				"files_folders": list_meteor_files_folders_remove
			},
			"add":{
				"apps": [],
				"files_folders": list_meteor_files_folders_add
			}
		})

		if meteor_config.get("production_mode") or frappe.local.making_production:
			l = get_attr_from_json([whatfor, "remove", "files_folders"], list_ignores)
			l.update({
				"all":{
					"remove": [{"pattern": "highlight/?.*"}]
				}
			})

	logger = logging.getLogger("frappe")
	logger.error("list_ignores {}".format(list_ignores))
	return list_ignores


def get_permission_files_json(whatfor):
	#from fluorine.utils import APPS as apps
	from fluorine.utils.apps import get_active_apps

	curr_app = meteor_config.get("current_dev_app", "").strip()
	apps = get_active_apps(whatfor)
	if curr_app != apps[-1]:
		#set current dev app in last
		apps.remove(curr_app)
		apps.append(curr_app)

	conf_perm = frappe._dict()

	#curre develop app override everything follow by last installed app.
	for app in apps:
		app_path = frappe.get_app_path(app)
		perm_path = os.path.join(app_path, "templates", "react", whatfor, "permission_files.json")
		if os.path.exists(perm_path):
			conf_file = frappe.get_file_json(perm_path)
			for k,v in conf_file.iteritems():
				key = conf_perm.get(k)
				if key:
					key.update(v)
				else:
					conf_perm[key] = v

	return conf_perm


import logging
logger = logging.getLogger("frappe")
if not meteor_config.get("production_mode") and not meteor_config.get("stop"):
	logger.error('starting reactivity...')
	start_meteor()