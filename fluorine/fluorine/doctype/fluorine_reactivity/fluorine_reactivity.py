# Copyright (c) 2013, Luis Fernandes and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, os
from frappe.model.document import Document
from frappe import _


class FluorineReactivity(Document):
	def on_update(self, method=None):
		#from fluorine.utils.file import set_config
		from fluorine.utils.file import save_custom_template
		from fluorine.utils.reactivity import meteor_config

		#if not meteor_config:
		#	from fluorine.utils import get_meteor_configuration_file
		#	meteor_config = get_meteor_configuration_file()

		meteor_config["developer_mode"] = self.fluor_dev_mode #if self.fluorine_state == "on" else 0
		#production_mode = meteor_config.get("production_mode")

		if self.fluorine_state == "off" and self.fluor_dev_mode == 0: #and not production_mode:

			#if meteor_config.get("production_mode"):
			#	from fluorine.utils.reactivity import start_meteor
			#	start_meteor()
				#TODO check if needed to remove
				#set_config({
					#"developer_mode": self.fluor_dev_mode
				#	"developer_mode": 0
				#})
			#prepare_make_meteor_file(self.fluor_meteor_port, self.fluorine_reactivity)
			meteor_config["production_mode"] = 1
			#update_versions()
			#return

		if self.fluorine_base_template and self.fluorine_base_template.lower() != "default":
			save_custom_template(self.fluorine_base_template)

		if self.current_dev_app and self.current_dev_app.strip() != "":
			meteor_config["current_dev_app"] = self.current_dev_app
		#if not self.fluor_dev_mode:
			#prepare_make_meteor_file(self.fluor_meteor_port, self.fluorine_reactivity)
		save_to_common_site_config(self, meteor_config)

		#if self.fluor_dev_mode:
		#	save_to_procfile(self)
		#else:
		#	remove_from_procfile()

	def validate(self, method=None):
		if not self.ddpurl or self.ddpurl.strip() == "":
			return frappe.throw("You must provide a valid ddp url")

		if self.current_dev_app and self.current_dev_app.strip() != "":
			from fluorine.utils import APPS as apps
			#apps = frappe.get_installed_apps()
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
	#from fluorine.utils.reactivity import meteor_config
	#from fluorine.utils.meteor.utils import default_path_prefix, PORT

	procfile, procfile_path = get_procfile()
	tostart = {"Both": ("meteor_app", "meteor_web"), "Reactive App": ("meteor_app", ), "Reactive Web": ("meteor_web", )}
	meteor_apps = tostart.get(doc.fluorine_reactivity)

	"""
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
	"""
	from fluorine.commands_helpers.meteor import get_meteor_settings

	for app in meteor_apps:
		export_mongo, mongo_default = get_mongo_exports(doc)
		mthost, mtport, forwarded_count = get_root_exports(doc, app)

		if production_debug:
			#procfile.insert(0, "%s: (%s%s && export ROOT_URL=%s && export PORT=%s && cd apps/reactivity/%s/bundle && node main.js)\n" %
			#				(app, export_mongo + " && ", forwarded_count, mthost, mtport, app))
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
	#import os
	#from fluorine.utils.reactivity import meteor_config
	from fluorine.utils.meteor.utils import default_path_prefix, PORT, update_common_config
	#from fluorine.utils.file import get_path_reactivity, save_js_file

	#path_reactivity = get_path_reactivity()
	#config_path = os.path.join(path_reactivity, "common_site_config.json")

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
	meteor_web["port"] = doc.fluor_meteor_port or PORT.meteor_web
	#mtconf.get("meteor_app")["port"] = PORT["meteor_app"]
	meteor_app["port"] = PORT["meteor_app"]

	#mtconf["host"] = doc.fluor_meteor_host.strip()
	meteor_dev["host"] = doc.fluor_meteor_host.strip() or "http://127.0.0.1"

	#mtconf.get("meteor_app")["ddpurl"] = doc.ddpurl.strip()
	meteor_app["ddpurl"] = doc.ddpurl.strip()

	f["site"] = doc.site.strip() if doc.site else frappe.local.site
	f["developer_mode"] = doc.fluor_dev_mode


	if doc.check_mongodb and doc.fluor_mongo_host.strip():
		if not f.get("meteor_mongo"):
			f["meteor_mongo"] = {}

		mongo = f.get("meteor_mongo")
		#mgconf["host"] = doc.fluor_mongo_host.strip()
		mongo["host"] = doc.fluor_mongo_host.replace("http://","").replace("mongodb://","").strip(' \t\n\r')
		#mgconf["port"] = doc.fluor_mongo_port or 0
		mongo["port"] = doc.fluor_mongo_port or 0
		#mgconf["db"] = doc.fluor_mongo_database
		mongo["db"] = doc.fluor_mongo_database.strip()
		mongo.pop("type", None)
	#else:
	#	if f.get("meteor_mongo", None): #and not f.get("meteor_mongo").get("type") == "default":
	#		del f["meteor_mongo"]
	#	make_mongodb_default(f, meteor_web.get("port"))

	#save_js_file(config_path, f)
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


