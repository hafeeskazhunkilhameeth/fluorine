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



def clear_frappe_caches(site=None):

	if not frappe.db:
		if not site:#TODO get default site from file
			try:
				with open("currentsite.txt") as f:
					site = f.read().strip()
			except IOError:
				site = None
		frappe.connect(site)

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

"""
def save_sites_to_cache(link_sites):

	for site in link_sites:
		dedicated_name = site.fluorine_site_name
		frappe.cache().set_value("fluorine:site:%s" % dedicated_name, dedicated_name)
		doc_fluorine_site = frappe.get_doc("Fluorine Site Names", dedicated_name)
		sites_dependents = doc_fluorine_site.fluorine_table_site_dependents
		for site_dependent in sites_dependents:
			site_dependents_name = site_dependent.fluorine_site_name
			frappe.cache().set_value("fluorine:site:%s" % site_dependents_name, dedicated_name)


def get_dedicated_site_name(current_site):

	site_name = frappe.cache().get_value("fluorine:site:%s" % current_site)
	if not site_name:
		doc_fluorine_reactivity = frappe.get_doc("Fluorine Reactivity")
		link_sites = doc_fluorine_reactivity.fluorine_link_sites
		save_sites_to_cache(link_sites)
		site_name = frappe.cache().get_value("fluorine:site:%s" % current_site)

	return site_name
"""