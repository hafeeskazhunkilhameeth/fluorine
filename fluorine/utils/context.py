__author__ = 'luissaguas'

import frappe,os, click
from fluorine.utils import whatfor_all, meteor_desk_app, set_making_production


class MeteorContext(object):
	def __init__(self, production=True):
		self.context = frappe._dict({meteor_desk_app:None})
		#frappe.local.making_production = production
		set_making_production(production)

	def meteor_init(self, mongo_custom=False):
		from fluorine.utils.file import get_path_reactivity
		from fluorine.commands_helpers.meteor import meteor_run


		for app in whatfor_all:
			app_path = os.path.join(get_path_reactivity(), app)
			program_json_path = os.path.join(app_path, ".meteor", "local", "build", "programs", "web.browser", "program.json")
			if not os.path.exists(program_json_path) and os.path.exists(os.path.join(app_path, ".meteor")):
				try:
					meteor_run(app, app_path, mongo_custom=mongo_custom)
				except Exception as e:
					click.echo("You have to start meteor at hand before start meteor. Issue `meteor` in %s. Error: %s" % (app_path, e))
					return

	def make_context(self):
		from fluorine.utils import prepare_environment
		from fluorine.utils.reactivity import start_meteor
		from fluorine.utils.finals import make_public_folders
		#from fluorine.command import prepare_make_meteor_file

		make_public_folders()
		prepare_environment()
		start_meteor()
		frappe.local.request = frappe._dict()

		for w in whatfor_all:
			#prepare_compile_environment(w)
			ctx = prepare_context_meteor_file( w)
			if w == meteor_desk_app:
				self.context[meteor_desk_app] = ctx

	def make_meteor_properties(self):
		from fluorine.utils.meteor.utils import make_meteor_props
		from fluorine.utils.spacebars_template import make_includes

		context = self.context.get(meteor_desk_app)
		make_meteor_props(context, meteor_desk_app, production=True)
		make_includes(context)


def remove_output_files(whatfor):
	from fluorine.utils.react_file_loader import get_default_custom_pattern
	from fluorine.utils.apps import get_active_apps
	from fluorine.utils.reactivity import get_read_file_patterns
	from shutil import ignore_patterns


	#custom_pattern = get_default_custom_pattern()
	#pattern = ignore_patterns(*custom_pattern)

	file_patterns = get_read_file_patterns()

	apps = get_active_apps(whatfor)
	for app in apps:
		app_path = frappe.get_app_path(app)
		reactive_path = os.path.join(app_path, "templates", "react", whatfor)
		for root, dirs, files in os.walk(reactive_path):
			#ign_names = pattern(root, files)
			for in_ext, fp in file_patterns.iteritems():
				out_ext = fp.get("ext")
				for f in files:
			#		if f in ign_names:
			#			continue
					f1 = "%s.%s" % (f.split(".",1)[0], in_ext.replace("*.", ""))
					f2 = "%s.%s" % (f.split(".",1)[0], out_ext)
					if f1 in files and f2 in files:
						if f.endswith(".%s" % out_ext):
							os.unlink(os.path.join(root, f))


def prepare_context_meteor_file(whatfor):
	from fluorine.templates.pages.fluorine_home import get_context as fluorine_get_context
	from fluorine.utils import meteor_desk_app, fluor_get_context as get_context

	#remove_output_files(whatfor)

	if whatfor == meteor_desk_app:
		frappe.local.path = "desk"
		return get_context("desk")
	else:
		return fluorine_get_context(frappe._dict())


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


def get_general_context(context, apps, whatfor, pfs_in, pfs_out):

	from fluorine.utils.module import get_app_module

	ctx = frappe._dict()

	for app in apps:
		app_path = frappe.get_app_path(app)
		path = os.path.join(app_path, "templates", "react", whatfor)
		module = get_app_module(path, app, app_path, "meteor_general_context.py")
		if module:
			if hasattr(module, "get_context"):
				nctx = module.get_context(context, ctx) or []

				if isinstance(nctx, dict):
					nctx = [nctx]

				for nc in nctx:
					appname = nc.get("appname")
					pattern = nc.get("pattern")
					pattern = os.path.join("templates", "react", whatfor, pattern)
					action = nc.get("action", "add")
					if not ctx.get(appname):
						ctx[appname] = []

					ctx[appname].append({"pattern": pattern, "action": action})

			if hasattr(module, "get_files_folders"):
				ff = module.get_files_folders(context) or {}
				print "get_files_folders {}".format(ff)

				ffin = ff.get("IN") or ff.get("in") or {}
				pfs_in.feed_files_folders(ffin)

				ffout = ff.get("OUT") or ff.get("out") or {}
				pfs_out.feed_files_folders(ffout)

			if hasattr(module, "get_apps"):
				fapps = module.get_apps(context) or {}

				appsin = fapps.get("IN") or fapps.get("in") or {}
				pfs_in.feed_apps(appsin)

				appsout = fapps.get("OUT") or fapps.get("out") or {}
				pfs_out.feed_apps(appsout)

	#pfs_in.compile_pattern()
	#pfs_out.compile_pattern()

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


def get_common_context(context, apps, whatfor, pfs_in, pfs_out):

	from fluorine.utils.module import get_app_module

	ctx = frappe._dict()

	for app in apps:
		app_path = frappe.get_app_path(app)
		path = os.path.join(app_path, "templates", "react")
		module = get_app_module(path, app, app_path, "meteor_common_context.py")
		if module:
			if hasattr(module, "get_context"):
				nctx = module.get_context(context, ctx, whatfor) or []

				if isinstance(nctx, dict):
					nctx = [nctx]

				for nc in nctx:
					appname = nc.get("appname")
					pattern = nc.get("pattern")
					pattern = os.path.join("templates", "react", whatfor, pattern)
					action = nc.get("action", "add")
					if not ctx.get(appname):
						ctx[appname] = []

					ctx[appname].append({"pattern": pattern, "action": action})

			if hasattr(module, "get_files_folders"):
				ff = module.get_files_folders(context, whatfor) or {}
				print "get_files_folders {}".format(ff)

				ffin = ff.get("IN") or ff.get("in") or {}
				pfs_in.feed_files_folders(ffin)

				ffout = ff.get("OUT") or ff.get("out") or {}
				pfs_out.feed_files_folders(ffout)

			if hasattr(module, "get_apps"):
				fapps = module.get_apps(context, whatfor) or {}

				appsin = fapps.get("IN") or fapps.get("in") or {}
				pfs_in.feed_apps(appsin)

				appsout = fapps.get("OUT") or fapps.get("out") or {}
				pfs_out.feed_apps(appsout)

	#pfs_in.compile_pattern()
	#pfs_out.compile_pattern()

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
				extra_func = getattr(module, extra)
				extra_func(context, app, template_path)
