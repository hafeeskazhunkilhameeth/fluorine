# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'

import frappe

meteor_config = None

file_map_site = None

making_production = False
#frappe.local("making_production")
#frappe.local.making_production = False
#assets_public_path = "/assets/fluorine/js/react"
meteor_runtime_config_path = ""

APPS = None

meteor_web_app = "meteor_web"
meteor_desk_app = "meteor_app"
whatfor_all = (meteor_web_app, meteor_desk_app)

def is_making_production():
	return making_production

def set_making_production(val):
	global making_production
	making_production = val


def get_meteor_final_name(site, whatfor):

	sitename = site.replace(".", "_")
	final = whatfor.replace("meteor", "final")

	return "%s_%s" % (final, sitename)

def get_meteor_runtime_config_path(whatfor, real=False):
	import os

	if real:
		app_path = frappe.get_app_path("fluorine")
		public_app_folder = os.path.join(app_path, "public", whatfor)
		return os.path.join(public_app_folder, "meteor_runtime_config.js")
	else:
		return os.path.join("/assets", "fluorine", whatfor, "meteor_runtime_config.js")


def get_attr_from_json(attrs, _json_):
	"""
	Example:
	{
		meteor_web:{
			host:'http://localhost',
			port: 3070
		}
	}

	To get attribute port:
		attrs = ["meteor_web", "port"]
	"""
	tmp_attr = _json_

	for attr in attrs:
		tmp_attr = tmp_attr.get(attr)
		if tmp_attr == None:
			tmp_attr = {}

	return tmp_attr


def get_frappe_apps_path():
	import os

	return os.path.normpath(os.path.join(os.path.realpath("."), "..", "apps"))

def remove_from_hooks(hooks, stop=False):

	base_template = "templates/fluorine_base.html"
	#meteor_js = "/assets/js/meteor_app.min.js"
	#meteor_css = "/assets/css/meteor_app.css"
	home_page = "fluorine_home"

	if isinstance(hooks, dict):
		base = hooks.get("base_template")
		home = hooks.get("home_page")
		#hjs = hooks.get("app_include_js")
		#hcss = hooks.get("app_include_css")

		#if hjs and meteor_js in hjs:
		#	hjs.remove(meteor_js)
		#if hcss and meteor_css in hcss:
		#	hcss.remove(meteor_css)

		if stop:
			if base_template == base:
				base.remove(base_template)

			if home_page == home:
				home.remove(home_page)

	else:
		#if meteor_js in hooks:
		#	hooks.remove(meteor_js)
		#if meteor_css in hooks:
		#	hooks.remove(meteor_css)
		if stop:
			if base_template in hooks:
				hooks.remove(base_template)
			if home_page in hooks:
				hooks.remove(home_page)


def fluor_get_hooks(hook=None, default=None, app_name=None):
	hooks = frappe_get_hooks(hook=hook, default=default, app_name=app_name)
	if meteor_config.get("stop"):
		remove_from_hooks(hooks, stop=True)
	else:
		remove_from_hooks(hooks)
	return hooks


def fluor_get_context(path):

	context = frappe_get_context(path)
	if path == "desk":
		from fluorine.templates.pages import mdesk
		context = mdesk.get_context(context)

	return context

#Get all apps installed and not installed. This away we can have multiple sites and fluorine installed in only one site.
def get_installed_apps():
	import re

	global APPS

	if APPS != None:
		return APPS

	try:
		with open("apps.txt") as f:
			APPS = re.sub(r" +", "", f.read()).split()
	except IOError:
		APPS = frappe.get_installed_apps()

	return APPS


def get_encoding():
	return "utf-8"


def check_dev_mode():

	if not meteor_config:
		get_meteor_configuration_file()

	if meteor_config:
		devmode = meteor_config.get("developer_mode") or 0
		if devmode:
			return True


	return False


def jquery_include():
	return True

def get_Frappe_Version(version=None):
	import semantic_version as sv

	version = version or frappe.__version__
	return sv.Version(version)


def get_meteor_configuration_file():
	from fluorine.utils.file import get_common_config_file_json

	global meteor_config

	meteor_config = get_common_config_file_json()

	return meteor_config



frappe_get_hooks = None

def patch_hooks():
	global frappe_get_hooks
	frappe_get_hooks = frappe.get_hooks
	frappe.get_hooks = fluor_get_hooks


frappe_get_context = None

def patch_frappe_get_context():
	import frappe.website.context

	global frappe_get_context
	frappe_get_context = frappe.website.context.get_context
	frappe.website.context.get_context = fluor_get_context


get_installed_apps()

def prepare_environment():

	if frappe_get_hooks == None:
		patch_hooks()
	else:
		print "error hooks"

	if not meteor_config.get("stop") or is_making_production():
		#PATCH get_context
		if frappe_get_context == None:
			patch_frappe_get_context()
		else:
			print "error get_context"

def is_open_port(ip="127.0.0.1", port=3070):
	import socket
	is_open = False
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	result = sock.connect_ex((ip,port))
	if result == 0:
		is_open = True
	sock.close()
	return is_open


def update_file_map_site(fms):
	import os
	from fluorine.utils.file import get_path_reactivity, save_js_file
	from fluorine.utils import get_file_map_site

	if not file_map_site:
		get_file_map_site()

	global file_map_site

	file_map_site.update(fms)
	path_reactivity = get_path_reactivity()
	config_file_path = os.path.join(path_reactivity, "file_map_site.json")

	save_js_file(config_file_path, file_map_site)


def get_file_map_site():
	import os

	if file_map_site:
		return file_map_site

	global file_map_site

	frappe_module = os.path.dirname(frappe.__file__)
	path_apps = os.path.realpath(os.path.join(frappe_module, "..", ".."))
	path_reactivity = os.path.join(path_apps, "reactivity")

	file_map_site_json = os.path.join(path_reactivity, "file_map_site.json")
	if os.path.exists(file_map_site_json):
		file_map_site = frappe.get_file_json(file_map_site_json)
	else:
		file_map_site = {}

	return file_map_site


if check_dev_mode():
	#PATCH HOOKS
	prepare_environment()
	import reactivity
else:
	get_file_map_site()