from __future__ import unicode_literals
__author__ = 'luissaguas'

import frappe, os, json


class FluorineHooks(object):

	def __init__(self, site=None):
		self.hooks = frappe.get_hooks(app_name="fluorine")
		self.site = site

	def __enter__(self):
		return self

	def __exit__(self, type, value, trace):
		return self.save_hook()

	def change_base_template(self, page_default=True):
		self.hooks.pop("base_template", None)
		self.hooks.pop("home_page", None)

		if not page_default:
			self.hooks["base_template"] = ["templates/fluorine_base.html"]
			self.hooks["home_page"] = ["fluorine_home"]


	def hook_app_include(self, ijs, icss):

		app_include_js = self.hooks.get("app_include_js") or []
		app_include_css = self.hooks.get("app_include_css") or []

		itemp = app_include_js[:]

		for file in itemp:
			if file == "/assets/js/meteor_app.min.js":
				app_include_js.remove(file)

		itemp = app_include_css[:]

		for file in itemp:
			if file == "/assets/css/meteor_app.css":
				app_include_css.remove(file)

		if app_include_js:
			app_include_js.extend(ijs)
		elif ijs:
			self.hooks["app_include_js"] = ijs

		if app_include_css:
			app_include_css.extend(icss)
		elif icss:
			self.hooks["app_include_css"] = icss


	def remove_hook_app_include(self):

		app_include_js = self.hooks.get("app_include_js") or []
		app_include_css = self.hooks.get("app_include_css") or []

		itemp = app_include_js[:]

		for file in itemp:
			if file == "/assets/js/meteor_app.min.js":
				app_include_js.remove(file)

		itemp = app_include_css[:]

		for file in itemp:
			if file == "/assets/css/meteor_app.css":
				app_include_css.remove(file)

		if not app_include_js:
			self.hooks.pop("app_include_js", None)

		if not app_include_css:
			self.hooks.pop("app_include_css", None)


	def save_hook(self):
		fluorine_path = frappe.get_app_path("fluorine")
		save_batch_hook(self.hooks, os.path.join(fluorine_path, "hooks.py"))

"""
#not used
def add_react_to_hook(paths, page_default=True):
	from fluorine.utils import assets_public_path
	from fluorine.utils import fcache

	lpaths = paths[:]
	hooks = frappe.get_hooks(app_name="fluorine")
	hooks.pop("base_template", None)
	hooks.pop("home_page", None)

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
		hooks["base_template"] = ["templates/fluorine_base.html"]#[fluorine_base_template]#frappe.get_app_path("fluorine") + "/templates" + "/fluorine_base.html"
		hooks["home_page"] = ["fluorine_home"]

	fluorine_publicjs_path = os.path.join(frappe.get_app_path("fluorine"), "public", "js", "react")
	frappe.create_folder(fluorine_publicjs_path)

	save_batch_hook(hooks, frappe.get_app_path("fluorine") + "/hooks.py")

	fcache.clear_frappe_caches()
"""
"""
#not used
def remove_react_from_hook(paths, where="app", hooks=None, include_files_from_disk=True):
	from fluorine.utils import assets_public_path
	from fluorine.utils import fcache

	lpaths = paths[:]

	if not hooks:
		hooks = frappe.get_hooks(app_name="fluorine")
		hooks.pop("base_template", None)
		hooks.pop("home_page", None)

	hjs = hooks.get(where + "_include_js", None)

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
"""
"""
#not used
def remove_react_from_app_hook(paths, hooks=None, include_files_from_disk=True):
	remove_react_from_hook(paths, where="app", hooks=hooks, include_files_from_disk=include_files_from_disk)

#not used
def remove_react_from_web_hook(paths, hooks=None, include_files_from_disk=True):
	remove_react_from_hook(paths, where="web", hooks=hooks, include_files_from_disk=include_files_from_disk)
"""

def get_hook_files_from_disk():
	import glob
	fluorine_publicjs_path = os.path.join(frappe.get_app_path("fluorine"), "public", "js", "react")
	return glob.glob(fluorine_publicjs_path + "/*.js")


def save_batch_hook_all(sessionId, objjs):
	from fluorine.utils import fcache

	save_batch_hook(objjs, frappe.get_app_path("fluorine") + "/hooks.py")
	fcache.save_fluorine_cache(sessionId, objjs)

def save_batch_hook(objjs, file_path):
	with open(file_path, "w") as f:
		for key, value in objjs.iteritems():
			f.write(key + '=' + json.dumps(value) + os.linesep)
			f.flush()

def get_extras_context():
	hooks = frappe.get_hooks("fluorine_extras_context_method")
	return hooks


def check_jquery(hook, hooks):
	found = False
	iweb = hooks.get(hook, None)
	for a in ("jquery.min.js", "jquery.js"):
		if iweb and any(a in s for s in iweb):
			found = True
			break
	if not found:
		iweb.insert(0, "/assets/frappe/js/lib/jquery/jquery.min.js")
		print "jquery not found, inserting frappe jquery!"


def check_includes(hook, hooks):
	iweb = hooks.get(hook, None)
	if iweb and not any("before_fluorine_helper" in s for s in iweb):
		update_includes(hook,iweb)
	elif iweb:
		to_remove = []
		for include in iweb:
			if "before_fluorine_helper" in include or "after_fluorine_helper" in include:
				to_remove.append(include)
		for i in to_remove:
			iweb.remove(i)
		update_includes(hook, iweb)


def update_includes(hook, iweb):
	from fluorine.utils import fcache

	d = fcache.get_cached_value("hooks_helper")

	if not d:
		return

	fweb = d.get(hook, None)
	if fweb:
		iweb.insert(0, fweb[0])
		iweb.insert(1, fweb[1])
		if fweb[2:]:
			iweb.extend(fweb[2:])
		fcache.clear_frappe_caches()


class FrappeContext:

	def __init__(self, site, user):
		self.site = site
		self.user = user

	def __enter__(self):
		frappe.init(site=self.site)
		frappe.connect()
		print frappe.local.site
		frappe.set_user(self.user)

	def __exit__(self, type, value, trace):
		if frappe.db:
			frappe.db.commit()
		frappe.destroy()