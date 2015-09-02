# Copyright (c) 2013, Luis Fernandes and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, os
from frappe.model.document import Document
from frappe import _


class FluorineReactivity(Document):

	def on_update(self, method=None):
		#from fluorine.utils.file import save_custom_template
		from fluorine.utils.reactivity import meteor_config

		meteor_config["developer_mode"] = self.fluor_dev_mode

		#if self.fluorine_state == "off" and self.fluor_dev_mode == 0:
		#	meteor_config["production_mode"] = 1

		#if self.fluorine_base_template and self.fluorine_base_template.lower() != "default":
		#	save_custom_template(self.fluorine_base_template)

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


def get_root_exports(doc, app):
	from fluorine.utils.reactivity import meteor_config
	from fluorine.utils.meteor.utils import default_path_prefix, PORT

	meteor_dev = meteor_config.get("meteor_dev", None)
	count = meteor_config.get("meteor_http_forwarded_count") or "1"
	forwarded_count = "export HTTP_FORWARDED_COUNT='" + str(count) + "'"
	if meteor_dev:
		meteor = meteor_dev.get(app)
		default_prefix = default_path_prefix if app=="meteor_app" else ""
		prefix = meteor.get("ROOT_URL_PATH_PREFIX") or ""
		mthost = meteor_dev.get("host") + (prefix if prefix else default_prefix)
		mtport = meteor.get("port") or PORT.get(app)

		return (mthost, mtport, forwarded_count)

def get_mongo_exports(doc):
	from fluorine.utils.reactivity import meteor_config

	mongo_default = False
	if doc.check_mongodb and doc.fluor_mongo_host.strip():
		user_pass = "%s:%s@" % (doc.mongo_user, doc.mongo_pass) if doc.mongo_user and doc.mongo_pass else ''
		mghost = doc.fluor_mongo_host.replace("http://","").replace("mongodb://","").strip(' \t\n\r')
		export_mongo = "export MONGO_URL=mongodb://%s%s:%s/%s " % (user_pass, mghost, doc.fluor_mongo_port, doc.fluor_mongo_database)
	else:
		mongo_conf = meteor_config.get("meteor_mongo")
		db = mongo_conf.get("db") or "fluorine"
		port = mongo_conf.get("port") or 27017
		host = mongo_conf.get("host") or "127.0.0.1"
		export_mongo = "export MONGO_URL=mongodb://%s:%s/%s " % (host.replace("http://","").replace("mongodb://","").strip(' \t\n\r'), port, db)
		mongo_default = True

	return export_mongo, mongo_default


def save_to_procfile(doc, production_debug=False):
	from fluorine.utils.file import writelines

	procfile, procfile_path = get_procfile()
	#tostart = {"Both": ("meteor_app", "meteor_web"), "Reactive App": ("meteor_app", ), "Reactive Web": ("meteor_web", )}
	#meteor_apps = tostart.get(doc.fluorine_reactivity)

	from fluorine.commands_helpers.meteor import get_meteor_settings

	for app in ("meteor_app", "meteor_web"):
		export_mongo, mongo_default = get_mongo_exports(doc)
		mthost, mtport, forwarded_count = get_root_exports(doc, app)

		if production_debug:
			final_app = app.replace("meteor", "final")
			procfile.insert(0, "%s: (cd apps/reactivity/%s/bundle && ./exec_meteor)\n" %
							(final_app, final_app))
		else:
			if app == "meteor_web" and mongo_default:
				exp_mongo = ""
			else:
				exp_mongo = export_mongo + " && "

			msf= get_meteor_settings(app)
			procfile.insert(0, "%s: (%s%s && export ROOT_URL=%s && cd apps/reactivity/%s && meteor --port %s%s)\n" %
							(app, exp_mongo, forwarded_count, mthost, app, mtport, msf))

		writelines(procfile_path, procfile)


def get_procfile():
	from fluorine.utils.file import readlines
	from fluorine.utils.fjinja2.utils import c

	re_meteor_procfile = c(r"^(meteor_app:|meteor_web:|final_app:|final_web:)")
	procfile_dir = os.path.normpath(os.path.join(os.getcwd(), ".."))
	procfile_path = os.path.join(procfile_dir, "Procfile")

	procfile = readlines(procfile_path)
	procfile = [p for p in procfile if not re_meteor_procfile.match(p)]

	return procfile, procfile_path

def remove_from_procfile():
	from fluorine.utils.file import writelines

	procfile, procfile_path = get_procfile()
	writelines(procfile_path, procfile)


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
def prepare_to_update():
	from fluorine.utils.reactivity import meteor_config
	from fluorine.utils.meteor.utils import update_common_config
	from fluorine.commands import add_meteor_packages
	from fluorine.commands_helpers.meteor import update_versions, check_updates

	doc = frappe.get_doc("Fluorine Reactivity")

	check_meteor_apps_created(doc)
	bench = "../../bench-repo/"

	if not check_updates(bench=bench):
		frappe.throw(_("Sorry, There is no updates."))

	if doc.fluorine_state == "off" and doc.fluor_dev_mode == 0:
		update_versions(bench=bench)
		prepare_make_meteor_file(doc.fluor_meteor_port, doc.fluorine_reactivity)
		meteor_config["on_update"] = 1
		add_meteor_packages()
		update_common_config(meteor_config)
	else:
		frappe.throw(_("Please set state off and/or developer mode off first."))


