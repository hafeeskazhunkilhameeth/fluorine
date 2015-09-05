# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'


from jinja2.utils import concat
import frappe
from frappe.utils.jinja import set_filters, get_allowed_functions_for_jenv
import os
from collections import OrderedDict


def fluorine_get_fenv():
	from fluorine.utils import get_encoding
	from jinja2 import DebugUndefined
	from fluorine.utils.fjinja2.fjinja import MyEnvironment
	from fluorine.utils.fjinja2.extension_template import MeteorTemplate
	from fluorine.utils.fjinja2.utils import mdom_filter, mself, msuper, tkeep

	if not frappe.local.fenv:
		encoding = get_encoding()
		fenv = MyEnvironment(loader = fluorine_get_floader(encoding=encoding),
			undefined=DebugUndefined, extensions=[MeteorTemplate, "jinja2.ext.do"])
		set_filters(fenv)

		fenv.globals.update(get_allowed_functions_for_jenv())
		fenv.globals.update({"msuper":msuper})
		fenv.globals.update({"mself":mself})
		fenv.globals.update({"mtkeep":tkeep})
		fenv.filters["mdom_filter"] = mdom_filter

		frappe.local.fenv = fenv

		add_jinja_extension(MeteorTemplate)
		add_jinja_globals([{"msuper":msuper}, {"mself":mself}, {"mtkeep":tkeep}])
		add_jinja_filters({"mdom_filter": mdom_filter})

	return frappe.local.fenv


def add_jinja_filters(filters):
	frappe_env = frappe.get_jenv()
	for k, v in filters.iteritems():
		frappe_env.filters[k] = v

def add_jinja_globals(funcs):
	frappe_env = frappe.get_jenv()
	for f in funcs:
		frappe_env.globals.update(f)

def add_jinja_extension(extension):
	frappe_env = frappe.get_jenv()
	frappe_env.add_extension(extension)

def fluorine_get_floader(encoding="utf-8"):

	from fluorine.utils import APPS
	from fluorine.utils.fjinja2.fjinja import MyChoiceLoader
	from fluorine.utils.fjinja2.fjinja import MyFileSystemLoader

	if not frappe.local.floader:

		path = os.path.normpath(os.path.join(os.getcwd(), "..")) + "/apps"
		apps = APPS[::-1]
		app_fluorine = frappe.get_app_path("fluorine")
		dbname = os.path.join(app_fluorine, "templates/react/temp", "fluorinedb")
		db_dirpath = os.path.dirname(os.path.join(dbname))
		frappe.create_folder(db_dirpath)
		m = MyFileSystemLoader(apps, path, dbpath=dbname, encoding=encoding)
		fluor_loader = [m]

		frappe.local.floader = MyChoiceLoader(fluor_loader)

	return frappe.local.floader


def compile_jinja_templates(context, whatfor):
	from fluorine.utils import meteor_desk_app
	from fluorine.utils import get_encoding
	from file import save_file
	from fluorine.utils.fjinja2.utils import STARTTEMPLATE_SUB_ALL

	out = {}
	toadd = {}

	keys = frappe.local.meteor_map_templates.keys()

	for template_path in keys:
		obj = frappe.local.meteor_map_templates.get(template_path)
		template = obj.get("template_obj")
		realpath = obj.get("realpath")
		dstPath = realpath[:-6] + ".html"
		try:
			if template_path not in frappe.local.templates_referenced:
				content = concat(template.render(template.new_context(context)))

				if content and template:
					content = "\n\n".join([s for s in content.splitlines() if s])
					pattern = template_path[:-6] + r"(?:\.).*"
					context.files_to_add.append({"tname": "", "pattern":pattern, "page": template_path})
					save_file(dstPath, content.encode(get_encoding()))
					refs = obj.get("refs")
					tcont = {}
					for m in STARTTEMPLATE_SUB_ALL.finditer(content):
						name = m.group(2)
						tcont[name] = m.group(0)
					add = add_to_path(context, template, refs, tcont)
					toadd.update(add)
					if whatfor in (meteor_desk_app, "meteor_frappe"):
						out.update(tcont)
		except Exception as e:
			file_temp_path = obj.get("file_temp_path")
			print "an error occurr removing file {} error {}".format(file_temp_path, e)

	remove_from_path(context, toadd)

	from fluorine.utils.fjinja2.utils import local_tkeep

	for obj in context.files_to_add:
		tname = obj.get("tname")
		pattern = obj.get("pattern")
		page = obj.get("page")
		local_tkeep({"files_to_add":frappe.local.files_to_add}, tname, page, patterns=pattern)

	return out