#@frappe.whitelist()
#def make_meteor_file(devmode, mthost, mtport, mtddpurl, mghost, mgport, mgdb, architecture, whatfor):


def prepare_make_meteor_file(mtport, whatfor):
	from frappe.website.context import get_context
	#from fluorine.utils.fcache import clear_frappe_caches
	#clear_frappe_caches()
	_whatfor = {"Both": ("meteor_web", "meteor_app"), "Reactive Web": ("meteor_web",), "Reactive App": ("meteor_app",)}

	prepare_compile_environment()

	for w in _whatfor.get(whatfor):
		#prepare_client_files(w)

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
	from fluorine.utils.reactivity import list_ignores#, make_meteor_ignor_files
	#from fluorine.utils.fhooks import change_base_template
	#from fluorine.utils.file import set_config

	#set_config({
	#	"developer_mode": 0
	#})
	#meteor_config["developer_mode"] = 0
	#meteor_config["mongodb_users_ready"] = 0

	#make_meteor_ignor_files()
	#from fluorine.utils.reactivity import list_ignores
	#if not list_ignores:
	#	list_ignores = make_meteor_ignor_files()

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


#def make_final_app_client(jquery=0, meteor_root_url="http://localhost", meteor_ddpurl="http://localhost", meteor_port=3070):
def make_final_app_client(jquery=0):

	import json
	from fluorine.utils.file import get_path_reactivity, read, save_js_file
	#from fluorine.utils.meteor.utils import get_meteor_release, make_auto_update_version, get_meteor_config, save_meteor_props#, save_meteor_root_prefix

	#meteor_ddp_default_connection_url = meteor_ddpurl + (":" + str(meteor_port) if meteor_port > 80 else "")

	#whatfor = "meteor_app"

	#sites_path = os.path.abspath(".")

	react_path = get_path_reactivity()

	meteor_final_path = os.path.join(react_path, "final_app/bundle/programs/web.browser")
	progarm_path = os.path.join(meteor_final_path, "program.json")

	#star_path = os.path.join(react_path, "final_app/bundle/star.json")
	#meteorRelease = get_meteor_release(star_path)
	if os.path.exists(progarm_path):

		fluorine_path = frappe.get_app_path("fluorine")
		#js_path = os.path.join(fluorine_path, "public", "js", "meteor")
		build_file = os.path.join(fluorine_path, "public", "build.json")

		if os.path.exists(build_file):
			build_json_file = read(build_file)
			build_json = json.loads(build_json_file)
		else:
			build_json = frappe._dict()

		build_json["js/meteor_app.min.js"] = ["public/js/meteor_runtime_config.js"]
		build_json["css/meteor_app.css"] = []

		manifest = read(progarm_path)

		manifest = json.loads(manifest).get("manifest")
		#meteor_autoupdate_version, meteor_autoupdate_version_freshable, manifest_js, manifest_css =\
		#	make_auto_update_version(progarm_path, meteorRelease, meteor_root_url, "", whatfor)

		#props = get_meteor_config(meteor_root_url, meteor_ddp_default_connection_url, "", meteor_autoupdate_version,\
		#						meteor_autoupdate_version_freshable, meteorRelease, whatfor)

		#frappe.create_folder(js_path)
		#meteor_runtime_path = os.path.join(js_path, "meteor_runtime_config.js")

		#save_meteor_props(props, meteor_runtime_path)

		#meteor_root_url_prefix_path = os.path.join(js_path, "meteor_url_prefix.js")
		#save_meteor_props("__meteor_runtime_config__.ROOT_URL_PATH_PREFIX = '%s';" % meteor_ddp_default_connection_url, meteor_root_url_prefix)
		#save_meteor_root_prefix(meteor_ddp_default_connection_url, meteor_root_url_prefix_path)

		#rel = os.path.relpath(meteor_runtime_path, fluorine_path)
		#build_json.get("js/meteor_app.js").append("/assets/js/meteor_app/meteor_runtime_config.js")

		build_frappe_json_files(manifest, build_json, jquery=jquery)

		#rel = os.path.relpath(meteor_root_url_prefix_path, fluorine_path)
		#build_json.get("js/meteor_app.js").append(rel)

		save_js_file(build_file, build_json)


