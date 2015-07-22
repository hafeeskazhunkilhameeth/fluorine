# Copyright (c) 2013, Luis Fernandes and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, os
from frappe.model.document import Document


class FluorineReactivity(Document):
	def on_update(self, method=None):
		import fluorine as fluor
		from fluorine.utils import file
		from fluorine.utils import fhooks

		from fluorine.utils.reactivity import meteor_config

		meteor_config["developer_mode"] = self.fluor_dev_mode

		if self.fluorine_state == "off":
			fluor.utils.set_config({
				"developer_mode": self.fluor_dev_mode
			})
			fhooks.change_base_template(devmode=1)
			return

		page_default = True

		if self.fluorine_base_template and self.fluorine_base_template.lower() != "default":
			page_default = False
			file.save_custom_template(self.fluorine_base_template)

		fhooks.change_base_template(page_default=page_default, devmode=self.fluor_dev_mode)
		save_to_common_site_config(self)


	def validate(self, method=None):
		if not self.ddpurl or self.ddpurl.strip() == "":
			return frappe.throw("You must provide a valid ddp url")

		if not self.site or self.site.strip() == "":
			return frappe.throw("You must provide a valid site")



def save_to_common_site_config(doc):
	from fluorine.utils.reactivity import meteor_config
	import os

	mgconf = {}
	mtconf = {}

	path_reactivity = file.get_path_reactivity()
	config_path = os.path.join(path_reactivity, "common_site_config.json")

	f = meteor_config

	mtconf["port"] = doc.fluor_meteor_port
	mtconf["host"] = doc.fluor_meteor_host
	mtconf["ddpurl"] = doc.ddpurl
	mgconf["host"] = doc.fluor_mongo_host
	mgconf["port"] = doc.fluor_mongo_port
	mgconf["db"] = doc.fluor_mongo_database

	f["site"] = doc.site
	f["developer_mode"] = doc.fluor_dev_mode

	if f.get("meteor_dev", None):
		f.get("meteor_dev").update(mtconf)
	else:
		f["meteor_dev"] = mtconf

	if f.get("meteor_mongo", None):
		f.get("meteor_mongo").update(mgconf)
	else:
		f["meteor_mongo"] = mgconf


	file.save_js_file(config_path, f)

@frappe.whitelist()
def make_meteor_file(devmode, mthost, mtport, mtddpurl, mghost, mgport, mgdb, architecture, whatfor):
	#devmode = frappe.utils.cint(devmode)
	from frappe.website.context import get_context
	from fluorine.utils import fcache, file
	#from fluorine.utils.spacebars_template import get_app_pages, get_web_pages
	fcache.clear_frappe_caches()
	#whatfor = ["common"] if devmode else ["meteor_web", "meteor_app"]
	_whatfor = {"Both": ("meteor_web", "meteor_app"), "Reactive Web": ("meteor_web",), "Reactive App": ("meteor_app",)}

	prepare_compile_environment()

	for w in _whatfor.get(whatfor):
		prepare_client_files(w)

		if whatfor == "Both" and w == "meteor_app":
			mtport = int(mtport) + 80
			#get_app_pages(context)
			context = get_context("mdesk")
			frappe.get_template(context.base_template_path).render(context)
		else:
			context = get_context("fluorine_home")
			frappe.get_template(context.base_template_path).render(context)
			#get_web_pages(context)

		file.make_meteor_file(jquery=0, whatfor=w, mtport=mtport, mthost=mthost, architecture=architecture)

	if "meteor_app" in _whatfor.get(whatfor):
		make_final_app_client(meteor_root_url=mthost, meteor_port=int(mtport), meteor_ddpurl=mtddpurl)
	#fluorine_publicjs_path = os.path.join(frappe.get_app_path("fluorine"), "public", "js", "react")
	#file.remove_folder_content(fluorine_publicjs_path)
	#file.make_meteor_config_file(mthost, mtport, version)

	#if devmode:
	#	restart_reactivity(mthost=mthost, mtport=mtport, mghost=mghost, mgport=mgport, mgdb=mgdb)

def prepare_compile_environment():

	from fluorine.utils.reactivity import meteor_config, list_ignores
	import fluorine as fluor

	fluor.utils.set_config({
		"developer_mode": 0
	})
	meteor_config["developer_mode"] = 0

	list_ignores["files_folders"] = {
		"all":{
			"remove": [{"pattern": "highlight/?.*"}]
		}
	}

	doc = frappe.get_doc("Fluorine Reactivity")
	doc.fluor_dev_mode = 0
	doc.fluorine_state = "off"
	doc.save()


