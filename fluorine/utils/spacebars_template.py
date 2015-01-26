from __future__ import unicode_literals
__author__ = 'luissaguas'


from frappe.website.utils import scrub_relative_urls
#from frappe.website.template import render_blocks
from jinja2.utils import concat
from jinja2 import meta
import frappe
import os, re
from frappe.utils.jinja import set_filters, get_allowed_functions_for_jenv
#from frappe.website.context import get_context
#from fluorine.utils.packages_path import get_package_path
from fjinja import MyFileSystemLoader
from jinja2 import ChoiceLoader

#import react_file_loader
from react_file_loader import get_js_to_client

#fenv = frappe.local("fenv")
#floader = frappe.local("floader")

def fluorine_get_fenv():

	from jinja2 import Environment, DebugUndefined

	fenv = Environment(loader = fluorine_get_floader(),
		undefined=DebugUndefined)
	set_filters(fenv)

	fenv.globals.update(get_allowed_functions_for_jenv())

	frappe.local.fenv = fenv

	return frappe.local.fenv


def fluorine_get_floader():

	if not frappe.local.floader:

		path = os.path.normpath(os.path.join(os.getcwd(), "..")) + "/apps"

		apps = frappe.get_installed_apps()[::-1]

		fluor_loader = [MyFileSystemLoader(apps, path)]

		print "fluorine_get_floader {}".format(path)
		frappe.local.floader = ChoiceLoader(fluor_loader)

	return frappe.local.floader


def fluorine_get_template(path):
	return fluorine_get_fenv().get_template(path)


def fluorine_render_blocks(context):
	"""returns a dict of block name and its rendered content"""
	#import inspect
	#print 'I am f1 and was called by', inspect.currentframe().f_back.f_code.co_name
	out = {}
	#env = frappe.get_jenv()
	env = fluorine_get_fenv()

	def _render_blocks(template_path):
		#print "template_paths {}".format(template_path)
		source = frappe.local.floader.get_source(frappe.local.fenv, template_path)[0]
		for referenced_template_path in meta.find_referenced_templates(env.parse(source)):
			if referenced_template_path:
				_render_blocks(referenced_template_path)

		template = fluorine_get_template(template_path)
		for block, render in template.blocks.items():
			make_heritage(block, context)
			out[block] = scrub_relative_urls(concat(render(template.new_context(context))))

	_render_blocks(context["spacebars_template"])

	return out


def fluorine_build_context(context):

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
							#print "app_path {}".format(controller_path + ".py")
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

	hooks_js = get_js_to_client()

	context.compiled_spacebars_js = arr

	context.update(hooks_js)
	#print "A compilar templates \n{}".format(context.compiled_spacebars_js)

	return context


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
	subprocess.Popen(["node", path + "/compile_spacebars_js.js", path + "/fluorine_program.json"], cwd=path, shell=False, close_fds=True)
	c = zerorpc.Client()
	c.connect("tcp://127.0.0.1:4242")
	#for key, val in out.items():
	compiled_templates = c.compile(templates)

	return compiled_templates
#print "In override spacebars"
#frappe.website.context.build_context = fluorine_spacebars_build_context
#frappe.website.render.build_page = fluorine_spacebars_build_page
#frappe.website.context.__dict__["get_context"] = fluorine_spacebars_get_context

#print "frappe.website.context.get_context {}".format(frappe.website.context.__dict__["get_context"])