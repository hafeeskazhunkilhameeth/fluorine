from __future__ import unicode_literals
__author__ = 'luissaguas'


#import hooks
import frappe
import frappe.website.render
from fluorine.utils import file


#called from clear_web (bench frappe --clear_web)
def clear_cache(path):
	print "clear web cache"
	import fluorine, os
	devmode = fluorine.utils.check_dev_mode()
	if devmode:
		path_reactivity = file.get_path_reactivity()
		config_path = os.path.join(path_reactivity, "common_site_config.json")
		f = frappe.get_file_json(config_path)
		if f.get("meteor_folder", None):
			f["meteor_folder"].update({"folder_refresh": 1, "compile": 1})
		else:
			f["meteor_folder"] = {"folder_refresh": 1, "compile": 1}
		file.save_js_file(config_path, f)



def clear_frappe_caches():
	frappe.clear_cache()
	frappe.website.render.clear_cache()

def clear_fluorine_cache(sessionId):
	delete_fluorine_session(sessionId)

def save_fluorine_cache(sessionId, objjs):
	fluorine_set_value(sessionId, objjs)

def delete_fluorine_session(sessionId):
	frappe.cache().delete_value("fluorine:" + sessionId)

def fluorine_set_value(sessionId, data):
	frappe.cache().set_value("fluorine:" + sessionId, data)

def fluorine_get_value(sessionId):
	return frappe.cache().get_value("fluorine:" + sessionId)

def get_cached_value(sessionId):

	data = fluorine_get_value(sessionId)
	print "data cached! {}".format(data)
	if not data:
		data = file.read_file("hook_help.txt")

	return data