def make_final_app_client(jquery=0, meteor_root_url="http://localhost", meteor_ddpurl="http://localhost", meteor_port=3000):

	import json
	import file
	from fluorine.utils.meteor.utils import get_meteor_release, make_auto_update_version, get_meteor_config,\
		save_meteor_props, save_meteor_root_prefix

	meteor_ddp_default_connection_url = meteor_ddpurl + (":" + str(meteor_port) if meteor_port > 80 else "")

	whatfor = "meteor_app"
	fluorine_path = frappe.get_app_path("fluorine")
	js_path = os.path.join(fluorine_path, "public", "js", "meteor")
	build_file = os.path.join(fluorine_path, "public", "build.json")

	if os.path.exists(build_file):
		build_json_file = file.read(build_file)
		build_json = json.loads(build_json_file)
	else:
		build_json = frappe._dict()

	build_json["js/meteor_app.js"] = []
	build_json["js/meteor_app.css"] = []

	react_path = file.get_path_reactivity()
	meteor_final_path = os.path.join(react_path, "final_app/bundle/programs/web.browser")
	progarm_path = os.path.join(meteor_final_path, "program.json")

	star_path = os.path.join(react_path, "final_app/bundle/star.json")
	meteorRelease = get_meteor_release(star_path)

	manifest = file.read(progarm_path)

	manifest = json.loads(manifest).get("manifest")
	meteor_autoupdate_version, meteor_autoupdate_version_freshable, manifest_js, manifest_css =\
		make_auto_update_version(progarm_path, meteorRelease, meteor_root_url, "", whatfor)

	props = get_meteor_config(meteor_root_url, meteor_ddp_default_connection_url, "", meteor_autoupdate_version,\
							meteor_autoupdate_version_freshable, meteorRelease, whatfor)

	frappe.create_folder(js_path)
	meteor_runtime_path = os.path.join(js_path, "meteor_runtime_config.js")

	save_meteor_props(props, meteor_runtime_path)

	meteor_root_url_prefix_path = os.path.join(js_path, "meteor_url_prefix.js")
	#save_meteor_props("__meteor_runtime_config__.ROOT_URL_PATH_PREFIX = '%s';" % meteor_ddp_default_connection_url, meteor_root_url_prefix)
	save_meteor_root_prefix(meteor_ddp_default_connection_url, meteor_root_url_prefix_path)

	rel = os.path.relpath(meteor_runtime_path, fluorine_path)
	build_json.get("js/meteor_app.js").append(rel)

	build_frappe_json_files(manifest, js_path, fluorine_path, build_json, meteor_final_path, jquery=jquery)

	rel = os.path.relpath(meteor_root_url_prefix_path, fluorine_path)
	build_json.get("js/meteor_app.js").append(rel)

	file.save_js_file(build_file, build_json)


def build_frappe_json_files(manifest, js_path, fluorine_path, build_json, meteor_final_path, jquery=0):
	from shutil import copyfile

	for m in manifest:
		if m.get("where") == "client":
			path = m.get("path")
			if "jquery" in path and jquery == 0:
				continue
			dst = os.path.join(js_path, path)
			rel = os.path.relpath(dst, fluorine_path)
			if m.get("type") == "js":
				build_json["js/meteor_app.js"].append(rel)
			else:
				build_json["js/meteor_app.css"].append(rel)

			frappe.create_folder(os.path.dirname(dst))
			src = os.path.join(meteor_final_path, path)
			copyfile(src, dst)


def restart_reactivity(mthost="http://localhost", mtport=3000, mghost="http://localhost", mgport=27017, mgdb="fluorine"):
	from fluorine.utils.reactivity import run_reactivity
	path = file.get_path_reactivity()
	version = fluor.utils.meteor_autoupdate_version()
	run_reactivity(path, version, mthost=mthost, mtport=mtport, mghost=mghost, mgport=mgport, mgdb=mgdb, restart=True)

def prepare_client_files(whatfor):
	from fluorine.utils.react_file_loader import remove_directory
	import file
	
	#fluorine_path = frappe.get_app_path("fluorine")
	react_path = file.get_path_reactivity()
	meteor_final_path = os.path.join(react_path, "final_%s" % (whatfor.split("_")[1],))
	if os.path.exists(meteor_final_path):
		remove_directory(meteor_final_path)

	fluorine_path = frappe.get_app_path("fluorine")
	meteor_js_path = os.path.join(fluorine_path, "public", "js", "meteor")
	if os.path.exists(meteor_js_path):
		remove_directory(meteor_js_path)
	#fluorine_dst_temp_path = os.path.join(frappe.get_app_path("fluorine"), "templates", "react", "temp")

	#dst = os.path.join(react_path, "app")
	#remove_tmp_app_dir(fluorine_dst_temp_path, dst)
	#if devmode:
	#	return
	#frappe.create_folder(dst)
	#file.copy_all_files_with_symlink(fluorine_dst_temp_path, dst, whatfor, extension=["js", "html"])


def remove_tmp_app_dir(src, dst):
	from fluorine.utils.react_file_loader import remove_directory
	try:
		remove_directory(src)
		remove_directory(dst)
	except:
		pass