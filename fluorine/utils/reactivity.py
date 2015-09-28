from __future__ import unicode_literals
__author__ = 'luissaguas'


from . import meteor_config
import frappe

start_db = False

"""
read_patterns = None

#read_patterns is a dict with extension to read and extension to write
def get_read_file_patterns():

	global read_patterns
	if read_patterns:
		return read_patterns

	read_patterns = {"*.xhtml": {"ext":"html"}}

	read_file_patterns = meteor_config.get("read_patterns", {})
	for k, v in read_file_patterns.iteritems():
		if not k.startswith("*."):
			k = "*.%s" % k
		read_patterns[k] = {"ext": v.get("ext"), "out": v.get("out", True)}
		print "read_pattern {}".format(read_patterns)

	return read_patterns
"""

def check_mongodb(conf):
	if not conf.get("meteor_mongo"):
		return False

def start_meteor():
	from fluorine.commands_helpers import get_default_site
	from fluorine.utils.permission_file import make_meteor_ignor_files

	frappesite = get_default_site()

	make_meteor_ignor_files()
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
		#user = "Administrator"
		frappe.init(site=site)
		frappe.connect()
		#frappe.set_user(user)
		global start_db
		start_db = True

	hooks = get_extras_context()

	return hooks

import logging
logger = logging.getLogger("frappe")
if not meteor_config.get("production_mode") and not meteor_config.get("stop"):
	logger.error('starting reactivity...')
	start_meteor()