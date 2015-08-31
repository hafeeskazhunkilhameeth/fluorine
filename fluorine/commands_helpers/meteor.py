__author__ = 'luissaguas'


import frappe, click, os


def make_production_link():
	from fluorine.utils.file import get_path_reactivity

	path_reactivity = get_path_reactivity()
	#final_app_path = os.path.join(path_reactivity, "final_app", "bundle", "programs", "web.browser")
	#meteordesk_path = os.path.join(os.path.abspath("."), "assets", "js", "meteor_app", "meteordesk")
	#if os.path.exists(final_app_path) and not os.path.exists(meteordesk_path):
	#	frappe.create_folder(os.path.join(os.path.abspath("."), "assets", "js", "meteor_app"))
	#	os.symlink(final_app_path, meteordesk_path)

	final_web_path = os.path.join(path_reactivity, "final_web", "bundle", "programs", "web.browser")
	#meteor_web_path = os.path.join(os.path.abspath("."), "assets", "js", "meteor_web")
	meteor_web_path = os.path.join("assets", "js", "meteor_web")
	if os.path.exists(final_web_path):
		try:
			os.symlink(final_web_path, meteor_web_path)
		except:
			pass


def make_public_folders():

	for whatfor in ("meteor_app", "meteor_web"):
		app_path = frappe.get_app_path("fluorine")
		public_app_folder = os.path.join(app_path, "public", whatfor)
		frappe.create_folder(public_app_folder)

def copy_meteor_runtime_config():
	from shutil import copyfile

	app_path = frappe.get_app_path("fluorine")
	public_folder = os.path.join(app_path, "public")
	meteor_runtime_file = os.path.join(public_folder, "meteor_app", "meteor_runtime_config.js")
	copyfile(meteor_runtime_file, os.path.join(public_folder, "js", "meteor_runtime_config.js"))



def get_meteor_app_files():
	from shutil import copyfile

	#meteor_app_path = os.path.join(os.path.abspath("."), "assets", "js", "meteor_app")
	meteor_app_path = os.path.join("assets", "js", "meteor_app")
	meteordesk_path = os.path.join(meteor_app_path, "meteordesk")
	app_include_js = []
	app_include_css = []

	if os.path.exists(meteordesk_path):
		app_include_js.append("assets/js/meteor_app/meteor_runtime_config.js")
		progfile = frappe.get_file_json(os.path.join(meteordesk_path, "program.json"))
		manifest = progfile.get("manifest")
		for obj in manifest:
			if obj.get("type") == "js" and obj.get("where") == "client":
				app_include_js.append("assets/js/meteor_app/meteordesk" + obj.get("url"))
			elif obj.get("type") == "css" and obj.get("where") == "client":
				app_include_css.append("assets/js/meteor_app/meteordesk" + obj.get("url"))

		fluorine_path = frappe.get_app_path("fluorine")
		src = os.path.join(fluorine_path, "public", "meteor_app", "meteor_runtime_config.js")
		dst = os.path.join(meteor_app_path, "meteor_runtime_config.js")
		copyfile(src, dst)

	return app_include_js, app_include_css


#Run npm install for meteor server
def run_npm():
	from fluorine.utils.file import get_path_reactivity
	import subprocess

	path_reactivity = get_path_reactivity()
	final_app_path = os.path.join(path_reactivity, "final_app", "bundle", "programs", "server")
	final_web_path = os.path.join(path_reactivity, "final_web", "bundle", "programs", "server")
	click.echo("npm install meteor server Desk APP")
	subprocess.call(["npm", "install"], cwd=final_app_path)
	click.echo("npm install meteor server WEB")
	subprocess.call(["npm", "install"], cwd=final_web_path)


def make_start_meteor_script(doc):
	from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import get_mongo_exports, get_root_exports
	from fluorine.utils.file import get_path_reactivity, save_file
	from distutils.spawn import find_executable
	import stat#, platform

	tostart = {"Both": ("meteor_app", "meteor_web"), "Reactive App": ("meteor_app", ), "Reactive Web": ("meteor_web", )}
	meteor_apps = tostart.get(doc.fluorine_reactivity)

	react_path = get_path_reactivity()

	#if not platform.system() == 'Darwin':
	node = find_executable("node") or find_executable("nodejs")

	for app in meteor_apps:
		meteor_final_path = os.path.join(react_path, app.replace("meteor", "final"), "bundle/exec_meteor")
		exp_mongo, mongo_default = get_mongo_exports(doc)
		mthost, mtport, forwarded_count = get_root_exports(doc, app)
		script =\
