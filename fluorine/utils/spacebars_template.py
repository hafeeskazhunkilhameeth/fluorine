from __future__ import unicode_literals
__author__ = 'luissaguas'


from frappe.website.utils import scrub_relative_urls
#from frappe.website.template import render_blocks
from jinja2.utils import concat
from jinja2 import meta
import frappe
from frappe.utils.jinja import set_filters, get_allowed_functions_for_jenv
#from frappe.website.context import get_context
#from fluorine.utils.packages_path import get_package_path
from fjinja import MyFileSystemLoader
from jinja2 import ChoiceLoader
import hashlib, json, os, re
from collections import OrderedDict


def fluorine_get_fenv():

	from jinja2 import DebugUndefined
	from fluorine.utils.fjinja import MyEnvironment

	fenv = MyEnvironment(loader = fluorine_get_floader(),
		undefined=DebugUndefined)
	set_filters(fenv)

	fenv.globals.update(get_allowed_functions_for_jenv())

	frappe.local.fenv = fenv

	return frappe.local.fenv


def fluorine_get_floader():

	from fluorine.utils.fjinja import MyChoiceLoader

	if not frappe.local.floader:

		path = os.path.normpath(os.path.join(os.getcwd(), "..")) + "/apps"

		#first template to load is the last installed
		#So, we can replace the oldest template by new one with the same name
		apps = frappe.get_installed_apps()[::-1]
		m = MyFileSystemLoader(apps, path)
		fluor_loader = [m]

		frappe.local.floader = MyChoiceLoader(fluor_loader)

	return frappe.local.floader


def fluorine_get_template(path):
	return fluorine_get_fenv().addto_meteor_templates_list(path)

"""
def fluorine_render_blocks(context, whatfor):
	env = fluorine_get_fenv()

	def _render_blocks(template_path):
		#print "template_paths {}".format(template_path)
		#get the first template. The last installed in this case
		source = frappe.local.floader.get_source(frappe.local.fenv, template_path)[0]
		for referenced_template_path in meta.find_referenced_templates(env.parse(source)):
			if referenced_template_path:
				_render_blocks(referenced_template_path)

		#fluorine_get_template(template_path)
	fluorine_get_template(context["spacebars_template"])
	#_render_blocks(context["spacebars_template"])
"""

def compile_jinja_templates(mtl, context):
	from file import save_file, remove_file

	out = {}

	for l in mtl:
		template = l.get("template")
		dstPath = template.filename[:-6] + ".html"
		content = scrub_relative_urls(concat(template.render(template.new_context(context))))
		if content:
			save_file(dstPath, content)
			items = template.blocks.items()
			for block, render in items:
				if block.startswith("spacebars"):
					block = block[10:]
					#make_heritage(block, context)
					out[block] = scrub_relative_urls(concat(render(template.new_context(context))))
		else:
			remove_file(dstPath)

	return out


"""
def fluorine_render_blocks(context, whatfor):
	#import inspect
	#print 'I am f1 and was called by', inspect.currentframe().f_back.f_code.co_name
	out = {}
	#env = frappe.get_jenv()
	env = fluorine_get_fenv()

	def _render_blocks(template_path):
		#print "template_paths {}".format(template_path)
		#get the first template. The last installed in this case
		source = frappe.local.floader.get_source(frappe.local.fenv, template_path)[0]
		for referenced_template_path in meta.find_referenced_templates(env.parse(source)):
			if referenced_template_path:
				_render_blocks(referenced_template_path)

		template = fluorine_get_template(template_path)
		items = template.blocks.items()
		#if not items:
		from file import save_file
		#from shutil import copyfile
		dstPath = template.filename[:-6] + ".html"
		content = scrub_relative_urls(concat(template.render(template.new_context(context))))
		save_file(dstPath, content)
		#return
			#copyfile(template.filename, dst)
			#out[block] = scrub_relative_urls(concat(render(template.new_context(context))))
		#if whatfor in ("meteor_app", "meteor_frappe"):
		for block, render in items:
			if block.startswith("spacebars"):
				block = block[10:]
				make_heritage(block, context)
				out[block] = scrub_relative_urls(concat(render(template.new_context(context))))

	_render_blocks(context["spacebars_template"])

	return out
"""