def build_frappe_json_files(manifest, build_json, jquery=0):
	#from shutil import copyfile
	from fluorine.utils.file import get_path_reactivity

	react_path = get_path_reactivity()

	for m in manifest:
		if m.get("where") == "client":
			path = m.get("path")
			if "jquery" in path and jquery == 0:
				continue
			#dst = os.path.join(js_path, path)
			#rel = os.path.relpath(dst, fluorine_path)
			pack_path = os.path.join(react_path, "final_app/bundle/programs/web.browser", path)
			if m.get("type") == "js":
				build_json["js/meteor_app.min.js"].append(pack_path)
			else:
				build_json["css/meteor_app.css"].append(pack_path)

			#frappe.create_folder(os.path.dirname(dst))
			#src = os.path.join(meteor_final_path, path)
			#copyfile(src, dst)


def remove_tmp_app_dir(src, dst):
	from fluorine.utils.react_file_loader import remove_directory
	try:
		remove_directory(src)
		remove_directory(dst)
	except:
		pass

def make_mongodb_default(conf, port=3070):
	if is_open_port(port=port):
		frappe.throw("port {} is open, please close. If you change from production then stop supervisor (sudo supervisorctl stop all).".format(port))
		return
	if not conf.get("meteor_mongo"):
		import subprocess
		from fluorine.utils import file
		path_reactivity = file.get_path_reactivity()
		meteor_web = os.path.join(path_reactivity, "meteor_web")
		print "getting mongo config..."
		meteor = subprocess.Popen(["meteor", "--port", str(port)], cwd=meteor_web, shell=False, stdout=subprocess.PIPE)
		mongodb = None
		while True:
			line = meteor.stdout.readline()
			if "App running at" in line:
				mongodb = subprocess.check_output(["meteor", "mongo", "-U"], cwd=meteor_web, shell=False)
				#meteor.kill()
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

	path_reactivity = get_path_reactivity()
	whatfor = doc.fluorine_reactivity
	meteor_web = os.path.join(path_reactivity, "meteor_web", ".meteor")
	meteor_app = os.path.join(path_reactivity, "meteor_app", ".meteor")
	msg = "Please install meteor app first. From command line issue 'bench fluorine create-meteor-apps.'"
	error = False

	web_folder_exist = os.path.exists(meteor_web)
	app_folder_exist = os.path.exists(meteor_app)

	if whatfor == "Both" and not (web_folder_exist and app_folder_exist):
		error = True
	elif whatfor == "Reactive Web" and not web_folder_exist:
		error = True
	elif whatfor == "Reactive App" and not app_folder_exist:
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
