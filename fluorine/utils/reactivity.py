from __future__ import unicode_literals
__author__ = 'luissaguas'


from . import meteor_config
import frappe


start_db = False

def check_mongodb(conf):
	if not conf.get("meteor_mongo"):
		return False

def start_meteor():
	from fluorine.commands_helpers import get_default_site
	from fluorine.utils.permission_file import make_ignor_apps_list

	frappesite = get_default_site()

	make_ignor_apps_list()
	extras_context_methods.update(get_extras_context_method(frappesite))

	global start_db

	if frappe.db and start_db:
		frappe.db.commit()
		frappe.destroy()
		start_db = False

extras_context_methods = set([])

def get_extras_context_method(site):
	from fluorine.utils.fhooks import get_extras_context

	if not frappe.db:
		frappe.init(site=site)
		frappe.connect()
		global start_db
		start_db = True

	hooks = get_extras_context()

	return hooks

import logging
logger = logging.getLogger("frappe")
if not meteor_config.get("production_mode") and not meteor_config.get("stop"):
	logger.error('starting reactivity...')
	start_meteor()