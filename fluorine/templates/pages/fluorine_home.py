# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'

import fluorine
import fluorine.utils
import frappe
from fluorine.utils.meteor.utils import build_meteor_context
from fluorine.utils.spacebars_template import fluorine_build_context

no_sitemap = 1
base_template_path = "templates/fluorine_base.html"
no_cache = 1

def get_context(context):
	print "fluorine get_context called again 3!!!"

	devmode = fluorine.utils.check_dev_mode()
	context.developer_mode = devmode
	context.jquery_include = fluorine.utils.jquery_include()

	doc = frappe.get_doc("Fluorine Reactivity")

	#Meteor
	build_meteor_context(context, devmode, "meteor_web")

	context.meteor_web = True
	context.custom_template = doc.fluorine_base_template
	#context.whatfor = "common" if devmode else "web"

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

	return fluorine_build_context(context, "meteor_web")
