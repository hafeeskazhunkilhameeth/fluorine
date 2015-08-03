# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'


import frappe

meteor_config = None

assets_public_path = "/assets/fluorine/js/react"



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

	conf = None

	meteor_config = get_common_config_file_json()

	return conf

if check_dev_mode():
	frappe_conf = frappe.get_site_config()
	frappe_developer_mode = frappe_conf.developer_mode

	if frappe_developer_mode:
		print "Enter Reactivity State!!!"
		import spacebars_template
		import reactivity
