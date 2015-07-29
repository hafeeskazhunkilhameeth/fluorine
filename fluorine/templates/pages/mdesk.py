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
	frappe.form_dict['sid'] = frappe.local.form_dict.get("code")
	print "getting context in mdesk.py 7 dict {}".format(frappe.local.form_dict )
	make_session(resume=True)
	return get_app_pages(context)



def make_session(user=None, full_name=None, user_type=None, resume=False):
	# start session
	frappe.local.session_obj = Session(user=user, resume=resume,
		full_name=full_name, user_type=user_type)

	# reset user if changed to Guest
	user = frappe.local.session_obj.user
	frappe.local.session = frappe.local.session_obj.data
	#clear_active_sessions()

def clear_active_sessions():
		if not frappe.conf.get("deny_multiple_sessions"):
			return

		if frappe.session.user != "Guest":
			clear_sessions(frappe.session.user, keep_current=True)