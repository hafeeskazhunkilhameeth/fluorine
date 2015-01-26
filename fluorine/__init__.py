from __future__ import unicode_literals

#import fluorine
import hooks, frappe, json, os
import frappe.website.render
from .utils import file

#import utils
#import utils.file

#print "dir file {}".format(dir(file))

def check_dev_mode():
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

#print "frappe.conf start {}".format(frappe.get_site_config())
#if frappe.conf and frappe.conf.developer_mode:

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

"""
def set_base_template(bt):
	clear_cache()
	save_hooks('base_template', [bt])
"""
"""
def _reactivity2(where, path):
	arrjs = []
	arrjs.extend(path)
	save_hooks(where + '_include_js', arrjs)
"""
"""
def reactivity2(state, where, path):
	clear_cache()
	remove_file("hook_help.txt")
	if state == "off":
		return

	if where == "both":
		_reactivity2("app", path)
		_reactivity2("web", path)
	else:
		_reactivity2(where, path)
"""

"""
def reactivity(state, where, path):
	clear_cache()
	remove_file("hook_help.txt")
	if state == "off":
		return

	objjs = {}

	if where == "both":
		objjs["app_include_js"] = path
		objjs["web_include_js"] = path
	else:
		objjs[where + "_include_js"] = path

	save_batch_hook(objjs)
"""

def save_batch_hook_all(sessionId, objjs):
	save_batch_hook(objjs)
	save_fluorine_cache(sessionId, objjs)

def save_batch_hook(objjs, file_path):
	#module_path = os.path.dirname(fluorine.__file__)
	#file_path = file.get_path_fluorine("hook_help.txt")
	#with open(os.path.join(module_path, "hook_help.txt"), "w") as f:
	with open(file_path, "w") as f:
		for key in objjs:
			value = objjs.get(key)
			#if isinstance(value, (list,dict,tuple)):
			f.write(key + '=' + json.dumps(value) + os.linesep)
			#else:
			#	f.write(key + '=' + json.dumps(value) + os.linesep)

"""
def save_hooks(key, value):
	module_path = os.path.dirname(fluorine.__file__)
	with open(os.path.join(module_path, "hook_help.txt"), "a") as f:
		if isinstance(value, (list,dict,tuple)):
			f.write(key + '=' + json.dumps(value) + os.linesep)
		else:
			f.write(key + '=' + value + os.linesep)
"""
"""
def set_hook_attr(key, val):
	setattr(hooks,key, val)
"""

"""
def update_hooks():
	d = read_file("hook_help.txt")
	for key in d:
		set_hook_attr(key, d.get(key))
"""

def get_cached_value(sessionId):
	data = fluorine_get_value(sessionId)
	print "data cached! {}".format(data)
	if not data:
		data = file.read_file("hook_help.txt")

	return data


"""
def override_jinja_jloader(path="."):
	original_jinja_jloader = frappe.utils.jinja.get_jloader
	from .utils.fjinja import MyFileSystemLoader
	from jinja2 import ChoiceLoader

	def fluorine_get_jloader():
		fl = frappe.get_doc("Fluorine Reactivity")
		#fluor_base_template = fl.fluorine_base_template.lower()
		if not frappe.local.jloader:
			if check_dev_mode() and fl.fluorine_state == "on":#and fluor_base_template and fluor_base_template !="default"
				#orig_loader = original_jinja_jloader().loaders
				apps = frappe.get_installed_apps()[::-1]
				fluor_loader = [MyFileSystemLoader(apps, path)]
				print "myfluor_loader {}".format(fluor_loader)
				frappe.local.jloader = ChoiceLoader(fluor_loader)
				return frappe.local.jloader

			#print "my jinja jloader {} cwd {}".format(frappe.get_doc("Fluorine Reactivity").fluorine_base_template, path)
			return original_jinja_jloader()

	frappe.utils.jinja.get_jloader = fluorine_get_jloader

override_jinja_jloader(os.path.normpath(os.path.join(os.getcwd(), "..")) + "/apps")
"""

#make_meteor_file()

if check_dev_mode():
	print "Enter Reactivity State!!!"
	from .utils import spacebars_template
	from .utils import reactivity