def remove_from_path(ctx, toadd):
	for k, v in frappe.local.meteor_map_templates.iteritems():
		template = v.get("template_obj")
		if template:
			for block in template.blocks.keys():
				appname = v.get("appname")
				if appname == toadd.get(block):
					continue

				ctx.files_to_remove.append({"tname": k[:-6], "pattern": "", "page": k})

def add_to_path(ctx, template, refs, tcont):
	toadd = {}
	for tname in tcont.keys():

		if template and tname not in template.blocks.keys():
			ref = check_refs(tname, refs)
		else:
			ref = template.name

		if ref:
			obj = frappe.local.meteor_map_templates.get(ref)
			appname = obj.get("appname")
			ctx.files_to_add.append({"tname": tname, "pattern": "", "page": ref})
			toadd[tname] = appname

	return toadd


def check_refs(tname, refs):
	for ref in refs:
		obj = frappe.local.meteor_map_templates.get(ref)
		template = obj.get("template_obj")
		if template and tname in template.blocks.keys():
			return ref
		nrefs = obj.get("refs")
		found = check_refs(tname, nrefs)
		if found:
			return found
	return None


def prepare_common_page_context(context, whatfor):
	from fluorine.utils import check_dev_mode, jquery_include#, meteor_config
	from fluorine.utils.meteor.utils import build_meteor_context
	#from fluorine.utils.file import set_config

	devmode = check_dev_mode()
	context.developer_mode = devmode
	context.jquery_include = jquery_include()

	#doc = frappe.get_doc("Fluorine Reactivity")

	#Meteor
	build_meteor_context(context, whatfor)
	context.meteor_web = True
	#context.custom_template = doc.fluorine_base_template

	#if devmode:
	#	set_config({
	#		"production_mode": 0
	#	})

		#meteor_config["production_mode"] = 0

	return fluorine_build_context(context, whatfor)

def make_includes(context):

	include_js = context.get("include_js",[])
	include_css = context.get("include_css", [])
#	try:
#		include_js.remove("/assets/js/meteor_app.min.js")
#	except:
#		pass
#	finally:
	context["include_js"] = include_js + context.meteor_package_js
	context["include_css"] = include_css + context.meteor_package_css

def get_app_pages(context):
	#from fluorine.utils.module import get_app_context
	from fluorine.utils import meteor_desk_app
	from fluorine.utils.meteor.utils import make_meteor_props

	"""
	def get_frappe_context(context):

		app = "frappe"
		app_path = frappe.get_app_path(app)
		path = os.path.join(app_path, "templates", "pages")
		ret = get_app_context(context, path, app, app_path, "desk.py")
		return ret
	"""

	context = prepare_common_page_context(context, meteor_desk_app)

	devmode = context.developer_mode

	try:
		making_production = frappe.local.making_production
	except:
		making_production = False

	print "online devemod 2 {} prodc {}".format(devmode, making_production)

	if devmode and not making_production:
		make_meteor_props(context, meteor_desk_app)
		make_includes(context)


	return context


def get_web_pages(context):
	from fluorine.utils import meteor_web_app

	context.meteor_web_include_css = frappe.get_hooks("meteor_web_include_css")
	context.meteor_web_include_js = frappe.get_hooks("meteor_web_include_js")

	context = prepare_common_page_context(context, meteor_web_app)

	#if devmode:
	#TODO ver se é preciso remove tb o css gerado
	#	try:
	#		context.meteor_web_include_js.remove("/assets/fluorine/js/meteor_web.js")
	#	except:
	#		pass

	return context


