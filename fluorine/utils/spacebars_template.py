# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'


#from frappe.website.utils import scrub_relative_urls
from jinja2.utils import concat
import frappe
from frappe.utils.jinja import set_filters, get_allowed_functions_for_jenv
import os
from collections import OrderedDict


def fluorine_get_fenv():
	from fluorine.utils import get_encoding
	from jinja2 import DebugUndefined
	from fluorine.utils.fjinja2.fjinja import MyEnvironment
	from extension_template import MeteorTemplate
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
		#fenv.filters["mecho"] = mecho
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

	from fluorine.utils.fjinja2.fjinja import MyChoiceLoader
	from fluorine.utils.fjinja2.fjinja import MyFileSystemLoader

	if not frappe.local.floader:

		path = os.path.normpath(os.path.join(os.getcwd(), "..")) + "/apps"
		#first template to load is the last installed
		#So, we can replace the oldest template by new one with the same name
		apps = frappe.get_installed_apps()[::-1]
		app_fluorine = frappe.get_app_path("fluorine")
		dbname = os.path.join(app_fluorine, "templates/react/temp", "fluorinedb")
		db_dirpath = os.path.dirname(os.path.join(dbname))
		frappe.create_folder(db_dirpath)
		m = MyFileSystemLoader(apps, path, dbpath=dbname, encoding=encoding)
		fluor_loader = [m]

		frappe.local.floader = MyChoiceLoader(fluor_loader)

	return frappe.local.floader


def fluorine_get_template(path):
	return fluorine_get_fenv().addto_meteor_templates_list(path)


def compile_jinja_templates(context, whatfor):

	from fluorine.utils import get_encoding
	from file import save_file
	from fluorine.utils.fjinja2.utils import STARTTEMPLATE_SUB_ALL

	#print "mtl list de templates {}".format(mtl)
	out = {}
	toadd = {}
	print "frappe.local.meteor_map_templates 2 {}".format(frappe.local.meteor_map_templates.keys())
	keys = frappe.local.meteor_map_templates.keys()

	for template_path in keys:
		obj = frappe.local.meteor_map_templates.get(template_path)
		template = obj.get("template_obj")
		realpath = obj.get("realpath")
		dstPath = realpath[:-6] + ".html"
		#template_path = obj.get("template")
		tname = os.path.basename(template_path)
		print "dstPath in compile jinja2 17 {} template {} appname {} template {}".format(dstPath, tname, obj.get("appname"), template)
		#dstPath = frappe.local.meteor_map_path[l.get("tpath")].get("realpath")[:-6] + ".html"
		#dstPath = template.filename[:-6].replace("templates/react/temp","templates/react",1) + ".html"

		try:
			#if not frappe.local.files_to_add.get(obj.get("appname")):
			#	frappe.local.files_to_add[obj.get("appname")] = []
			if template_path not in frappe.local.templates_referenced:
				print "calling render template from compile jinja {}".format(template_path)
				#content = scrub_relative_urls(concat(template.render(template.new_context(context))))
				content = concat(template.render(template.new_context(context)))
			#re_file = fnmatch.translate(realpath[:-6] + "[./]*")
			#pattern = get_pattern_path(tname[:-6], realpath)
			#content = ""
			#print "template in compile jinja templates 23 pattern {} blocks {} content {}".format(pattern, template, template.blocks, content)
				if content and template: #and template.blocks:
					#print "l.get save to file {}".format(l.get("save"))
					content = "\n\n".join([s for s in content.splitlines() if s])
					#if template_path not in frappe.local.templates_referenced:
					#print "not in reference files template_path 4 {} referenced {}\n".format(template_path, frappe.local.templates_referenced)
					#pattern = realpath[:-6] + r"[/.](.*)"
					#pattern = realpath[:-6] + r"(?:\.).*"
					pattern = template_path[:-6] + r"(?:\.).*"
					#frappe.local.files_to_add.get(obj.get("appname")).append({"tname": template_path, "pattern":pattern})
					context.files_to_add.append({"tname": "", "pattern":pattern, "page": template_path})
					#pattern = realpath[:-6] + r"/common/(.*)"
					#context.files_to_add.get(obj.get("appname")).append({"tname": template_path, "path": c(pattern), "pattern":pattern})
					save_file(dstPath, content.encode(get_encoding()))
					refs = obj.get("refs")
					#template_path = obj.get("template")
					tcont = {}
					for m in STARTTEMPLATE_SUB_ALL.finditer(content):
						name = m.group(2)
						tcont[name] = m.group(0)
					add = add_to_path(context, template, refs, tcont)
					toadd.update(add)
					if whatfor in ("meteor_app", "meteor_frappe"):
						out.update(tcont)
					#print "templates teste with finditer template name 9 {} template is {}".format(m.group(2), m.group(0))

				"""
				items = template.blocks.items()
				for block, render in items:
					if block.startswith("spacebars"):
						nameblock = block[10:]
						#make_heritage(block, context)
						block = scrub_relative_urls(concat(render(template.new_context(context))))
						out[nameblock] = block
						print "templates teste with finditer template name 5 {} template is {}".format(nameblock, block)
				"""
			#else:
			#	os.remove(dstPath)
		except Exception as e:
			file_temp_path = obj.get("file_temp_path")
			print "an error occurr removing file {} error {}".format(file_temp_path, e)
			#os.remove(file_temp_path)

		#file_temp_path = doc.file_temp_path
		#frappe.create_folder(os.path.dirname(file_temp_path))
		#write(file_temp_path, contents)

	remove_from_path(context, toadd)

	from fluorine.utils.fjinja2.utils import local_tkeep

	for obj in context.files_to_add:
		tname = obj.get("tname")
		pattern = obj.get("pattern")
		page = obj.get("page")
		local_tkeep({"files_to_add":frappe.local.files_to_add}, tname, page, patterns=pattern)

	return out


