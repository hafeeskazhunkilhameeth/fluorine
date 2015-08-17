# Copyright (c) 2013, Luis Fernandes and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, os
from frappe.model.document import Document



"""
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
			change_base_template()
			return

		page_default = True

		if self.fluorine_base_template and self.fluorine_base_template.lower() != "default":
			page_default = False
			save_custom_template(self.fluorine_base_template)

		if not self.fluor_dev_mode:
			prepare_make_meteor_file(self.fluor_meteor_port, self.fluorine_reactivity)
			#self.fluorine_state = "off"
		else:
			change_base_template(page_default=page_default)

		save_to_common_site_config(self)

		if self.fluor_dev_mode:
			save_to_procfile(self)
		else:
			remove_from_procfile()


	def validate(self, method=None):
		if not self.ddpurl or self.ddpurl.strip() == "":
			return frappe.throw("You must provide a valid ddp url")

		#if not self.site or self.site.strip() == "":
		#	return frappe.throw("You must provide a valid site")
"""

class FluorineReactivity(Document):
	def on_update(self, method=None):
		from fluorine.utils.file import set_config

		from fluorine.utils.reactivity import meteor_config

		meteor_config["developer_mode"] = self.fluor_dev_mode if self.fluorine_state == "on" else 0

		if self.fluorine_state == "off":
			set_config({
				#"developer_mode": self.fluor_dev_mode
				"developer_mode": 0
			})
			prepare_make_meteor_file(self.fluor_meteor_port, self.fluorine_reactivity)
			#return

		#if self.fluorine_base_template and self.fluorine_base_template.lower() != "default":
		#	save_custom_template(self.fluorine_base_template)

		#if not self.fluor_dev_mode:
			#prepare_make_meteor_file(self.fluor_meteor_port, self.fluorine_reactivity)

		save_to_common_site_config(self)

		#if self.fluor_dev_mode:
		#	save_to_procfile(self)
		#else:
		#	remove_from_procfile()

	def validate(self, method=None):
		if not self.ddpurl or self.ddpurl.strip() == "":
			return frappe.throw("You must provide a valid ddp url")


