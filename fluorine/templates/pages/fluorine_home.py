__author__ = 'luissaguas'

import fluorine
from fluorine.utils.spacebars_template import fluorine_build_context
from fluorine.utils import file
import fluorine.utils
import frappe


def get_context(context):

	print "fluorine get_context called again 3!!!"

	devmode = fluorine.utils.check_dev_mode()
	frappe.local.fenv = None
	frappe.local.floader = None
	context.developer_mode = devmode
	context.jquery_include = fluorine.utils.jquery_include()

	doc = frappe.get_doc("Fluorine Reactivity")

	#Meteor
	meteor_host = doc.fluor_meteor_host + ":" + str(doc.fluor_meteor_port)
	context.meteorRelease = file.get_meteor_release()
	context.meteor_root_url = meteor_host
	context.meteor_url_path_prefix = fluorine.utils.meteor_url_path_prefix()
	context.meteor_autoupdate_version = fluorine.utils.meteor_autoupdate_version()
	context.meteor_autoupdate_version_freshable = fluorine.utils.meteor_autoupdate_version_freshable()
	context.meteor_ddp_default_connection_url = meteor_host

	context.meteor_web = True
	context.custom_template = doc.fluorine_base_template
	context.whatfor = "common" if devmode else "web"

	context.meteor_web_include_css = frappe.get_hooks("meteor_web_include_css")
	context.meteor_web_include_js = frappe.get_hooks("meteor_web_include_js")

	return fluorine_build_context(context, "meteor_web")
