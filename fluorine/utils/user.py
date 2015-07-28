# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'

import frappe
from frappe import _
from frappe.core.doctype.user.user import User


class MyUser(User):

	def send_welcome_mail_to_user(self):
		from frappe.utils import random_string
		from fluorine.utils import meteor_config
		import urllib

		key = random_string(32)
		self.db_set("reset_password_key", key)
		#link = get_url("/update-password?key=" + key)
		meteor = meteor_config.get("meteor_dev") or {}
		ddpurl = meteor.get("ddpurl")
		port = meteor.get("port")
		mturl = ddpurl + ":" + str(port)
		uri = "/?update-password=1&key=" + key
		link = urllib.basejoin(mturl, uri)
		#link = ddpurl + ":" + str(port) + "/" + "/update-password?key=" + key

		print "my Wellcome notifications mturl {} get_url {}".format(mturl, link)
		self.send_login_mail(_("Verify Your Account"), "templates/emails/new_user.html",
			{"link": link})



@frappe.whitelist(allow_guest=True)
def meteor_sign_up(email, full_name):

	user = frappe.db.get("User", {"email": email})
	if user:
		if user.disabled:
			return _("Registered but disabled.")
		else:
			return _("Already Registered")
	else:
		if frappe.db.sql("""select count(*) from tabUser where
			HOUR(TIMEDIFF(CURRENT_TIMESTAMP, TIMESTAMP(modified)))=1""")[0][0] > 200:
			frappe.msgprint("Login is closed for sometime, please check back again in an hour.")
			raise Exception, "Too Many New Users"
		from frappe.utils import random_string
		#user = frappe.get_doc({
		user = MyUser({
			"doctype":"User",
			"email": email,
			"first_name": full_name,
			"enabled": 1,
			"new_password": random_string(10),
			"user_type": "Website User"
		})
		user.flags.ignore_permissions = True
		user.insert()

		return _("Registration Details Emailed.")