def remove_from_path(ctx, toadd):
	#fremove = ctx.get("files_to_remove", {})
	for k, v in frappe.local.meteor_map_templates.iteritems():
		template = v.get("template_obj")
		if template:
			for block in template.blocks.keys():
				appname = v.get("appname")
				if appname == toadd.get(block):
					continue
				#if not frappe.local.files_to_remove.get(appname):
				#	frappe.local.files_to_remove[appname] = []
				#realpath = v.get("realpath")
				ctx.files_to_remove.append({"tname": k[:-6], "pattern": "", "page": k})
				#pattern = get_pattern_path(block, k[:-6])
				#fremove.get(appname).append({"tname": block, "path": c(pattern)})
				#frappe.local.files_to_remove.get(appname).append({"tname": k, "pattern": pattern})
				print "blocks to remove are: block name 7 {} appname {} toadd {}".format(block, appname, toadd)

def add_to_path(ctx, template, refs, tcont):
	#fadd = ctx.get("files_to_add",{})
	toadd = {}
	for tname in tcont.keys():

		if template and tname not in template.blocks.keys():
			ref = check_refs(tname, refs)
		else:
			ref = template.name

		if ref:
			obj = frappe.local.meteor_map_templates.get(ref)
			appname = obj.get("appname")
			#if not frappe.local.files_to_add.get(appname):
			#	frappe.local.files_to_add[appname] = []
			#realpath = obj.get("realpath")
			ctx.files_to_add.append({"tname": tname, "pattern": "", "page": ref})
			#pattern = get_pattern_path(tname, ref[:-6])
			#fadd.get(appname).append({"tname": tname, "path": c(pattern)})
			#frappe.local.files_to_add.get(appname).append({"tname": ref, "pattern":pattern})
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
	from fluorine.utils import check_dev_mode, jquery_include
	from fluorine.utils.meteor.utils import build_meteor_context

	devmode = check_dev_mode()
	context.developer_mode = devmode
	context.jquery_include = jquery_include()

	doc = frappe.get_doc("Fluorine Reactivity")

	#Meteor
	build_meteor_context(context, devmode, whatfor)
	context.meteor_web = True
	context.custom_template = doc.fluorine_base_template

	return fluorine_build_context(context, whatfor), devmode


def get_app_pages(context):

	from fluorine.utils.module import get_app_context

	def get_frappe_context(context):

		app = "frappe"
		app_path = frappe.get_app_path(app)
		path = os.path.join(app_path, "templates", "pages")
		ret = get_app_context(context, path, app, app_path, "desk.py")
		return ret

	context, devmode = prepare_common_page_context(context, "meteor_app")

	fcontext = get_frappe_context(context)

	if devmode:
		include_js = fcontext.get("include_js",[])
		include_css = fcontext.get("include_css", [])
		#TODO ver se é preciso remove tb o css gerado
		try:
			include_js.remove("/assets/js/meteor_app.js")
		except:
			pass
		finally:
			fcontext["include_js"] = include_js + context.meteor_package_js
			fcontext["include_css"] = include_css + context.meteor_package_css

	#fcontext["include_js"] = context.meteor_package_js + fcontext.get("include_js",[])
	#fcontext["include_css"] = context.meteor_package_css + fcontext.get("include_css", [])

	context.update(fcontext)

	return context


def get_web_pages(context):

	context, devmode = prepare_common_page_context(context, "meteor_web")

	context.meteor_web_include_css = frappe.get_hooks("meteor_web_include_css")
	context.meteor_web_include_js = frappe.get_hooks("meteor_web_include_js")

	if devmode:
		#TODO ver se é preciso remove tb o css gerado
		try:
			context.meteor_web_include_js.remove("/assets/fluorine/js/meteor_web.js")
		except:
			pass

	print "frappe.local.request 6 url {} url_root {} host {} scheme {} host_url {}".format(frappe.local.request.url, frappe.local.request.url_root, frappe.local.request.host, frappe.local.request.scheme,\
																				frappe.local.request.host_url)

	return context


