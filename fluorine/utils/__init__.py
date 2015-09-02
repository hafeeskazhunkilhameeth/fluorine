# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'

import frappe

meteor_config = None

frappe.local("making_production")
frappe.local.making_production = False
#assets_public_path = "/assets/fluorine/js/react"
meteor_runtime_config_path = ""

APPS = None

meteor_web_app = "meteor_web"
meteor_desk_app = "meteor_app"
whatfor_all = (meteor_web_app, meteor_desk_app)

def get_meteor_runtime_config_path(whatfor, real=False):
	import os

	if real:
		app_path = frappe.get_app_path("fluorine")
		public_app_folder = os.path.join(app_path, "public", whatfor)
		return os.path.join(public_app_folder, "meteor_runtime_config.js")
	else:
		return os.path.join("assets", "fluorine", whatfor, "meteor_runtime_config.js")


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
		tmp_attr = tmp_attr.get(attr) or {}

	return tmp_attr


def remove_from_hooks(hooks, stop=False):

	base_template = "templates/fluorine_base.html"
	meteor_js = "/assets/js/meteor_app.min.js"
	meteor_css = "/assets/css/meteor_app.css"
	home_page = "fluorine_home"

	if isinstance(hooks, dict):
		base = hooks.get("base_template")
		home = hooks.get("home_page")
		hjs = hooks.get("app_include_js")
		hcss = hooks.get("app_include_css")

		if hjs and meteor_js in hjs:
			hjs.remove(meteor_js)
		if hcss and meteor_css in hcss:
			hcss.remove(meteor_css)

		if stop:
			if base_template == base:
				base.remove(base_template)

			if home_page == home:
				home.remove(home_page)

	else:
		if meteor_js in hooks:
			hooks.remove(meteor_js)
		if meteor_css in hooks:
			hooks.remove(meteor_css)

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
	version = version or frappe.__version__
	import semantic_version as sv
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

	if not meteor_config.get("stop") or frappe.local.making_production:
		#PATCH get_context
		if frappe_get_context == None:
			patch_frappe_get_context()
		else:
			print "error get_context"


if check_dev_mode():
	#PATCH HOOKS
	prepare_environment()
	import reactivity