"""#!/usr/bin/env bash
export ROOT_URL=%s
export PORT=%s
%s
%s
%s main.js""" % (mthost, mtport, forwarded_count, exp_mongo, node)
		save_file(meteor_final_path, script)

		st = os.stat(meteor_final_path)
		os.chmod(meteor_final_path, st.st_mode | stat.S_IEXEC)


def get_meteor_environment(doc, whatfor):
	from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import get_mongo_exports, get_root_exports
	#from fluorine.utils.meteor.utils import default_path_prefix, PORT
	#from fluorine.utils.file import get_path_reactivity


	conf = frappe._dict()

	#CONFIG FILE
	#path_reactivity = get_path_reactivity()
	#meteor_config = frappe.get_file_json(os.path.join(path_reactivity, "common_site_config.json"))

	#METEOR MAIL
	if hasattr(doc, "mailurl"):
		conf.mail_url = ", MAIL_URL='{mail_url}'".format(doc.mailurl)
	else:
		conf.mail_url = ""

	#MONGODB
	"""
	mongodb_conf = meteor_config.get("meteor_mongo")
	if mongodb_conf and mongodb_conf.get("type") != "default":
		user_pass = "%s:%s@" % (doc.mongo_user, doc.mongo_pass) if doc.mongo_user and doc.mongo_pass else ''
		mghost = doc.fluor_mongo_host.replace("http://","").replace("mongodb://","").strip(' \t\n\r')
		mgport = doc.fluor_mongo_port
		dbname = doc.fluor_mongo_database
	else:
		user_pass = ''
		mghost = "127.0.0.1"
		mgport = 27017
		dbname = "fluorine"

	conf.mongo_url = "mongodb://{user_pass}{host}:{port}/{databasename}".format(user_pass=user_pass, host=mghost, port=mgport, databasename=dbname)
	"""
	mongo_url, mongo_default = get_mongo_exports(doc)

	conf.mongo_url = mongo_url.strip().replace("export MONGO_URL=", "")
	#METEOR
	"""
	mthost = doc.fluor_meteor_host.strip() or "http://127.0.0.1"
	port = doc.fluor_meteor_port or PORT.meteor_web
	conf.port = port if whatfor == "meteor_web" else PORT.meteor_app
	default_prefix = default_path_prefix if whatfor=="meteor_app" else ""
	meteor_dev = meteor_config.get("meteor_dev", None)
	meteor = meteor_dev.get(whatfor)
	prefix = meteor.get("ROOT_URL_PATH_PREFIX") or ""
	conf.root_url = mthost + (prefix if prefix else default_prefix)

	#NGINX
	count = meteor_config.get("meteor_http_forwarded_count") or "1"
	conf.forwarded_count = ", HTTP_FORWARDED_COUNT='" + str(count) + "'"
	"""
	conf.root_url, conf.port, forwarded_count = get_root_exports(doc, whatfor)
	conf.forwarded_count = forwarded_count.replace("export", "").strip()
	#SUPERVISOR
	env = "PORT={port}, ROOT_URL='{root_url}', MONGO_URL='{mongo_url}'{mail_url}, {forwarded_count}".format(**conf)

	return env


def remove_public_link():
	from fluorine.utils.react_file_loader import remove_directory
	app_path = frappe.get_app_path("fluorine")
	public_folder = os.path.join(app_path, "public")

	for app in ("meteor_app", "meteor_web"):
		folder = os.path.join(public_folder, app)
		#if os.path.exists(folder):
		#	link_name = os.path.join(folder, "webbrowser")
		remove_directory(folder)


def make_public_link():
	#from fluorine.utils.file import get_path_reactivity

	#CONFIG FILE
	#path_reactivity = get_path_reactivity()

	app_path = frappe.get_app_path("fluorine")
	public_folder = os.path.join(app_path, "public")

	for app in ("meteor_app", "meteor_web"):
		folder = os.path.join(public_folder, app)
		if not os.path.exists(folder):
			frappe.create_folder(folder)
			#source = os.path.join(path_reactivity, app, ".meteor", "local", "build", "programs", "web.browser")
			#link_name = os.path.join(folder, "webbrowser")
			#os.symlink(source, link_name)

def remove_from_assets():
	from fluorine.utils.react_file_loader import remove_directory
	#app_path = frappe.get_app_path("fluorine")
	#meteor_web_path = os.path.join(os.path.abspath("."), "assets", "js", "meteor_web")

	#for app in ("meteor_app", "meteor_web"):
	try:
		#meteor_path = os.path.join(os.path.abspath("."), "assets", "js", "meteor_app")
		#remove_directory(meteor_path)
		#meteor_path = os.path.join(os.path.abspath("."), "assets", "js", "meteor_web")
		meteor_path = os.path.join("assets", "js", "meteor_web")
		#remove_directory(meteor_path)
		os.unlink(meteor_path)
		#remove_directory(os.path.join(os.path.abspath("."), "assets", "js", "packages"))
		#os.unlink(os.path.join(os.path.abspath("."), "assets", "js", "program.json"))
	except:
		pass