def fluorine_build_context(context, whatfor):

	from file import make_all_files_with_symlink, empty_directory, get_path_reactivity#, save_js_file
	from reactivity import list_ignores
	from fluorine.utils.meteor.utils import make_meteor_props

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
	devmode = context.developer_mode
	refresh = False
	space_compile = True
	apps = frappe.get_installed_apps()#[::-1]

	frappe.local.meteor_ignores = list_ignores

	if devmode:
		frefresh = os.path.join(path_reactivity, "common_site_config.json")
		#refresh = True
		if os.path.exists(frefresh):
			f = frappe.get_file_json(frefresh)
			meteor = f.get("meteor_folder", {})
			refresh = meteor.get("folder_refresh", True)
			space_compile = meteor.get("compile", True)

	#if refresh or space_compile or whatfor == "meteor_app":
	process_react_templates(context, apps[::-1], whatfor)

	#if refresh:
	fluorine_publicjs_dst_path = os.path.join(path_reactivity, whatfor)
	empty_directory(fluorine_publicjs_dst_path, ignore=(".meteor",))
	print "context files_to_add 2 {}".format(context.files_to_add)
	make_all_files_with_symlink(fluorine_publicjs_dst_path, whatfor, custom_pattern=["*.xhtml"])

	make_meteor_props(context, whatfor)

	return context

def process_react_templates(context, apps, whatfor):

	from fluorine.utils.fhooks import get_xhtml_context
	from react_file_loader import read_client_xhtml_files, get_custom_pattern
	from fluorine.utils.fhooks import get_extra_context_func, get_general_context
	from fluorine.utils.meteor.utils import compile_spacebars_templates
	from reactivity import extras_context_methods
	#from fjinja import process_hooks_apps, process_hooks_meteor_templates
	#first installed app first
	#list_apps_remove = process_hooks_apps(apps)
	#list_meteor_files_add, list_meteor_files_remove = process_hooks_meteor_templates(apps, "fluorine_files_templates")
	#list_meteor_files_folders_add, list_meteor_files_folders_remove = process_hooks_meteor_templates(apps, "fluorine_files_folders")
	spacebars_templates = {}
	#spacebars_context = []

	#ignore = {"templates":list_meteor_files_remove, "files_folders":list_meteor_files_folders_remove}
	list_apps_remove = frappe.local.meteor_ignores.get("remove", {}).get("apps")

	custom_pattern = get_custom_pattern(whatfor, custom_pattern=None)
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
					#if not check_in_files_remove_list(app, spacebars_template_path, list_meteor_files_remove):
					addto_meteor_templates_list(spacebars_template_path)
						#spacebars_context.append(frappe._dict({"file_path": file_path, "file_name": file_name, "app_path": pathname, "appname": app, "whatfor": whatfor }))

	#get the context from all the python files of templates
	get_xhtml_context(context)

	#get all the templates to use
	#mtl = get_meteor_template_list()
	#and compile them all
	#out = compile_jinja_templates(mtl, context, whatfor)
	#TODO get from hooks
	#from the first app to the last installed to override the changes made by first installed apps
	get_extra_context_func(context, apps[::-1], extras_context_methods)

	get_general_context(context, apps[::-1], whatfor)

	out = compile_jinja_templates(context, whatfor)

	spacebars_templates.update(out)
	#only compile if meteor_app or meteor_frappe
	if spacebars_templates:# and whatfor in ("meteor_app", "meteor_frappe"):
		compiled_spacebars_js = compile_spacebars_templates(spacebars_templates)
		arr = compiled_spacebars_js.split("__templates__\n")
		arr.insert(0, "(function(){\n")
		arr.append("})();\n")
		context.compiled_spacebars_js = arr


def addto_meteor_templates_list(template_path):
	from fluorine.utils.fhooks import get_xhtml_files_to_add_remove

	if not frappe.local.meteor_map_templates.get(template_path, None):# and template_path not in frappe.local.templates_referenced:
		template = fluorine_get_fenv().get_template(template_path)
		frappe.local.meteor_map_templates.get(template_path).update({"template_obj": template})
		#TODO get the context from file of the template...pass the context, the template object and template_path
		#TODO with template_path and frappe.local.meteor_map_templates.get(template_path) get refs if needed to pass macro template object
		#TODO get the context from frappe.local.context!
		get_xhtml_files_to_add_remove(frappe.local.context, template_path)
		print "calling render template from addto_meteor_templates_list {}".format(template_path)
		return True
	return False
	#return fluorine_get_fenv().addto_meteor_templates_list(template_path)


