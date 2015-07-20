# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'

no_sitemap = 1
no_cache = 1
base_template_path = "templates/pages/mdesk.html"

import frappe, os

def get_context(context):
	from fluorine.utils.spacebars_template import fluorine_build_context
	import fluorine

	print "fluorine get_context called again 3!!!"

	devmode = fluorine.utils.check_dev_mode()
	context.developer_mode = devmode
	context.jquery_include = fluorine.utils.jquery_include()

	doc = frappe.get_doc("Fluorine Reactivity")

	#Meteor
	fluorine.utils.build_meteor_context(context, devmode, "meteor_app")
	context.meteor_web = True
	context.custom_template = doc.fluorine_base_template

	context = fluorine_build_context(context, "meteor_app")

	fcontext = get_frappe_context(context)

	include_js = fcontext.get("include_js",[])
	include_css = fcontext.get("include_css", [])

	if devmode:
		#TODO ver se é preciso remove tb o css gerado
		try:
			include_js.remove("/assets/fluorine/js/meteor_app.js")
		except:
			pass

	fcontext["include_js"] = context.meteor_package_js + include_js
	fcontext["include_css"] = context.meteor_package_css + include_css
	#fcontext["include_js"] = context.meteor_package_js + fcontext.get("include_js",[])
	#fcontext["include_css"] = context.meteor_package_css + fcontext.get("include_css", [])

	context.update(fcontext)

	return context


def get_frappe_context(context):
	from fluorine.utils.module import get_app_context

	app = "frappe"
	app_path = frappe.get_app_path(app)
	path = os.path.join(app_path, "templates", "pages")
	ret = get_app_context(context, path, app, app_path, "desk.py")
	return ret