"""
def fluorine_build_context3(context, whatfor):

	from react_file_loader import read_client_files
	from . import check_dev_mode
	#print "befores fluorine_spacebars_build_context path {}".format(path)
	#if path.find(".") == -1 and not path == "404":
		#print "news fluorine_spacebars_build_context path {}".format(path)
	#fl = frappe.get_doc("Fluorine Reactivity")
	#if fl.fluorine_base_template and fl.fluorine_base_template.lower() != "default":
	#	app_base_template = fl.fluorine_base_template
	#else:
	#	app_base_template = frappe.get_hooks("base_template")
	#	if not app_base_template:
	#		app_base_template = "templates/base.html"

	#if context.base_template_path == app_base_template:

		#if not context.spacebars_data:
		#	context.spacebars_data = {}
		#print "context data path in override {}".format(context.data)
		#context.update(context.data or {})
	if not check_dev_mode():
		return

	apps = frappe.get_installed_apps()#[::-1]
	#apps.remove("fluorine")
	name_templates = []
	spacebars_templates = {}

	for app in apps:
		#print "app {}".format(app)
		pathname = frappe.get_app_path(app)#get_package_path(app, "", "")
		path = os.path.join(pathname, "templates", "react")
		if os.path.exists(path):
			files = read_client_files(path, whatfor, extension="html")
			for file in files:
				#l = prepare_files(files)
				for obj in reversed(file):
					#print "app is {} path is {}".format(app, os.path.join(os.path.relpath(root, pathname), file))
					#print(os.path.join(root, file[:-5] + ".py"))
					#filename = os.path.join(root, file)
					file_path = obj.get("path")
					py_path = file_path[:-5]
					root = file_path[:-len(obj.get("name"))]
					context.spacebars_template = os.path.join(os.path.relpath(root, pathname), obj.get("name"))
					if os.path.exists(os.path.join(root, py_path + ".py")):
						controller_path = os.path.join(app, context.spacebars_template).replace(os.path.sep, ".")[:-5]
						print "app_path 4 {} root {} context.spacebars_template {}".format(controller_path + ".py", root, context.spacebars_template)
						module = frappe.get_module(controller_path)
						if module:
							if hasattr(module, "get_context"):
								ret = module.get_context(context)
								if ret:
									context.update(ret)
							if hasattr(module, "get_children"):
								context.get_children = module.get_children
					#heritage
					out = fluorine_render_blocks(context)
					#context.spacebars_data.update(out)
					print "out {}".format(out)
					#print "context teste123 {} out {}".format(context.teste123, out.get("teste123", None))
					#print frappe.utils.pprint_dict(out)
					spacebars_templates.update(out)
					#for name in out:
					#	name_templates.append(name)
					context.update(out)
						#print "new spacebars_data {}".format(context)
	#context.data.update(context.spacebars_data or {})
#print "In fluorine_spacebars_build_context"
	if spacebars_templates:
		compiled_spacebars_js = compile_spacebars_templates(spacebars_templates)
		arr = compiled_spacebars_js.split("__templates__\n")
		arr.insert(0, "(function(){\n")
		arr.append("})();\n")
		context.compiled_spacebars_js = arr

	fluorine_publicjs_dst_path = os.path.join(frappe.get_app_path("fluorine"), "public", "js", "react")
	hooks_js = get_js_to_client(fluorine_publicjs_dst_path, whatfor)

	context.update(hooks_js)
	#print "A compilar templates \n{}".format(context.compiled_spacebars_js)

	return context
"""

