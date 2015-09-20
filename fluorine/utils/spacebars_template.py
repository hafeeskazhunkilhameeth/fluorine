# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'


from jinja2.utils import concat
import frappe
from frappe.utils.jinja import set_filters, get_allowed_functions_for_jenv
import os
from collections import OrderedDict


xhtml_ignores = ["page_relations.xhtml", "AppLayout.xhtml"]



def fluorine_get_fenv():
	from fluorine.utils import get_encoding
	from jinja2 import DebugUndefined
	from fluorine.utils.fjinja2.fjinja import MyEnvironment
	from fluorine.utils.fjinja2.extension_template import MeteorTemplate
	from fluorine.utils.fjinja2.utils import mdom_filter, mself, msuper, tkeep, mtlog

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
		fenv.filters["mlog"] = mtlog

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
	#from fluorine.utils import meteor_desk_app
	from fluorine.utils import get_encoding
	#from fluorine.utils.reactivity import get_read_file_patterns
	from fluorine.utils.file import save_file
	from fluorine.utils.fjinja2.refs import add_fluroine_template_to_dict, get_page_templates_and_refs, add_to_path
	from fluorine.utils.fjinja2.utils import STARTTEMPLATE_SUB_ALL
	from fluorine.utils.api import Api, validate_update_api_list_members
	from fluorine.utils.context import get_app_meteor_template_files_to_process
	#out = {}

	keys = frappe.local.meteor_map_templates.keys()
	#file_patterns = get_read_file_patterns()
	list_apis = frappe.local.list_files_apis

	#ctx = frappe.local.files_to_add
	#fadd = ctx.get("files_to_add")
	#if fadd == None:
	#	ctx["files_to_add"] = {}
	#fadd = ctx.get("files_to_add")
	frappe.local.page_relations[whatfor] = page_relations = []

	for template_path in keys:
		obj = frappe.local.meteor_map_templates.get(template_path)
		template = obj.get("template_obj")

		try:
			if template_path not in frappe.local.templates_referenced:
				content = concat(template.render(template.new_context(context)))
				realpath = obj.get("realpath")

				in_ext = realpath.rsplit(".", 1)[1]
				#fp = file_patterns.get("*.%s" % in_ext)
				#out_ext = fp.get("ext")
				ext_out = obj.get("ext_out")
				ext_len = len(in_ext) + 1
				dstPath = realpath[:-ext_len] + ".%s" % ext_out

				if content and template:
					if context.page_relations:
						page_relations.append(get_page_templates_and_refs(template_path))
					content = "\n\n".join([s for s in content.splitlines() if s])
					#pattern = "%s.%s" % (template_path[:-ext_len], out_ext)
					#context.files_to_add.append({"tname": "", "pattern":pattern, "page": template_path})
					#context.files_to_add.append({"tname": template_path, "file":pattern})
					#auto_out = fp.get("out", True)
					auto_out = obj.get("export", True)
					appname = obj.get("appname")
					if auto_out:
						add_fluroine_template_to_dict(appname, template_path, is_ref=False)
					#if not ctx.get(appname):
					#	ctx[appname] = []
					#ctx.get(appname).append({"tname": template_path, "ref":False})

					save_file(dstPath, content.encode(get_encoding()))
					refs = obj.get("refs")
					tcont = {}
					for m in STARTTEMPLATE_SUB_ALL.finditer(content):
						name = m.group(2)
						#if template.name == "templates/react/meteor_web/extend_teste3.xhtml":
						#print "template {} meteor templates {}".format(template.name, name)
						tcont[name] = m.group(0)
					if auto_out:
						add_to_path(template, refs, tcont)

					api = Api(appname, whatfor, devmode=context.developer_mode)
					get_app_meteor_template_files_to_process(appname, whatfor, template_path, api, context)
					validate_update_api_list_members(api, list_apis)
					list_apis.append(api)
					#toadd.update(add)
					#if whatfor in (meteor_desk_app, "meteor_frappe"):
					#	out.update(tcont)
		except Exception as e:
			from fluorine.commands import meteor_echo
			file_temp_path = obj.get("file_temp_path")
			meteor_echo("template: {}.\n\nError is: {}".format(file_temp_path, e), 80)
			#print "an error occurr removing file {} error {}".format(file_temp_path, e)

	#remove_from_path(context, toadd)

	#from fluorine.utils.fjinja2.utils import local_tkeep

	"""
	for obj in context.files_to_add:
		tname = obj.get("tname")
		pattern = obj.get("pattern")
		page = obj.get("page")
		local_tkeep({"files_to_add":frappe.local.files_to_add}, tname, page, patterns=pattern)
	"""
	return #toadd


