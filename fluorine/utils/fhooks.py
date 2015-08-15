from __future__ import unicode_literals
__author__ = 'luissaguas'

import frappe, os, json

"""
hook_helper_json = "hook_helper.json"

def change_base_template(devmod=1, page_default=True):
	from fluorine.utils.file import save_js_file

	fluorine_path = frappe.get_app_path("fluorine")
	hook_helper = os.path.join(fluorine_path, hook_helper_json)
	if os.path.exists(hook_helper):
		hook = frappe._dict(frappe.get_file_json(hook_helper))
	else:
		hook = frappe._dict()

	if not page_default:
		hook["base_template"] = ["templates/fluorine_base.html"]
		hook["home_page"] = ["fluorine_home"]
	else:
		if hook.base_template:
			del hook["base_template"]
		if hook.home_page:
			del hook["home_page"]

	hook.devmod = devmod

	save_js_file(hook_helper, hook)
"""

def change_base_template(hooks=None, page_default=True):
	from fluorine.utils.fcache import clear_frappe_caches

	#def remove_meteor_include():
	#	try:
	#		hooks.get("app_include_js").remove("/assets/js/meteor_app.js")
	#	except:
	#		pass

	if not hooks:
		hooks = frappe.get_hooks(app_name="fluorine")
		hooks.pop("base_template", None)
		hooks.pop("home_page", None)

	if not page_default:
		hooks["base_template"] = ["templates/fluorine_base.html"]
		hooks["home_page"] = ["fluorine_home"]

	#remove_meteor_include()

	#if not devmode:
	#	app_include_js = hooks.get("app_include_js")
	#	if app_include_js:
	#		app_include_js.append("/assets/js/meteor_app.js")
	#	else:
	#		hooks["app_include_js"] = ["/assets/js/meteor_app.js"]


	fluorine_path = frappe.get_app_path("fluorine")
	save_batch_hook(hooks, fluorine_path + "/hooks.py")
	clear_frappe_caches()

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

#not used
def remove_react_from_app_hook(paths, hooks=None, include_files_from_disk=True):
	remove_react_from_hook(paths, where="app", hooks=hooks, include_files_from_disk=include_files_from_disk)

#not used
def remove_react_from_web_hook(paths, hooks=None, include_files_from_disk=True):
	remove_react_from_hook(paths, where="web", hooks=hooks, include_files_from_disk=include_files_from_disk)


def get_hook_files_from_disk():
	import glob
	fluorine_publicjs_path = os.path.join(frappe.get_app_path("fluorine"), "public", "js", "react")
	return glob.glob(fluorine_publicjs_path + "/*.js")


def save_batch_hook_all(sessionId, objjs):
	from fluorine.utils import fcache

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


def get_xhtml_files_to_add_remove(context, template_path):
	obj = frappe.local.meteor_map_templates.get(template_path)
	path = obj.realpath[:-6] + ".py"
	appname = obj.get("appname")
	module = get_xhtml_module(appname, template_path, path)
	if module:

		if hasattr(module, "get_files_to_add"):
			ret = module.get_files_to_add(context, appname, template_path, obj.get("template_obj"))
			if ret:
				if isinstance(ret, basestring):
					context.files_to_add.append({"tname": "", "pattern": ret, "page": template_path})
				else:
					context.files_to_add.append(ret)

		if hasattr(module, "get_files_to_remove"):
			ret = module.get_files_to_remove(context, appname, template_path, obj.get("template_obj"))
			if ret:
				if isinstance(ret, basestring):
					context.files_to_remove.append({"tname": "", "pattern": ret, "page": template_path})
				else:
					context.files_to_remove.append(ret)

def get_xhtml_context(context):

	for template_path in reversed(frappe.local.meteor_map_templates.keys()):
		obj = frappe.local.meteor_map_templates.get(template_path)
		path = obj.realpath[:-6] + ".py"
		appname = obj.get("appname")
		module = get_xhtml_module(appname, template_path, path)
		if module:
			if hasattr(module, "get_context"):
				ret = module.get_context(context, appname, template_path, obj.get("template_obj"))
				if ret:
					#print "get context app_path 6 controller_path {} ret {}".format(controller_path + ".py", ret)
					context.update(ret)
			if hasattr(module, "get_children"):
				context.get_children = module.get_children

#TODO - ver file.py function process_ignores_from_files
def get_xhtml_module(appname, template_path, path):

	if os.path.exists(path):
		controller_path = os.path.join(appname, template_path).replace(os.path.sep, ".")[:-6]
		module = frappe.get_module(controller_path)
		frappe.local.module_registe[appname] = frappe._dict({"template_path": template_path, "module": module})
		return module

	return None


def get_general_context(context, apps, whatfor):

	from fluorine.utils.module import get_app_module

	ctx = frappe._dict()

	for app in apps:
		app_path = frappe.get_app_path(app)
		path = os.path.join(app_path, "templates", "react", whatfor)
		module = get_app_module(path, app, app_path, "meteor_general_context.py")
		if module:
			if hasattr(module, "get_context"):
				nctx = module.get_context(context, ctx, whatfor)
				if not nctx:
					continue
				for nc in nctx:
					appname = nc.get("appname")
					pattern = nc.get("pattern")
					pattern = os.path.join("templates", "react", whatfor, pattern)
					action = nc.get("action", "add")
					if not ctx.get(appname):
						ctx[appname] = []

					ctx[appname].append({"pattern": pattern, "action": action})

	for k,v in ctx.iteritems():
		for obj in v:
			pattern = obj.get("pattern")
			action = obj.get("action", "add")
			if action == "add":
				if not frappe.local.files_to_add.get(k):
					frappe.local.files_to_add[k] = []
				frappe.local.files_to_add.get(k).append({"tname": "", "pattern": pattern})
			elif action == "remove":
				if not frappe.local.files_to_remove.get(k):
					frappe.local.files_to_remove[k] = []
				frappe.local.files_to_remove.get(k).append({"tname": "", "pattern": pattern})

	return

def get_extra_context_func(context, apps, extras):

	for app in apps:
		obj = frappe.local.module_registe.get(app)
		if not obj:
			continue
		module = obj.module
		template_path = obj.template_path
		for extra in extras:
			if hasattr(module, extra):
				extra_func = getattr(module, extra)#estava 'method_name'
				extra_func(context, app, template_path)

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