def make_auto_update_version(path, meteorRelease, root_url, root_prefix, appId=None):
	from fluorine.utils import file

	runtimeCfg = OrderedDict()
	runtimeCfg["meteorRelease"] = meteorRelease#"METEOR@1.1.0.2"
	runtimeCfg["ROOT_URL"] = root_url#"http://localhost"
	runtimeCfg["ROOT_URL_PATH_PREFIX"] = root_prefix
	if appId:
		runtimeCfg["appId"] = appId
	#runtimeCfg["appId"] = "1uo02wweyt6o11xsntyy"
	manifest = file.read(path)
	manifest = json.loads(manifest).get("manifest")
	autoupdateVersion, autoupdateVersionRefresh, frappe_manifest = meteor_hash_version(manifest, runtimeCfg)
	print "sha1 digest {} {}".format(autoupdateVersion, autoupdateVersionRefresh)
	#runtimeCfg["autoupdateVersion"] = autoupdateVersion
	#autoupdateVersionRefresh = meteor_hash_version(manifest, runtimeCfg, css=True)
	#print "sha1 digest ", autoupdateVersionRefresh
	return autoupdateVersion, autoupdateVersionRefresh, frappe_manifest


def meteor_hash_version(manifest, runtimeCfg):
	sh1 = hashlib.sha1()
	sh2 = hashlib.sha1()
	frappe_manifest = []
	#runtimeCfg = {"meteorRelease": meteorRelease,
	#            "ROOT_URL": 'http://localhost',
	#             "ROOT_URL_PATH_PREFIX": ""}

	#runtimeCfg = """{'meteorRelease': %s,'ROOT_URL': 'http://localhost','ROOT_URL_PATH_PREFIX': ''}""" % meteorRelease
	rt = json.dumps(runtimeCfg).replace(" ", "").encode('utf8')
	print "json.dumps ", rt
	sh1.update(rt)
	sh2.update(rt)
	for m in manifest:
		if m.get("where") == "client" or m.get("where") == "internal":
			if m.get("where") == "client":
				frappe_manifest.append(m.get("url"))
			if m.get("type") == "css":
				sh2.update(m.get("path"))
				sh2.update(m.get("hash"))
				continue
			sh1.update(m.get("path"))
			sh1.update(m.get("hash"))

	return sh1.hexdigest(), sh2.hexdigest(), frappe_manifest


def fluorine_build_context(context, whatfor):

	from file import make_all_files_with_symlink, empty_directory, get_path_reactivity#, save_js_file

	path_reactivity = get_path_reactivity()
	devmode = context.developer_mode
	refresh = False
	space_compile = True

	if devmode:
		frefresh = os.path.join(path_reactivity, "common_site_config.json")
		refresh = True
		if os.path.exists(frefresh):
			f = frappe.get_file_json(frefresh)
			meteor = f.get("meteor_folder", {})
			refresh = meteor.get("folder_refresh", True)
			space_compile = meteor.get("compile", True)

	if refresh or space_compile or whatfor == "meteor_app":
		process_react_templates(context, whatfor)

	if refresh:
		fluorine_publicjs_dst_path = os.path.join(path_reactivity, whatfor)
		empty_directory(fluorine_publicjs_dst_path, ignore=(".meteor",))
		make_all_files_with_symlink(fluorine_publicjs_dst_path, whatfor, ignore=None, custom_pattern=["*.xhtml"])

	make_meteor_props(context, whatfor)

	return context

def process_react_templates(context, whatfor):

	from react_file_loader import read_client_files
	from fjinja import process_hooks_apps
	#first installed app first
	apps = frappe.get_installed_apps()#[::-1]
	list_apps_remove = process_hooks_apps(apps)
	spacebars_templates = {}
	spacebars_context = []

	for app in apps:
		if app in list_apps_remove:
			continue
		pathname = frappe.get_app_path(app)
		path = os.path.join(pathname, "templates", "react")
		if os.path.exists(path):
			files = read_client_files(path, whatfor, extension="xhtml")
			for f in files:
				for obj in reversed(f):
					file_path = obj.get("path")
					file_name = obj.get("name")
					root = file_path[:-len(file_name)]
					spacebars_template_path = os.path.join(os.path.relpath(root, pathname), file_name)
					if addto_meteor_templates_list(spacebars_template_path):
						spacebars_context.append(frappe._dict({"file_path": file_path, "file_name": file_name, "app_path": pathname, "appname": app, "whatfor": whatfor }))

	#get the context from all the python files of templates
	get_spacebars_context(context, spacebars_context)
	#get all the templates to use
	mtl = get_meteor_template_list()
	#and compile them all
	out = compile_jinja_templates(mtl, context)
	#only compile if meteor_app or meteor_frappe
	if spacebars_templates and whatfor in ("meteor_app", "meteor_frappe"):
		compiled_spacebars_js = compile_spacebars_templates(spacebars_templates)
		arr = compiled_spacebars_js.split("__templates__\n")
		arr.insert(0, "(function(){\n")
		arr.append("})();\n")
		context.compiled_spacebars_js = arr


