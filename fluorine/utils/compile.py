__author__ = 'luissaguas'


import frappe
import frappe.async


#@frappe.whitelist(allow_guest=True)
@frappe.async.handler
def meteor_compile():
	from fluorine.utils.context import prepare_context_meteor_file
	from fluorine.utils import meteor_config, meteor_web_app


	if meteor_config.get("developer_mode") and not meteor_config.get("stop"):
		prepare_context_meteor_file(meteor_web_app)
