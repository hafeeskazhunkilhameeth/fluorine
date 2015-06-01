__author__ = 'luissaguas'

import frappe, os, json

from fluorine.utils import assets_public_path
from fluorine.utils import fcache

def add_react_to_hook(paths, page_default=True):

	lpaths = paths[:]
	hooks = frappe.get_hooks(app_name="fluorine")
	hooks.pop("base_template", None)
	hooks.pop("home_page", None)
	#remove_react_from_hook(hooks, paths)

	#if hooks.app_include_js:
	#	hooks.app_include_js.extend(objjs.get("app_include_js"))
	#else:

	files = get_hook_files_from_disk()

	lpaths.extend([os.path.join(assets_public_path, file.rsplit("/",1)[1]) for file in files])

	print "files from disk {} lpaths {}".format(files, lpaths)

	if hooks.app_include_js:
		remove_react_from_app_hook(lpaths, hooks=hooks, include_files_from_disk=False)
		if hooks.app_include_js:
			hooks.app_include_js.extend(lpaths)
		else:
			hooks.app_include_js = lpaths
	else:
		hooks.app_include_js = lpaths

	if not page_default:
		#fluor.set_base_template(self.fluorine_base_template)
		#objjs["base_template"] = [self.fluorine_base_template]
		hooks["base_template"] = ["templates/fluorine_base.html"]#[fluorine_base_template]#frappe.get_app_path("fluorine") + "/templates" + "/fluorine_base.html"
		hooks["home_page"] = ["fluorine_home"]

	fluorine_publicjs_path = os.path.join(frappe.get_app_path("fluorine"), "public", "js", "react")
	frappe.create_folder(fluorine_publicjs_path)

	save_batch_hook(hooks, frappe.get_app_path("fluorine") + "/hooks.py")

	fcache.clear_frappe_caches()


def remove_react_from_hook(paths, where="app", hooks=None, include_files_from_disk=True):

	lpaths = paths[:]

	if not hooks:
		hooks = frappe.get_hooks(app_name="fluorine")
		hooks.pop("base_template", None)
		hooks.pop("home_page", None)

	hjs = hooks.get(where + "_include_js", None)
	print "removing from app hook where {} hooks app_include_js {}".format(where, hjs)

	if hjs:
		if include_files_from_disk:
			files = get_hook_files_from_disk()
			lpaths.extend([os.path.join(assets_public_path, file.rsplit("/",1)[1]) for file in files])

		for path in lpaths:
			try:
				hjs.remove(path)
			except:
				pass

		if len(hjs) == 0:
			hooks.pop(where + "_include_js")

	save_batch_hook(hooks, frappe.get_app_path("fluorine") + "/hooks.py")
	fcache.clear_frappe_caches()


def remove_react_from_app_hook(paths, hooks=None, include_files_from_disk=True):
	remove_react_from_hook(paths, where="app", hooks=hooks, include_files_from_disk=include_files_from_disk)


def remove_react_from_web_hook(paths, hooks=None, include_files_from_disk=True):
	remove_react_from_hook(paths, where="web", hooks=hooks, include_files_from_disk=include_files_from_disk)


def get_hook_files_from_disk():
	import glob
	fluorine_publicjs_path = os.path.join(frappe.get_app_path("fluorine"), "public", "js", "react")
	return glob.glob(fluorine_publicjs_path + "/*.js")


def save_batch_hook_all(sessionId, objjs):
	save_batch_hook(objjs, frappe.get_app_path("fluorine") + "/hooks.py")
	fcache.save_fluorine_cache(sessionId, objjs)

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
