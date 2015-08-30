# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'

import frappe

meteor_config = None

assets_public_path = "/assets/fluorine/js/react"

APPS = None

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
		#print "hooks in my fluor_get_hooks appname {} hooks {}".format(app_name, hooks)
	return hooks


def fluor_get_context(path):
	from fluorine.templates.pages import mdesk

	#print "path fluor_get_context 2 {}".format(path)
	context = frappe_get_context(path)
	if path == "desk":
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
	from fluorine.utils.file import get_path_reactivity, get_fluorine_conf

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


get_installed_apps()


if check_dev_mode():
	#import logging
	#PATCH HOOKS
	frappe_get_hooks = frappe.get_hooks
	frappe.get_hooks = fluor_get_hooks

	if not meteor_config.get("stop"):
		#PATCH get_context
		import frappe.website.context
		frappe_get_context = frappe.website.context.get_context
		frappe.website.context.get_context = fluor_get_context

		#frappe_conf = frappe.get_site_config()
		#logger = logging.getLogger("frappe")
		#logger.error('Hello baby %s' % frappe_conf)
		#frappe_developer_mode = frappe_conf.developer_mode
		#if frappe_conf.developer_mode:

		#print "Enter Reactivity State!!!"
		import spacebars_template
		import reactivity