def fluorine_build_context(context, whatfor):
	from fluorine.commands_helpers.meteor import get_active_apps
	from fluorine.utils import meteor_web_app, meteor_config
	from file import make_all_files_with_symlink, empty_directory, get_path_reactivity, copy_project_translation, copy_mobile_config_file
	from reactivity import list_ignores
	from react_file_loader import get_custom_pattern


	frappe.local.context = context
	frappe.local.fenv = None
	frappe.local.floader = None
	frappe.local.meteor_map_path = None
	frappe.local.meteor_Templates = None
	frappe.local.meteor_dynamic_templates_remove = frappe._dict()
	frappe.local.jinja_blocks = None
	frappe.local.meteor_ignores = None
	frappe.local.templates_found_add = frappe._dict()
	frappe.local.templates_found_remove = frappe._dict()

	frappe.local.meteor_map_templates = OrderedDict()
	frappe.local.templates_referenced = []

	frappe.local.context.files_to_add = []
	frappe.local.context.files_to_remove = []

	frappe.local.files_to_add = frappe._dict()
	frappe.local.files_to_remove = frappe._dict()
	frappe.local.module_registe = frappe._dict()

	path_reactivity = get_path_reactivity()

	frappe.local.meteor_ignores = list_ignores

	curr_app = meteor_config.get("current_dev_app", "").strip()
	apps = get_active_apps(whatfor)
	if apps[-1] != curr_app:
		#set current dev app in last
		apps.remove(curr_app)
		apps.append(curr_app)

	#go from current dev app then last installed app to first installed app in order.
	known_apps = apps[::-1]
	custom_pattern = get_custom_pattern(whatfor, custom_pattern=None)

	#set current app as the first app
	if curr_app != known_apps[0]:
		known_apps.remove(curr_app)
		known_apps.insert(0, curr_app)

	process_react_templates(context, known_apps, whatfor, custom_pattern)

	fluorine_publicjs_dst_path = os.path.join(path_reactivity, whatfor)
	empty_directory(fluorine_publicjs_dst_path, ignore=(".meteor",))
	make_all_files_with_symlink(fluorine_publicjs_dst_path, whatfor, custom_pattern=["*.xhtml"])

	copy_project_translation(apps, whatfor, custom_pattern)

	#Only support for mibile in web app
	if whatfor == meteor_web_app:
		copy_mobile_config_file(known_apps, whatfor)

	return context

def process_react_templates(context, apps, whatfor, custom_pattern):

	from fluorine.utils import get_attr_from_json
	from fluorine.utils.fhooks import get_xhtml_context
	from react_file_loader import read_client_xhtml_files
	from fluorine.utils.fhooks import get_extra_context_func, get_general_context
	#from fluorine.utils.meteor.utils import compile_spacebars_templates
	from reactivity import extras_context_methods

	#spacebars_templates = {}

	#list_apps_remove = frappe.local.meteor_ignores.get("remove", {}).get("apps")
	list_apps_remove = get_attr_from_json([whatfor, "remove", "apps"], frappe.local.meteor_ignores)

	for app in apps:
		if app in list_apps_remove:
			continue
		pathname = frappe.get_app_path(app)
		path = os.path.join(pathname, "templates", "react")
		if os.path.exists(path):
			files = read_client_xhtml_files(path, whatfor, app, meteor_ignore=frappe.local.meteor_ignores, custom_pattern=custom_pattern)
			for f in files:
				for obj in reversed(f):
				#for obj in f:
					file_path = obj.get("path")
					file_name = obj.get("name")
					root = file_path[:-len(file_name)]
					spacebars_template_path = os.path.join(os.path.relpath(root, pathname), file_name)
					addto_meteor_templates_list(spacebars_template_path)

	#get the context from all the python files of templates
	get_xhtml_context(context)
	get_extra_context_func(context, apps[::-1], extras_context_methods)

	get_general_context(context, apps[::-1], whatfor)

	compile_jinja_templates(context, whatfor)

	#only compile if meteor_app or meteor_frappe
	"""
	if spacebars_templates:
		compiled_spacebars_js = compile_spacebars_templates(spacebars_templates)
		arr = compiled_spacebars_js.split("__templates__\n")
		arr.insert(0, "(function(){\n")
		arr.append("})();\n")
		context.compiled_spacebars_js = arr
	"""

def addto_meteor_templates_list(template_path):
	from fluorine.utils.fhooks import get_xhtml_files_to_add_remove

	if not frappe.local.meteor_map_templates.get(template_path, None):# and template_path not in frappe.local.templates_referenced:
		template = fluorine_get_fenv().get_template(template_path)
		frappe.local.meteor_map_templates.get(template_path).update({"template_obj": template})
		#TODO get the context from file of the template...pass the context, the template object and template_path
		#TODO with template_path and frappe.local.meteor_map_templates.get(template_path) get refs if needed to pass macro template object
		#TODO get the context from frappe.local.context!
		get_xhtml_files_to_add_remove(frappe.local.context, template_path)
		return True
	return False