def prepare_make_meteor_file(mtport, whatfor):
	#from frappe.website.context import get_context
	from fluorine.templates.pages.fluorine_home import get_context as fluorine_get_context
	from fluorine.utils import whatfor_all, meteor_desk_app, meteor_web_app, fluor_get_context as get_context

	_whatfor = {"Both": whatfor_all, "Reactive Web": (meteor_web_app,), "Reactive App": (meteor_desk_app,)}


	prepare_compile_environment()

	for w in _whatfor.get(whatfor):
		if whatfor == "Both" and w == meteor_desk_app:
			#mtport = int(mtport) + 10
			frappe.local.path = "desk"
			get_context("desk")
		else:
			#frappe.local.path = "fluorine_home"
			#get_context("fluorine_home")
			fluorine_get_context(frappe._dict())


def prepare_compile_environment():
	from fluorine.utils.reactivity import meteor_config
	from fluorine.utils.reactivity import list_ignores

	if meteor_config and meteor_config.get("production_mode"):
		list_ignores["files_folders"] = {
			"all":{
				"remove": [{"pattern": "highlight/?.*"}]
			}
		}


def make_final_app_client(jquery=0):
	import json
	from fluorine.utils.file import get_path_reactivity, read, save_js_file
	from fluorine.utils import meteor_desk_app

	react_path = get_path_reactivity()

	meteor_final_path = os.path.join(react_path, "final_app/bundle/programs/web.browser")
	progarm_path = os.path.join(meteor_final_path, "program.json")

	if os.path.exists(progarm_path):

		fluorine_path = frappe.get_app_path("fluorine")
		build_file = os.path.join(fluorine_path, "public", "build.json")

		if os.path.exists(build_file):
			build_json_file = read(build_file)
			build_json = json.loads(build_json_file)
		else:
			build_json = frappe._dict()

		build_json["js/meteor_app.min.js"] = ["public/%s/meteor_runtime_config.js" % meteor_desk_app]
		build_json["css/meteor_app.css"] = []

		manifest = read(progarm_path)

		manifest = json.loads(manifest).get("manifest")

		build_frappe_json_files(manifest, build_json, jquery=jquery)

		save_js_file(build_file, build_json)


def build_frappe_json_files(manifest, build_json, jquery=0):
	from fluorine.utils.file import get_path_reactivity

	react_path = get_path_reactivity()

	for m in manifest:
		if m.get("where") == "client":
			path = m.get("path")
			if "jquery" in path and jquery == 0:
				continue

			pack_path = os.path.join(react_path, "final_app/bundle/programs/web.browser", path)
			type = m.get("type") == "js"
			if type:
				build_json["js/meteor_app.min.js"].append(pack_path)
			elif type == "css":
				build_json["css/meteor_app.css"].append(pack_path)


def remove_tmp_app_dir(src, dst):
	from fluorine.utils.react_file_loader import remove_directory
	try:
		remove_directory(src)
		remove_directory(dst)
	except:
		pass

def make_mongodb_default(conf, port=3070):
	from fluorine.utils import meteor_web_app

	if is_open_port(port=port):
		frappe.throw("port {} is open, please close. If you change from production then stop supervisor (sudo supervisorctl stop all).".format(port))
		return
	if not conf.get("meteor_mongo"):
		import subprocess
		from fluorine.utils import file
		path_reactivity = file.get_path_reactivity()
		meteor_web = os.path.join(path_reactivity, meteor_web_app)
		print "getting mongo config..."
		meteor = subprocess.Popen(["meteor", "--port", str(port)], cwd=meteor_web, shell=False, stdout=subprocess.PIPE)
		mongodb = None
		while True:
			line = meteor.stdout.readline()
			if "App running at" in line:
				mongodb = subprocess.check_output(["meteor", "mongo", "-U"], cwd=meteor_web, shell=False)
				meteor.terminate()
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

def check_meteor_apps_created(doc, with_error=True):
	from fluorine.utils.file import get_path_reactivity
	from frappe import _
	from fluorine.utils import meteor_desk_app, meteor_web_app

	path_reactivity = get_path_reactivity()
	meteor_web = os.path.join(path_reactivity, meteor_web_app, ".meteor")
	meteor_app = os.path.join(path_reactivity, meteor_desk_app, ".meteor")
	msg = "Please install meteor app first. From command line issue 'bench fluorine create-meteor-apps.'"
	error = False

	web_folder_exist = os.path.exists(meteor_web)
	app_folder_exist = os.path.exists(meteor_app)

	if not (web_folder_exist and app_folder_exist):
		error = True

	if with_error and error:
		frappe.throw(_(msg))

	return not error

def is_open_port(ip="127.0.0.1", port=3070):
	import socket
	is_open = False
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	result = sock.connect_ex((ip,port))
	if result == 0:
		is_open = True
	sock.close()
	return is_open