def save_to_procfile(doc):
	from fluorine.utils.file import writelines
	from fluorine.utils.reactivity import meteor_config
	from fluorine.utils.meteor.utils import default_path_prefix, PORT

	procfile, procfile_path = get_procfile()
	tostart = {"Both": ("meteor_app", "meteor_web"), "Reactive App": ("meteor_app", ), "Reactive Web": ("meteor_web", )}
	meteor_apps = tostart.get(doc.fluorine_reactivity)

	mongo_default = False
	if doc.check_mongodb and doc.fluor_mongo_host.strip():
		user_pass = "%s:%s@" % (doc.mongo_user, doc.mongo_pass) if doc.mongo_user and doc.mongo_pass else ''
		mghost = doc.fluor_mongo_host.replace("http://","").replace("mongodb://","").strip(' \t\n\r')
		export_mongo = "export MONGO_URL=mongodb://%s%s:%s/%s && " % (user_pass, mghost, doc.fluor_mongo_port, doc.fluor_mongo_database)
	else:
		mongo_conf = meteor_config.get("meteor_mongo")
		db = mongo_conf.get("db")
		port = mongo_conf.get("port")
		host = mongo_conf.get("host")
		export_mongo = "export MONGO_URL=mongodb://%s:%s/%s && " % (host, port, db)
		mongo_default = True


	meteor_dev = meteor_config.get("meteor_dev", None)
	count = meteor_config.get("meteor_http_forwarded_count") or "1"
	forwarded_count = "export HTTP_FORWARDED_COUNT='" + str(count) + "'"
	if meteor_dev:
		for app in meteor_apps:
			meteor = meteor_dev.get(app)
			default_prefix = default_path_prefix if app=="meteor_app" else ""
			prefix = meteor.get("ROOT_URL_PATH_PREFIX") or ""
			mthost = meteor_dev.get("host") + (prefix if prefix else default_prefix)
			mtport = meteor.get("port") or PORT.get(app)
			if app == "meteor_web" and mongo_default:
				exp_mongo = ""
			else:
				exp_mongo = export_mongo

			procfile.insert(0, "%s: (%s%s && export ROOT_URL=%s && cd apps/reactivity/%s && meteor --port %s)\n" %\
									(app, exp_mongo, forwarded_count, mthost, app, mtport))

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
	import os
	from fluorine.utils.reactivity import meteor_config
	from fluorine.utils.meteor.utils import default_path_prefix, PORT
	from fluorine.utils.file import get_path_reactivity, save_js_file

	path_reactivity = get_path_reactivity()
	config_path = os.path.join(path_reactivity, "common_site_config.json")

	f = meteor_config

	if not f.get("meteor_http_forwarded_count"):
		f["meteor_http_forwarded_count"] = "1"

	if not f.get("meteor_dev", None):
		f["meteor_dev"] = {}

	meteor_dev = f.get("meteor_dev")

	if not meteor_dev.get("meteor_web"):
		meteor_dev["meteor_web"] = {}

	meteor_web = meteor_dev.get("meteor_web")

	if not meteor_dev.get("meteor_app"):
		meteor_dev["meteor_app"] = {}

	meteor_app = meteor_dev.get("meteor_app")

	if not meteor_app.get("ROOT_URL_PATH_PREFIX"):
		meteor_app["ROOT_URL_PATH_PREFIX"] = default_path_prefix

	#mtconf.get("meteor_web")["port"] = doc.fluor_meteor_port
	meteor_web["port"] = doc.fluor_meteor_port or 3070
	#mtconf.get("meteor_app")["port"] = PORT["meteor_app"]
	meteor_app["port"] = PORT["meteor_app"]

	#mtconf["host"] = doc.fluor_meteor_host.strip()
	meteor_dev["host"] = doc.fluor_meteor_host.strip() or "http://127.0.0.1"

	#mtconf.get("meteor_app")["ddpurl"] = doc.ddpurl.strip()
	meteor_app["ddpurl"] = doc.ddpurl.strip()

	f["site"] = doc.site.strip() or frappe.local.site
	f["developer_mode"] = doc.fluor_dev_mode


	if doc.check_mongodb and doc.fluor_mongo_host.strip():
		mongo = f.get("meteor_mongo")
		#mgconf["host"] = doc.fluor_mongo_host.strip()
		mongo["host"] = doc.fluor_mongo_host.strip()
		#mgconf["port"] = doc.fluor_mongo_port or 0
		mongo["port"] = doc.fluor_mongo_port or 0
		#mgconf["db"] = doc.fluor_mongo_database
		mongo["db"] = doc.fluor_mongo_database.strip()
	else:
		if f.get("meteor_mongo", None) and not f.get("meteor_mongo").get("type") == "default":
			del f["meteor_mongo"]
		make_mongodb_default(f, meteor_web.get("port"))

	save_js_file(config_path, f)

@frappe.whitelist()
#def make_meteor_file(devmode, mthost, mtport, mtddpurl, mghost, mgport, mgdb, architecture, whatfor):
def make_meteor_file(mthost, mtport, mtddpurl, architecture, whatfor):
	#devmode = frappe.utils.cint(devmode)
	#from frappe.website.context import get_context
	from fluorine.utils.meteor.utils import build_meteor_context, make_meteor_props
	from fluorine.utils.file import make_meteor_file
	#from fluorine.utils.fcache import clear_frappe_caches
	#from fluorine.utils.spacebars_template import get_app_pages, get_web_pages
	#clear_frappe_caches()
	#whatfor = ["common"] if devmode else ["meteor_web", "meteor_app"]
	_whatfor = {"Both": ("meteor_web", "meteor_app"), "Reactive Web": ("meteor_web",), "Reactive App": ("meteor_app",)}

	#prepare_compile_environment()
	for w in _whatfor.get(whatfor):
		#prepare_client_files(w)
		#if whatfor == "Both" and w == "meteor_app":
		#	mtport = int(mtport) + 80
		#	frappe.local.path = "mdesk"
		#	get_context("mdesk")
			#frappe.get_template(context.base_template_path).render(context)
		#else:
		#	frappe.local.path = "fluorine_home"
		#	get_context("fluorine_home")
			#frappe.get_template(context.base_template_path).render(context)

		make_meteor_file(jquery=0, whatfor=w, mtport=mtport, mthost=mthost, architecture=architecture)
		context = frappe._dict()
		build_meteor_context(context, 0, w)
		make_meteor_props(context, w, production=1)

	#TODO REMOVER
	#if "meteor_app" in _whatfor.get(whatfor):
	#	make_final_app_client(meteor_root_url=mthost, meteor_port=int(mtport), meteor_ddpurl=mtddpurl)

	#fluorine_publicjs_path = os.path.join(frappe.get_app_path("fluorine"), "public", "js", "react")
	#file.remove_folder_content(fluorine_publicjs_path)
	#file.make_meteor_config_file(mthost, mtport, version)

	#if devmode:
	#	restart_reactivity(mthost=mthost, mtport=mtport, mghost=mghost, mgport=mgport, mgdb=mgdb)