def addto_meteor_templates_list(template_path):
	fluorine_get_fenv().addto_meteor_templates_list(template_path)

def get_meteor_template_list():
	return fluorine_get_fenv().get_meteor_template_list()

"""
def compile_spacebar_templates(context, whatfor):

	from react_file_loader import read_client_files
	from file import save_file

	#first installed app first
	apps = frappe.get_installed_apps()#[::-1]

	spacebars_templates = {}

	for app in apps:

		pathname = frappe.get_app_path(app)
		path = os.path.join(pathname, "templates", "react")
		if os.path.exists(path):
			files = read_client_files(path, whatfor, extension="xhtml")
			for f in files:
				for obj in reversed(f):
					file_path = obj.get("path")
					out = render_spacebar_html(context, file_path, obj.get("name"), pathname, app, whatfor)
					if whatfor in ("meteor_app", "meteor_frappe"):
						spacebars_templates.update(out)
						context.update(out)
					#dstPath = os.path.join(obj.get("filePath"), obj.get("fileName") + ".html")
					#content = ""
					#for k in out.keys():
					#	content = content + out[k] + "\n"
					#if content:
					#	save_file(dstPath, content)

	#only compile if meteor_app or meteor_frappe
	if spacebars_templates and whatfor in ("meteor_app", "meteor_frappe"):
		compiled_spacebars_js = compile_spacebars_templates(spacebars_templates)
		arr = compiled_spacebars_js.split("__templates__\n")
		arr.insert(0, "(function(){\n")
		arr.append("})();\n")
		context.compiled_spacebars_js = arr
"""

def make_meteor_props(context, whatfor):
	from file import get_path_reactivity, get_meteor_release

	path_reactivity = get_path_reactivity()
	progarm_path = os.path.join(path_reactivity, whatfor, ".meteor/local/build/programs/web.browser/program.json")
	config_path = os.path.join(path_reactivity, whatfor, ".meteor/local/build/programs/server/config.json")
	context.meteorRelease = get_meteor_release(config_path)
	appId = get_meteor_appId(os.path.join(path_reactivity, whatfor, ".meteor/.id"))
	context.appId = appId.replace(" ","").replace("\n","")

	context.meteor_autoupdate_version, context.meteor_autoupdate_version_freshable, manifest =\
				make_auto_update_version(progarm_path, context.meteorRelease, context.meteor_root_url, context.meteor_url_path_prefix, appId=context.appId)

	context.meteor_package_js = manifest
	context.meteor_runtime_config = True

def get_meteor_appId(path):
	appid = None
	with open(path, "r") as f:
		for line in f:
			if line.startswith("#") or line.startswith("\n"):
				continue
			appid = line
			break
	print "appId {}".format(appid)
	return appid

"""
def get_page(url, context):
	from bs4 import BeautifulSoup
	import urllib2, json, ast

	scripts = []
	html = BeautifulSoup(urllib2.urlopen(url).read())
	for link in html.find_all('script'):
		src = link.get("src")
		if src:
			scripts.append(src)
		else:
			#uq = urllib2.unquote(link.string)
			#mc = urllib2.unquote(link.string)
			#u = mc.split("(")[2][:-3]
			#mc = urllib2.unquote(str(link.string))

			#get __meteor_runtime_config__ string and convert to object and unquote
			c = urllib2.unquote(ast.literal_eval(link.string.split("(")[2][:-3]))
			meteor_config = json.loads(c)
			meteor_config["ROOT_URL"] = url
			meteor_config["DDP_DEFAULT_CONNECTION_URL"] = url
			context.meteor_runtime_config = json.dumps(meteor_config)
			#print "scripts meteor {}".format(json.loads(c).get("ROOT_URL"))

	return scripts
"""