"""
def remove_from_path(ctx, toadd):
	for k, v in frappe.local.meteor_map_templates.iteritems():
		template = v.get("template_obj")
		if template:
			for block in template.blocks.keys():
				appname = v.get("appname")
				print "all the known templates tname {} appname {}".format(block, appname)
				tname = toadd.get(block)
				if tname and appname == tname.get(appname):
					continue
				in_ext = k.rsplit(".", 1)[1]
				ext_len = len(in_ext) + 1
				ctx.files_to_remove.append({"tname": k[:-ext_len], "pattern": "", "page": k})
"""


def prepare_common_page_context(context, whatfor):
	from fluorine.utils import check_dev_mode, jquery_include
	from fluorine.utils.meteor.utils import build_meteor_context

	devmode = check_dev_mode()
	context.developer_mode = devmode
	context.jquery_include = jquery_include()

	#Meteor
	build_meteor_context(context, whatfor)
	context.meteor_web = True

	return fluorine_build_context(context, whatfor)

def make_includes(context):

	include_js = context.get("include_js",[])
	include_css = context.get("include_css", [])

	context["include_js"] = include_js + context.meteor_package_js
	context["include_css"] = include_css + context.meteor_package_css


def get_app_pages(context):
	from fluorine.utils import meteor_desk_app, is_making_production
	from fluorine.utils.meteor.utils import make_meteor_props

	context.admin_menus = [{"name":"panel_home", "text":"Home"}, {"name":"panel_profile", "text":"Profile"}]

	context.whatfor = meteor_desk_app
	context = prepare_common_page_context(context, meteor_desk_app)

	devmode = context.developer_mode


	if devmode and not is_making_production():
		make_meteor_props(context, meteor_desk_app)
		make_includes(context)


	return context


def get_web_pages(context):
	from fluorine.utils import meteor_web_app

	context.meteor_web_include_css = frappe.get_hooks("meteor_web_include_css")
	context.meteor_web_include_js = frappe.get_hooks("meteor_web_include_js")

	context.whatfor = meteor_web_app

	context = prepare_common_page_context(context, meteor_web_app)

	return context


def fluorine_build_context(context, whatfor):
	from fluorine.utils.debug import make_page_relations
	from fluorine.utils.reactivity import get_read_file_patterns
	from fluorine.utils.apps import get_active_apps
	from fluorine.utils import meteor_web_app, meteor_config
	from file import make_all_files_with_symlink, empty_directory, get_path_reactivity, copy_project_translation,\
		copy_mobile_config_file, custom_make_all_files_with_symlink
	from fluorine.utils.permission_file import ProcessFileSystem, list_ignores
	from react_file_loader import get_custom_pattern
	from fluorine.utils.meteor.packages import process_meteor_packages_from_apps


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

	#used to indicate the current fluorine xhtml template and current meteor template name
	#{"template": template_path, "tname": tname}
	frappe.local.context.current_xhtml_template = None
	#for to add used meteor templates
	frappe.local.context.files_to_add = frappe._dict()
	frappe.local.context.files_to_remove = frappe._dict()

	#for to add compiled fluorine xhtml templates
	frappe.local.files_to_add = frappe._dict()
	frappe.local.files_to_remove = frappe._dict()

	frappe.local.page_relations = frappe._dict()

	frappe.local.module_registe = frappe._dict()

	#frappe.local.list_jinja_apis = []
	frappe.local.list_files_apis = []

	path_reactivity = get_path_reactivity()

	frappe.local.meteor_ignores = list_ignores.get(whatfor)

	#print "whatfor {} list {}".format(whatfor, frappe.local.meteor_ignores)

	context.page_relations = meteor_config.get("page_relations", True)

	curr_app = meteor_config.get("current_dev_app", "").strip()
	#apps current dev app is in last
	apps = get_active_apps(whatfor)

	pfs_in = frappe.local.context.pfs_in = ProcessFileSystem(whatfor, curr_app)
	pfs_out = frappe.local.context.pfs_out = ProcessFileSystem(whatfor, curr_app)

	process_common_context(apps, whatfor, context, pfs_in, pfs_out)
	process_general_context(apps, whatfor, context, pfs_in, pfs_out)

	pfs_in.compile_pattern()
	pfs_out.compile_pattern()

	apps_remove = pfs_in.get_apps_remove()
	for r in apps_remove:
		apps.remove(r)
	#go from current dev app then last installed app to first installed app in order.
	known_apps = apps[::-1]

	#default_pattern = get_default_custom_pattern()
	custom_pattern = get_custom_pattern(whatfor, custom_pattern=None)

	process_react_templates(known_apps, whatfor, context)

	#do not revert apps. Use from first installed app to current dev app
	#This way we can use context from the first installed to the last installed
	#NOTE others apps may depend on current dev appp but it may be out of other!
	process_extra_context(apps, context)
	process_xhtml_context(context)

	compile_jinja_templates(context, whatfor)

	fluorine_publicjs_dst_path = os.path.join(path_reactivity, whatfor)
	empty_directory(fluorine_publicjs_dst_path, ignore=(".meteor",))

	#read_file_pattern = get_read_file_patterns()
	#make_all_files_with_symlink(known_apps, fluorine_publicjs_dst_path, whatfor, pfs_out, frappe.local.context.files_to_add, custom_pattern=read_file_pattern.keys())
	make_all_files_with_symlink(known_apps, fluorine_publicjs_dst_path, whatfor)

	process_meteor_packages_from_apps(whatfor)
	#custom_make_all_files_with_symlink(known_apps, fluorine_publicjs_dst_path, whatfor, pfs_out, custom_pattern=read_file_pattern.keys())
	copy_project_translation(apps, whatfor, pfs_out, custom_pattern)

	make_page_relations(context, whatfor)
	#Only support for mibile in web app
	if whatfor == meteor_web_app:
		copy_mobile_config_file(known_apps, whatfor)

	return context