def prepare_make_meteor_file(mtport, whatfor):
	from frappe.website.context import get_context
	#from fluorine.utils.fcache import clear_frappe_caches
	#clear_frappe_caches()
	_whatfor = {"Both": ("meteor_web", "meteor_app"), "Reactive Web": ("meteor_web",), "Reactive App": ("meteor_app",)}

	prepare_compile_environment()

	for w in _whatfor.get(whatfor):
		prepare_client_files(w)

		if whatfor == "Both" and w == "meteor_app":
			#from fluorine.templates.pages.mdesk import get_context
			mtport = int(mtport) + 10
			frappe.local.path = "mdesk"
			get_context("mdesk")
			#context = frappe._dict()
			#get_context(context)
		else:
			#from fluorine.templates.pages.fluorine_home import get_context
			frappe.local.path = "fluorine_home"
			#context = frappe._dict()
			get_context("fluorine_home")
			#get_context(context)


def prepare_compile_environment():

	#from fluorine.utils.fhooks import change_base_template
	from fluorine.utils.reactivity import meteor_config, list_ignores
	#from fluorine.utils.file import set_config

	#set_config({
	#	"developer_mode": 0
	#})
	#meteor_config["developer_mode"] = 0
	meteor_config["mongodb_users_ready"] = 0

	list_ignores["files_folders"] = {
		"all":{
			"remove": [{"pattern": "highlight/?.*"}]
		}
	}

	#remove_from_procfile()

	#change_base_template(page_default=True)


	#doc = frappe.get_doc("Fluorine Reactivity")
	#doc.fluor_dev_mode = 0
	#doc.fluorine_state = "off"
	#doc.save()

"""
def make_final_app_client(jquery=0, meteor_root_url="http://localhost", meteor_ddpurl="http://localhost", meteor_port=3070):

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
	build_json["css/meteor_app.css"] = []

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
				build_json["css/meteor_app.css"].append(rel)

			frappe.create_folder(os.path.dirname(dst))
			src = os.path.join(meteor_final_path, path)
			copyfile(src, dst)
"""

def prepare_client_files(whatfor):
	from fluorine.utils.react_file_loader import remove_directory
	from fluorine.utils.file import get_path_reactivity
	from shutil import copyfile

	#fluorine_path = frappe.get_app_path("fluorine")
	react_path = get_path_reactivity()
	#meteor_final_path = os.path.join(react_path, "final_%s" % (whatfor.split("_")[1],))
	meteor_final_path = os.path.join(react_path, whatfor.replace("meteor", "final"))
	if os.path.exists(meteor_final_path):
		remove_directory(os.path.join(meteor_final_path, "bundle"))

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

def make_mongodb_default(conf, port=3070):
	if not conf.get("meteor_mongo"):
		import subprocess
		from fluorine.utils import file
		path_reactivity = file.get_path_reactivity()
		meteor_web = os.path.join(path_reactivity, "meteor_web")
		meteor = subprocess.Popen(["meteor", "--port", str(port)], cwd=meteor_web, shell=False, stdout=subprocess.PIPE)
		mongodb = None
		while True:
			line = meteor.stdout.readline()
			if "App running at" in line:
				mongodb = subprocess.check_output(["meteor", "mongo", "-U"], cwd=meteor_web, shell=False)
				meteor.kill()
				break
			print line

		print "result meteor mongo -U {}".format(mongodb)
		if mongodb:
			fs = mongodb.rsplit("/",1)
			hp = fs[0].split("mongodb://")[1].split(":")
			db = fs[1].rstrip() or "fluorine"
			host = hp[0]
			port = hp[1]

			conf["meteor_mongo"] = {
				"host": host,
				"port": port,
				"db": db,
				"type": "default"
			}