def get_spacebars_context(context, spacebar_context):

	for obj in spacebar_context:
		py_path = obj.file_path[:-5]
		root = obj.file_path[:-len(obj.file_name)]
		context.spacebars_template = os.path.join(os.path.relpath(root, obj.app_path), obj.file_name)
		if os.path.exists(os.path.join(root, py_path + ".py")):
			controller_path = os.path.join(obj.appname, context.spacebars_template).replace(os.path.sep, ".")[:-5]
			print "app_path 4 {} root {} context.spacebars_template {}".format(controller_path + ".py", root, context.spacebars_template)
			module = frappe.get_module(controller_path)
			if module:
				if hasattr(module, "get_context"):
					ret = module.get_context(context)
					if ret:
						context.update(ret)
				if hasattr(module, "get_children"):
					context.get_children = module.get_children


"""
def render_spacebar_html(context, file_path, file_name, app_path, appname, whatfor):

	py_path = file_path[:-5]
	root = file_path[:-len(file_name)]
	context.spacebars_template = os.path.join(os.path.relpath(root, app_path), file_name)
	if os.path.exists(os.path.join(root, py_path + ".py")):
		controller_path = os.path.join(appname, context.spacebars_template).replace(os.path.sep, ".")[:-5]
		print "app_path 4 {} root {} context.spacebars_template {}".format(controller_path + ".py", root, context.spacebars_template)
		module = frappe.get_module(controller_path)
		if module:
			if hasattr(module, "get_context"):
				ret = module.get_context(context)
				if ret:
					context.update(ret)
			if hasattr(module, "get_children"):
				context.get_children = module.get_children
	#heritage
	out = fluorine_render_blocks(context, whatfor=whatfor)

	return out
"""

"""
def get_html_to_client(whatfor):
	from react_file_loader import copy_client_files, read_client_files, remove_directory

	fluorine_temp_path = os.path.join(frappe.get_app_path("fluorine"), "templates", "react", "temp")
	frappe.create_folder(fluorine_temp_path)
	copy_client_files(fluorine_temp_path, extension="html")
	files = read_client_files(fluorine_temp_path, whatfor, extension="html")

	hooks_js = move_to_public(files, whatfor)

	remove_directory(fluorine_temp_path)

	return hooks_js


def move_to_public(files, whatfor):
	from fluorine.utils import assets_public_path
	hooks_js = {"client_hooks_html":[]}
	fpath = assets_public_path

	for f in files:
		hooks_js["client_hooks_html"].extend(prepare_files(f, fpath))

	return hooks_js


def prepare_files(files):
	hooks = []
	for f in reversed(files):
		hooks.append(f)

	return hooks
"""

