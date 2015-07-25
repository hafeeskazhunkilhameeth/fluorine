# Copyright (c) 2013, Luis Fernandes and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, os
from frappe.model.document import Document


class FluorineReactivity(Document):
	def on_update(self, method=None):
		#from fluorine.utils.file import set_config
		from fluorine.utils.file import save_custom_template, set_config
		from fluorine.utils.fhooks import change_base_template

		from fluorine.utils.reactivity import meteor_config

		meteor_config["developer_mode"] = self.fluor_dev_mode

		if self.fluorine_state == "off":
			set_config({
				"developer_mode": self.fluor_dev_mode
			})
			change_base_template(devmode=1)
			return

		page_default = True

		if self.fluorine_base_template and self.fluorine_base_template.lower() != "default":
			page_default = False
			save_custom_template(self.fluorine_base_template)

		change_base_template(page_default=page_default, devmode=self.fluor_dev_mode)
		save_to_common_site_config(self)

		save_to_procfile(self)


	def validate(self, method=None):
		if not self.ddpurl or self.ddpurl.strip() == "":
			return frappe.throw("You must provide a valid ddp url")

		if not self.site or self.site.strip() == "":
			return frappe.throw("You must provide a valid site")

def save_to_procfile(doc):
	from fluorine.utils.file import writelines

	procfile, procfile_path = get_procfile()
	tostart = {"Both": ("meteor_app", "meteor_web"), "Reactive App": ("meteor_app", ), "Reactive Web": ("meteor_web", )}
	meteor_apps = tostart.get(doc.fluorine_reactivity)

	export_mongo = ''
	if doc.check_mongodb and doc.fluor_mongo_host.strip():
		user_pass = "%s:%s@" % (doc.mongo_user, doc.mongo_pass) if doc.mongo_user and doc.mongo_pass else ''
		mghost = doc.fluor_mongo_host.replace("http://","").replace("mongodb://","").strip(' \t\n\r')
		export_mongo = "export MONGO_URL=mongodb://%s%s:%s/%s && " % (user_pass, mghost, doc.fluor_mongo_port, doc.fluor_mongo_database)

	for app in meteor_apps:
		procfile.insert(0, "%s: (%sexport ROOT_URL=%s && cd apps/reactivity/%s && meteor --port %s)\n" %\
									(app, export_mongo, doc.fluor_meteor_host,app, int(doc.fluor_meteor_port) + (80 if app == "meteor_app" else 0)))

	writelines(procfile_path, procfile)


def get_procfile():
	from fluorine.utils.file import readlines
	from fluorine.utils.fjinja2.utils import c

	re_meteor_procfile = c(r"^(meteor_app:|meteor_web:)")
	procfile_dir = os.path.normpath(os.path.join(os.getcwd(), ".."))
	procfile_path = os.path.join(procfile_dir, "Procfile")

	procfile = readlines(procfile_path)
	procfile = [p for p in procfile if not re_meteor_procfile.match(p)]

	return procfile, procfile_path

def remove_from_procfile():
	from fluorine.utils.file import writelines

	procfile, procfile_path = get_procfile()
	writelines(procfile_path, procfile)


def save_to_common_site_config(doc):
	from fluorine.utils.reactivity import meteor_config
	import os
	from fluorine.utils.file import get_path_reactivity, save_js_file

	mgconf = {}
	mtconf = {}

	path_reactivity = get_path_reactivity()
	config_path = os.path.join(path_reactivity, "common_site_config.json")

	f = meteor_config

	mtconf["port"] = doc.fluor_meteor_port
	mtconf["host"] = doc.fluor_meteor_host
	mtconf["ddpurl"] = doc.ddpurl
	mgconf["host"] = doc.fluor_mongo_host.strip()
	mgconf["port"] = doc.fluor_mongo_port.strip() or 0
	mgconf["db"] = doc.fluor_mongo_database

	f["site"] = doc.site
	f["developer_mode"] = doc.fluor_dev_mode

	if f.get("meteor_dev", None):
		f.get("meteor_dev").update(mtconf)
	else:
		f["meteor_dev"] = mtconf

	if doc.fluor_mongo_host.strip() and doc.check_mongodb:
		if f.get("meteor_mongo", None):
			f.get("meteor_mongo").update(mgconf)
		else:
			f["meteor_mongo"] = mgconf

	elif f.get("meteor_mongo", None):
		del f["meteor_mongo"]


	save_js_file(config_path, f)