def process_react_templates(apps, whatfor, context):
	from fluorine.utils.context import get_app_jinja_files_to_process
	from fluorine.utils.api import Api

	list_apis = frappe.local.list_files_apis

	for app in apps:
		pathname = frappe.get_app_path(app)
		path = os.path.join(pathname, "templates", "react")
		if os.path.exists(path):
			api = Api(app, whatfor, devmode=context.developer_mode)
			get_app_jinja_files_to_process(app, whatfor, api)
			list_apis.append(api)
			#files = read_client_jinja_files(path, app, pfs_in, api.get_list_jinja_files(), meteor_ignore=xhtml_ignores, custom_pattern=custom_pattern)
			files = api.get_list_jinja_files()
			for fobj in files:
				jinja_template_path = fobj.get("relative_path")
				addto_meteor_templates_list(jinja_template_path, fobj.get("ext_out"))



def process_xhtml_context(context):
	from fluorine.utils.context import get_xhtml_context
	#get the context from all the python files of templates
	get_xhtml_context(context)


def process_extra_context(apps, context):
	from fluorine.utils.context import get_extra_context_func
	from reactivity import extras_context_methods

	#get extra context from custom functions
	get_extra_context_func(context, apps, extras_context_methods)


def process_general_context(apps, whatfor, context, pfs_in, pfs_out):
	from fluorine.utils.context import get_general_context

	#get extra context from meteor_general_context.py file. Here we put files to exclude from meteor app.
	get_general_context(context, apps, whatfor, pfs_in, pfs_out)

def process_common_context(apps, whatfor, context, pfs_in, pfs_out):
	from fluorine.utils.context import get_common_context

	#get extra context from meteor_general_context.py file. Here we put files to exclude from meteor app.
	get_common_context(context, apps, whatfor, pfs_in, pfs_out)

def addto_meteor_templates_list(template_path, ext_out="html", export=True):
	from fluorine.utils.context import get_xhtml_files_to_add_remove

	if not frappe.local.meteor_map_templates.get(template_path, None):# and template_path not in frappe.local.templates_referenced:
		template = fluorine_get_fenv().get_template(template_path)
		frappe.local.meteor_map_templates.get(template_path).update({"template_obj": template, "ext_out": ext_out, "export": export})
		#TODO get the context from file of the template...pass the context, the template object and template_path
		#TODO with template_path and frappe.local.meteor_map_templates.get(template_path) get refs if needed to pass macro template object
		#TODO get the context from frappe.local.context!
		get_xhtml_files_to_add_remove(frappe.local.context, template_path)


