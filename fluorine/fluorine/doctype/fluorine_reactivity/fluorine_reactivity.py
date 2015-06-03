# Copyright (c) 2013, Luis Fernandes and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import fluorine as fluor
from fluorine.utils import file
from fluorine.utils import fhooks
from fluorine.utils import fcache


class FluorineReactivity(Document):
	def on_update(self, method=None):

		fluor.utils.set_config({
				"developer_mode": self.fluor_dev_mode
		})

		if self.fluorine_state == "off":
			fhooks.change_base_template()
			return

		page_default = True

		if self.fluorine_base_template and self.fluorine_base_template.lower() != "default":
			page_default = False

		fhooks.change_base_template(self.fluorine_base_template, page_default=page_default)


@frappe.whitelist()
def make_meteor_file(devmode, mthost, mtport, mghost, mgport, mgdb):
	devmode = frappe.utils.cint(devmode)
	fcache.clear_frappe_caches()
	whatfor = ["common"] if devmode else ["meteor_web", "meteor_app"]
	for w in whatfor:
		prepare_client_files(w, devmode)
		file.make_meteor_file(jquery=0, devmode=devmode, whatfor=w)
	#fluorine_publicjs_path = os.path.join(frappe.get_app_path("fluorine"), "public", "js", "react")
	#file.remove_folder_content(fluorine_publicjs_path)
	#file.make_meteor_config_file(mthost, mtport, version)
	if devmode:
		restart_reactivity(mthost=mthost, mtport=mtport, mghost=mghost, mgport=mgport, mgdb=mgdb)

def restart_reactivity(mthost="http://localhost", mtport=3000, mghost="http://localhost", mgport=27017, mgdb="fluorine"):
	from fluorine.utils.reactivity import run_reactivity
	path = file.get_path_reactivity()
	version = fluor.utils.meteor_autoupdate_version()
	run_reactivity(path, version, mthost=mthost, mtport=mtport, mghost=mghost, mgport=mgport, mgdb=mgdb, restart=True)

def prepare_client_files(whatfor, devmode):
	import os
	fluorine_dst_temp_path = os.path.join(frappe.get_app_path("fluorine"), "templates", "react", "temp")
	react_path = file.get_path_reactivity()
	dst = os.path.join(react_path, "app")
	remove_tmp_app_dir(fluorine_dst_temp_path, dst)
	if devmode:
		return
	frappe.create_folder(dst)
	file.copy_all_files_with_symlink(fluorine_dst_temp_path, dst, whatfor, extension=["js", "html"])


def remove_tmp_app_dir(src, dst):
	from fluorine.utils.react_file_loader import remove_directory
	try:
		remove_directory(src)
		remove_directory(dst)
	except:
		pass