@frappe.whitelist()
def make_meteor_file(devmode, mthost, mtport, mtddpurl, mghost, mgport, mgdb, architecture, whatfor):
	#devmode = frappe.utils.cint(devmode)
	from frappe.website.context import get_context
	from fluorine.utils.file import make_meteor_file
	from fluorine.utils.fcache import clear_frappe_caches
	#from fluorine.utils.spacebars_template import get_app_pages, get_web_pages
	clear_frappe_caches()
	#whatfor = ["common"] if devmode else ["meteor_web", "meteor_app"]
	_whatfor = {"Both": ("meteor_web", "meteor_app"), "Reactive Web": ("meteor_web",), "Reactive App": ("meteor_app",)}

	prepare_compile_environment()

	for w in _whatfor.get(whatfor):
		prepare_client_files(w)

		if whatfor == "Both" and w == "meteor_app":
			mtport = int(mtport) + 80
			#get_app_pages(context)
			#local = frappe.local.path
			frappe.local.path = "mdesk"
			#frappe.local.path = "mdesk"
			context = get_context("mdesk")
			frappe.get_template(context.base_template_path).render(context)
		else:
			frappe.local.path = "fluorine_home"
			context = get_context("fluorine_home")
			frappe.get_template(context.base_template_path).render(context)
			#get_web_pages(context)

		make_meteor_file(jquery=0, whatfor=w, mtport=mtport, mthost=mthost, architecture=architecture)

	if "meteor_app" in _whatfor.get(whatfor):
		make_final_app_client(meteor_root_url=mthost, meteor_port=int(mtport), meteor_ddpurl=mtddpurl)

	#fluorine_publicjs_path = os.path.join(frappe.get_app_path("fluorine"), "public", "js", "react")
	#file.remove_folder_content(fluorine_publicjs_path)
	#file.make_meteor_config_file(mthost, mtport, version)

	#if devmode:
	#	restart_reactivity(mthost=mthost, mtport=mtport, mghost=mghost, mgport=mgport, mgdb=mgdb)

def prepare_compile_environment():

	from fluorine.utils.fhooks import change_base_template
	from fluorine.utils.reactivity import meteor_config, list_ignores
	from fluorine.utils.file import set_config

	set_config({
		"developer_mode": 0
	})
	meteor_config["developer_mode"] = 0
	meteor_config["mongodb_users_ready"] = 0

	list_ignores["files_folders"] = {
		"all":{
			"remove": [{"pattern": "highlight/?.*"}]
		}
	}

	remove_from_procfile()
	change_base_template(page_default=True, devmode=0)
	doc = frappe.get_doc("Fluorine Reactivity")
	doc.fluor_dev_mode = 0
	doc.fluorine_state = "off"
	doc.save()


def make_final_app_client(jquery=0, meteor_root_url="http://localhost", meteor_ddpurl="http://localhost", meteor_port=3000):

	import json
	from fluorine.utils.file import get_path_reactivity, read, save_js_file
	from fluorine.utils.meteor.utils import get_meteor_release, make_auto_update_version, get_meteor_config,\
		save_meteor_props, save_meteor_root_prefix

	meteor_ddp_default_connection_url = meteor_ddpurl + (":" + str(meteor_port) if meteor_port > 80 else "")

	whatfor = "meteor_app"
	fluorine_path = frappe.get_app_path("fluorine")
	js_path = os.path.join(fluorine_path, "public", "js", "meteor")
	build_file = os.path.join(fluorine_path, "public", "build.json")

	if os.path.exists(build_file):
		build_json_file = read(build_file)
		build_json = json.loads(build_json_file)
	else:
		build_json = frappe._dict()

	build_json["js/meteor_app.js"] = []
	build_json["js/meteor_app.css"] = []

	react_path = get_path_reactivity()
	meteor_final_path = os.path.join(react_path, "final_app/bundle/programs/web.browser")
	progarm_path = os.path.join(meteor_final_path, "program.json")

	star_path = os.path.join(react_path, "final_app/bundle/star.json")
	meteorRelease = get_meteor_release(star_path)

	manifest = read(progarm_path)

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

	save_js_file(build_file, build_json)


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

def prepare_client_files(whatfor):
	from fluorine.utils.react_file_loader import remove_directory
	from fluorine.utils.file import get_path_reactivity
	from shutil import copyfile

	#fluorine_path = frappe.get_app_path("fluorine")
	react_path = get_path_reactivity()
	meteor_final_path = os.path.join(react_path, "final_%s" % (whatfor.split("_")[1],))
	if os.path.exists(meteor_final_path):
		remove_directory(meteor_final_path)

	fluorine_path = frappe.get_app_path("fluorine")
	meteor_js_path = os.path.join(fluorine_path, "public", "js", "meteor")
	if os.path.exists(meteor_js_path):
		remove_directory(meteor_js_path)

	src = os.path.join(react_path, whatfor, ".meteor", "packages")
	dst = os.path.join(fluorine_path, "templates", "packages_" + whatfor)
	copyfile(src, dst)
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