def is_valid_fluorine_app(app):

	apps = get_active_apps()
	if app not in apps:
		return False

	return True


def get_active_apps():
	from fluorine.utils import APPS as apps
	from fluorine.utils.reactivity import make_meteor_ignor_files

	ign_files = make_meteor_ignor_files()

	ign_apps = ign_files.remove.get("apps")

	#apps = frappe.get_installed_apps()
	active_apps = []
	for app in apps:
		app_path = frappe.get_app_path(app)
		meteor_app = os.path.join(app_path, "templates", "react", "meteor_app")
		meteor_web = os.path.join(app_path, "templates", "react", "meteor_web")
		#print "not exists {} app {} web {} app in {}".format(app, os.path.exists(meteor_app), os.path.exists(meteor_web), app in ign_apps)
		#if not (os.path.exists(meteor_app) or os.path.exists(meteor_web)) or app in ign_apps:
		if (os.path.exists(meteor_app) or os.path.exists(meteor_web)) and app not in ign_apps:
			#apps.remove(app)
			active_apps.append(app)

	return active_apps


def check_updates(bench=".."):
	from fluorine.utils.reactivity import meteor_config
	from bench_helpers import get_current_version
	#from fluorine.utils.file import get_path_reactivity
	import semantic_version

	apps = get_active_apps()
	#path_reactivity = get_path_reactivity()
	#config_file_path = os.path.join(path_reactivity, "common_site_config.json")
	#config_file = frappe.get_file_json(config_file_path)
	versions = meteor_config.get("versions")

	if not versions:
		return False

	for app in apps:
		curr_version = get_current_version(app, bench=bench)
		old_version = versions.get(app, None)
		if not old_version or curr_version > semantic_version.Version(old_version):
			return True


	return False

def update_versions(bench=".."):
	from bench_helpers import get_current_version
	from fluorine.utils.reactivity import meteor_config
	from fluorine.utils.meteor.utils import update_common_config

	apps = get_active_apps()

	meteor_config.pop("versions", None)
	versions = meteor_config["versions"] = frappe._dict()

	for app in apps:
		version = get_current_version(app, bench=bench)
		versions[app] = str(version)

	update_common_config(meteor_config)


def meteor_run(app, app_path, port=3070, mongo_custom=False):
	from fluorine.utils.meteor.utils import PORT
	from fluorine.utils.reactivity import meteor_config
	import subprocess, shlex

	#mongo_url = ""
	print "starting meteor..."
	env = None
	if mongo_custom:
		mongo_conf = meteor_config.get("meteor_mongo", None)
		if mongo_conf and mongo_conf.get("type", None) != "default":
			db = mongo_conf.get("db").strip(' \t\n\r')
			host = mongo_conf.get("host").replace("http://","").replace("mongodb://","").strip(' \t\n\r')
			port = mongo_conf.get("port")
			env = os.environ.copy()
			env["MONGO_URL"] = "mongodb://%s:%s/%s" % (host, port, db)

	args = shlex.split("meteor --port %s" % PORT.get(app))
	#click.echo("meteor command {}".format(args))
	meteor = subprocess.Popen(args, cwd=app_path, shell=False, stdout=subprocess.PIPE, env=env)
	while True:
		line = meteor.stdout.readline()
		if "App running at" in line:
			meteor.terminate()
			break
		click.echo(line)


def meteor_init(doc, devmode, state, site=None, mongo_custom=False, bench=".."):
	from fluorine.utils.file import get_path_reactivity
	from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import save_to_procfile, make_mongodb_default, check_meteor_apps_created
	from fluorine.utils.meteor.utils import PORT, update_common_config
	from fluorine.utils.reactivity import meteor_config

	for app in ("meteor_app", "meteor_web"):
		app_path = os.path.join(get_path_reactivity(), app)
		program_json_path = os.path.join(app_path, ".meteor", "local", "build", "programs", "web.browser", "program.json")
		if not os.path.exists(program_json_path):
			try:
				meteor_run(app, app_path, port=PORT.get(app), mongo_custom=mongo_custom)
			except Exception as e:
				click.echo("You have to start meteor at hand before start meteor. Issue `meteor` in %s. Error: %s" % (app_path, e))
				return

	from fluorine.utils.reactivity import start_meteor
	from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import prepare_make_meteor_file

	start_meteor()
	frappe.local.request = frappe._dict()
	prepare_make_meteor_file(doc.fluor_meteor_port, doc.fluorine_reactivity)