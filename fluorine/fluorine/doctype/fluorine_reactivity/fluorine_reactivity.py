# Copyright (c) 2013, Luis Fernandes and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import fluorine as fluor
from fluorine.utils import file
from fluorine.utils import fhooks
from fluorine.utils import react
from fluorine.utils import fcache


class FluorineReactivity(Document):
	def on_update(self, method=None):

		fluor.utils.set_config({
				"developer_mode": self.fluor_dev_mode
		})
		#print "self.fluorine_reactivity {}".format(self.fluorine_reactivity)
		paths = fluor.utils.get_js_paths()

		if self.fluorine_state == "off":
			fhooks.remove_react_from_app_hook(paths)
			return

		objjs = reactivity(react.get(self.fluorine_reactivity, None), paths)

		if not objjs:
			return

		page_default = True

		if self.fluorine_base_template and self.fluorine_base_template.lower() != "default":
			page_default = False

		fhooks.add_react_to_hook(paths, page_default=page_default)

		#elif self.fluorine_base_template.lower() == "default" or self.fluorine_state == "off":
		#	fluor.remove_base_template()
		#fluor.save_batch_hook_all("hooks_helper", objjs)

		#if not in dev mode compile to meteor.js
		#if not fluor.check_dev_mode():
			#file.observer.stop()
			#jq = 1 if self.fluorine_base_template and self.fluorine_base_template.lower() != "default" else 0
		#	jq = 0
		#	file.make_meteor_file(jquery=jq, devmode=0)
		#else:
		#	jq = 0
		#	file.make_meteor_file(jquery=jq, devmode=1)
			#file.observer.join()

def reactivity(where, path):

	#fluor.delete_fluorine_session("hooks_helper")
	objjs = {}

	if where == "both" or where == "app":
		objjs["app_include_js"] = path
		#it is inserted in fluorine_home.html
		#objjs["web_include_js"] = path

	return objjs


@frappe.whitelist()
def make_meteor_file(devmode, mthost, mtport, mghost, mgport, mgdb):
	version = fluor.utils.meteor_autoupdate_version()
	fcache.clear_frappe_caches()
	file.make_meteor_file(jquery=0, devmode=devmode)
	file.make_meteor_config_file(mthost, mtport, version)
	path = file.get_path_reactivity()
	fluor.utils.reactivity.run_reactivity(path, version, mthost=mthost, mtport=mtport, mghost=mghost, mgport=mgport, mgdb=mgdb, restart=True)