"""
def fluorine_build_context2(context, whatfor):

	#print "befores fluorine_spacebars_build_context path {}".format(path)
	#if path.find(".") == -1 and not path == "404":
		#print "news fluorine_spacebars_build_context path {}".format(path)
	#fl = frappe.get_doc("Fluorine Reactivity")
	#if fl.fluorine_base_template and fl.fluorine_base_template.lower() != "default":
	#	app_base_template = fl.fluorine_base_template
	#else:
	#	app_base_template = frappe.get_hooks("base_template")
	#	if not app_base_template:
	#		app_base_template = "templates/base.html"

	#if context.base_template_path == app_base_template:

		#if not context.spacebars_data:
		#	context.spacebars_data = {}
		#print "context data path in override {}".format(context.data)
		#context.update(context.data or {})
	apps = frappe.get_installed_apps()#[::-1]
	#apps.remove("fluorine")
	name_templates = []
	spacebars_templates = {}

	for app in apps:
		#print "app {}".format(app)
		pathname = frappe.get_app_path(app)#get_package_path(app, "", "")
		if pathname:
			for root, dirs, files in os.walk(os.path.join(pathname, "templates", "react")):
				for file in files:
					if file.endswith(".html"):
						#print "app is {} path is {}".format(app, os.path.join(os.path.relpath(root, pathname), file))
						#print(os.path.join(root, file[:-5] + ".py"))
						#filename = os.path.join(root, file)
						context.spacebars_template = os.path.join(os.path.relpath(root, pathname), file)
						if os.path.exists(os.path.join(root, file[:-5] + ".py")):
							controller_path = os.path.join(app, context.spacebars_template).replace(os.path.sep, ".")[:-5]
							print "app_path 3 {} root {} context.spacebars_template {}".format(controller_path + ".py", root, context.spacebars_template)
							module = frappe.get_module(controller_path)
							if module:
								if hasattr(module, "get_context"):
									ret = module.get_context(context)
									if ret:
										context.update(ret)
								if hasattr(module, "get_children"):
									context.get_children = module.get_children
						#heritage
						out = fluorine_render_blocks(context)
						#context.spacebars_data.update(out)
						print "out {}".format(out)
						#print "context teste123 {} out {}".format(context.teste123, out.get("teste123", None))
						#print frappe.utils.pprint_dict(out)
						spacebars_templates.update(out)
						#for name in out:
						#	name_templates.append(name)
						context.update(out)
						#print "new spacebars_data {}".format(context)
	#context.data.update(context.spacebars_data or {})
#print "In fluorine_spacebars_build_context"
	compiled_spacebars_js = compile_spacebars_templates(spacebars_templates)
	arr = compiled_spacebars_js.split("__templates__\n")
	arr.insert(0, "(function(){\n")
	arr.append("})();\n")

	hooks_js = get_js_to_client(whatfor)

	context.compiled_spacebars_js = arr

	context.update(hooks_js)
	#print "A compilar templates \n{}".format(context.compiled_spacebars_js)

	return context
"""

def make_heritage(block, context):
	#for block, render in out.items():
	#in_first_block_render, data_first_block_render, outer_first_block_render = context.spacebars_data.get(block, None), context.data.get(block, None),\
	#context.block
	in_first_block_render = context.get(block, None)
	#print frappe.utils.pprint_dict(context)
	#print "make_heritages  template {} data.path {}".format(context["template"], context.get("path"))
	if in_first_block_render:
		contents = re.sub("<template name=['\"](.+?)['\"](.*?)>(.*?)</template>", template_replace, in_first_block_render, flags=re.S)
		#print "my new context block {}".format(context.get(block, None))
		context["_" + block] = contents
	#if data_first_block_render:
	#	context["__" + block] = data_first_block_render
	#if outer_first_block_render:
	#	context["___" + block] = outer_first_block_render


def template_replace(m):
	content = m.group(3)
	return content


def compile_spacebars_templates(context):
	import zerorpc
	import subprocess
	from fluorine.utils.file import get_path_reactivity

	templates = []
	for name, template in context.items():
		#template = context.get(name, "")
		m = re.match(r".*?<template\s+.*?>(.*?)</template>", template, re.S)
		if m:
			print "m.group(1) name {} group(1) {}".format(name, m.group(1))
			templates.append({"name":name, "code": m.group(1)})

	path = get_path_reactivity()
	print "path in compile_spacebars_templates {}".format(os.path.join(path, "compile_spacebars_js.js"))
	node = subprocess.Popen(["node", os.path.join(path, "server/compile_spacebars_js.js"), os.path.join(path, "fluorine_program.json")], cwd=os.path.join(path, "server"), shell=False, close_fds=True)
	c = zerorpc.Client()
	c.connect("tcp://127.0.0.1:4242")
	#for key, val in out.items():
	compiled_templates = c.compile(templates)
	node.kill()

	return compiled_templates
#print "In override spacebars"
#frappe.website.context.build_context = fluorine_spacebars_build_context
#frappe.website.render.build_page = fluorine_spacebars_build_page
#frappe.website.context.__dict__["get_context"] = fluorine_spacebars_get_context

#print "frappe.website.context.get_context {}".format(frappe.website.context.__dict__["get_context"])