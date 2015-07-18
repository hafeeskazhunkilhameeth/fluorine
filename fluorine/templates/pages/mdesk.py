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

	fcontext["include_js"] = context.meteor_package_js + fcontext.get("include_js",[])
	fcontext["include_css"] = context.meteor_package_css + fcontext.get("include_css", [])

	context.update(fcontext)

	return context


def get_frappe_context(context):

	ret = None
	app = "frappe"
	app_path = frappe.get_app_path(app)
	path = os.path.join(app_path, "templates", "pages")
	if os.path.exists(path):
		# add website route
		controller_path = os.path.join(path, "desk.py")
		if os.path.exists(controller_path):
			controller = app + "." + os.path.relpath(controller_path,
				app_path).replace(os.path.sep, ".")[:-3]
			module = frappe.get_module(controller)
			if module:
				if hasattr(module, "get_context"):
					ret = module.get_context(context)
				if hasattr(module, "get_children"):
					context.get_children = module.get_children
				for prop in ("template", "condition_field"):
					if hasattr(module, prop):
						context[prop] = getattr(module, prop)
	return ret