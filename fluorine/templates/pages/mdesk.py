# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'

import frappe
from frappe.sessions import Session, clear_sessions

no_sitemap = 1
no_cache = 1
base_template_path = "templates/pages/mdesk.html"


def get_context(context):
	from fluorine.utils.spacebars_template import get_app_pages
	"""
	from frappe.utils import cstr
	frappe.form_dict['sid'] = frappe.local.form_dict.get("code")
	#user_id = frappe.local.form_dict.get("user_id")
	make_session(resume=True)
	if not frappe.local.session.user:
		make_session(cstr(frappe.local.request.args.get("user_id")), resume=False)
	#for k, v in frappe.local.request.args.iteritems():
	#	print "key and value for request {} v {}".format(k,v)
	print "getting context in mdesk.py 10 dict {} user {} req args {}".format(frappe.local.form_dict, frappe.local.session.user, frappe.local.request.args.get("user_id"))
	"""
	print "getting context for desk"
	return get_app_pages(context)

"""
def make_session(user=None, full_name=None, user_type=None, resume=False):
	# start session
	frappe.local.session_obj = Session(user=user, resume=resume,
		full_name=full_name, user_type=user_type)

	# reset user if changed to Guest
	#user = frappe.local.session_obj.user
	frappe.local.session = frappe.local.session_obj.data
	#clear_active_sessions()

def clear_active_sessions():
		if not frappe.conf.get("deny_multiple_sessions"):
			return

		if frappe.session.user != "Guest":
			clear_sessions(frappe.session.user, keep_current=True)
"""