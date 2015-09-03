__author__ = 'luissaguas'


import frappe



@frappe.whitelist(allow_guest=True)
def meteor_compile():
	"""
	This request gives a Broken pipe error. This is because meteor get's new data and automaticaly disconnect current connection.
	This is a normal proceed.
	"""
	from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import prepare_make_meteor_file
	from fluorine.utils import meteor_config, meteor_web_app
	#from fluorine.commands_helpers import get_doctype
	if meteor_config.get("developer_mode") and not meteor_config.get("stop"):
		frappe.set_user("Administrator")
		#doc = get_doctype("Fluorine Reactivity", frappe.local.site)
		prepare_make_meteor_file(meteor_web_app)
		print "compile_meteor called for site {}.".format(frappe.local.site)