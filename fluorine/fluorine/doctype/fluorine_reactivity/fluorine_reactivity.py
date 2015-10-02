# Copyright (c) 2013, Luis Fernandes and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, os
from frappe.model.document import Document
from frappe import _


class FluorineReactivity(Document):

	def on_update(self, method=None):
		from fluorine.utils.reactivity import meteor_config
		from fluorine.utils.spacebars_template import save_sites_to_cache

		meteor_config["developer_mode"] = self.fluor_dev_mode
		if self.current_dev_app and self.current_dev_app.strip() != "":
			meteor_config["current_dev_app"] = self.current_dev_app

		save_to_common_site_config(self, meteor_config)


	def validate(self, method=None):
		if not self.ddpurl or self.ddpurl.strip() == "":
			return frappe.throw("You must provide a valid ddp url")

		if self.current_dev_app and self.current_dev_app.strip() != "":
			from fluorine.utils import APPS as apps
			if self.current_dev_app not in apps:
				return frappe.throw("App %s is not a valid meteor app. To be a valid meteor app it must exist as installed app and must exist templates/react/meteor_app and/or\
				 					templates/react/meteor_web folder" % self.current_dev_app)

		for site in self.fluorine_link_sites:
			docsite = frappe.get_doc("Fluorine Site Names", site.fluorine_site_name)
			if docsite.fluorine_site_type != "Dedicated":
				return frappe.throw("Sorry, but you must enter only Dedicated sites.")


def save_to_common_site_config(doc, meteor_config=None):
	from fluorine.utils.meteor.utils import default_path_prefix, PORT, update_common_config

	f = meteor_config

	if not f.get("meteor_http_forwarded_count"):
		f["meteor_http_forwarded_count"] = "1"

	if not f.get("meteor_dev", None):
		f["meteor_dev"] = {}

	meteor_dev = f.get("meteor_dev")

	if not meteor_dev.get("meteor_web"):
		meteor_dev["meteor_web"] = {"production":1}

	meteor_web = meteor_dev.get("meteor_web")

	if not meteor_dev.get("meteor_app"):
		meteor_dev["meteor_app"] = {"production":1}

	meteor_app = meteor_dev.get("meteor_app")

	if not meteor_app.get("ROOT_URL_PATH_PREFIX"):
		meteor_app["ROOT_URL_PATH_PREFIX"] = default_path_prefix

	meteor_web["port"] = doc.fluor_meteor_port or PORT.meteor_web
	meteor_app["port"] = PORT["meteor_app"]

	meteor_dev["host"] = doc.fluor_meteor_host.strip() or "http://127.0.0.1"
	meteor_app["ddpurl"] = doc.ddpurl.strip()

	f["site"] = doc.site.strip() if doc.site else frappe.local.site
	f["developer_mode"] = doc.fluor_dev_mode


	if doc.check_mongodb and doc.fluor_mongo_host.strip():
		if not f.get("meteor_mongo"):
			f["meteor_mongo"] = {}

		mongo = f.get("meteor_mongo")
		mongo["host"] = doc.fluor_mongo_host.replace("http://","").replace("mongodb://","").strip(' \t\n\r')
		mongo["port"] = doc.fluor_mongo_port or 0
		mongo["db"] = doc.fluor_mongo_database.strip()
		mongo.pop("type", None)

	update_common_config(f)


@frappe.whitelist()
def check_apps_updates():
	from fluorine.utils import whatfor_all
	from fluorine.commands_helpers.meteor import update_versions, check_updates

	bench = "../../bench-repo/"
	msg = []

	update_versions(bench=bench)
	for whatfor in whatfor_all:
		if not check_updates(whatfor, bench=bench):
			msg.append(_("%s: Sorry, There are no updates." % whatfor))
		else:
			msg.append(_("%s: There are updates." % whatfor))

	frappe.msgprint("\n".join(msg))


def remove_tmp_app_dir(src, dst):
	from fluorine.utils.react_file_loader import remove_directory
	try:
		remove_directory(src)
		remove_directory(dst)
	except:
		pass
