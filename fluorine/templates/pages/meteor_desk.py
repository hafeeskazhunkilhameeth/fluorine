# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import frappe
from fluorine.utils.spacebars_template import fluorine_build_context
import fluorine.utils
from fluorine.utils import get_Frappe_Version
from fluorine.utils import file

frappe_version = get_Frappe_Version()

if frappe_version >=5:
	import deskv5 as desk
	#base_template_path = "templates/pages/deskv5.html"
else:
	import deskv4 as desk
	#base_template_path = "templates/pages/deskv4.html"

no_sitemap = desk.no_sitemap
no_cache = desk.no_cache
base_template_path = desk.base_template_path

def get_context(context):
	context.frappe_version = frappe_version
	set_meteor_conetxt(context)
	return desk.get_context(context)



def set_meteor_conetxt(context):

	print "fluorine get_context called again app !!!"
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

	context.meteor_web = False
	context.custom_template = doc.fluorine_base_template
	context.whatfor = "common" if devmode else "app"

	return fluorine_build_context(context, "meteor_app")