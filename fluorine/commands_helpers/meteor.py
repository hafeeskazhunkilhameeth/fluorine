__author__ = 'luissaguas'


import frappe, click, os
from fluorine.utils import whatfor_all, meteor_desk_app, meteor_web_app


def make_production_link():
	from fluorine.utils.file import get_path_reactivity

	path_reactivity = get_path_reactivity()
	final_web_path = os.path.join(path_reactivity, meteor_web_app.replace("meteor", "final"), "bundle", "programs", "web.browser")
	meteor_web_path = os.path.join("assets", "js", meteor_web_app)
	if os.path.exists(final_web_path):
		try:
			os.symlink(final_web_path, meteor_web_path)
		except:
			pass


def make_public_folders():

	app_path = frappe.get_app_path("fluorine")
	for whatfor in (meteor_desk_app, ):#("meteor_app", "meteor_web"):
		public_app_folder = os.path.join(app_path, "public", whatfor)
		frappe.create_folder(public_app_folder)

def copy_meteor_runtime_config():
	from shutil import copyfile

	app_path = frappe.get_app_path("fluorine")
	public_folder = os.path.join(app_path, "public")
	meteor_runtime_file = os.path.join(public_folder, meteor_desk_app, "meteor_runtime_config.js")
	copyfile(meteor_runtime_file, os.path.join(public_folder, "js", "meteor_runtime_config.js"))



def get_meteor_app_files():
	from shutil import copyfile

	meteor_app_path = os.path.join("assets", "js", meteor_desk_app)
	meteordesk_path = os.path.join(meteor_app_path, "meteordesk")
	app_include_js = []
	app_include_css = []

	if os.path.exists(meteordesk_path):
		app_include_js.append("assets/js/%s/meteor_runtime_config.js" % meteor_desk_app)
		progfile = frappe.get_file_json(os.path.join(meteordesk_path, "program.json"))
		manifest = progfile.get("manifest")
		for obj in manifest:
			if obj.get("type") == "js" and obj.get("where") == "client":
				app_include_js.append("assets/js/%s/meteordesk%s" % (meteor_desk_app, obj.get("url")))#+ obj.get("url"))
			elif obj.get("type") == "css" and obj.get("where") == "client":
				app_include_css.append("assets/js/%s/meteordesk%s" % (meteor_desk_app, obj.get("url")))

		fluorine_path = frappe.get_app_path("fluorine")
		src = os.path.join(fluorine_path, "public", meteor_desk_app, "meteor_runtime_config.js")
		dst = os.path.join(meteor_app_path, "meteor_runtime_config.js")
		copyfile(src, dst)

	return app_include_js, app_include_css


#Run npm install for meteor server
def run_npm():
	from fluorine.utils.file import get_path_reactivity
	import subprocess

	path_reactivity = get_path_reactivity()
	final_app_path = os.path.join(path_reactivity, meteor_desk_app.replace("meteor", "final"), "bundle", "programs", "server")
	final_web_path = os.path.join(path_reactivity, meteor_web_app.replace("meteor", "final"), "bundle", "programs", "server")
	click.echo("npm install meteor server Desk APP")
	subprocess.call(["npm", "install"], cwd=final_app_path)
	click.echo("npm install meteor server WEB")
	subprocess.call(["npm", "install"], cwd=final_web_path)


def make_start_meteor_script(doc):
	from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import get_mongo_exports, get_root_exports
	from fluorine.utils.file import get_path_reactivity, save_file
	from distutils.spawn import find_executable
	import stat

	#tostart = {"Both": ("meteor_app", "meteor_web"), "Reactive App": ("meteor_app", ), "Reactive Web": ("meteor_web", )}
	#meteor_apps = tostart.get(doc.fluorine_reactivity)

	react_path = get_path_reactivity()

	node = find_executable("node") or find_executable("nodejs")

	for app in whatfor_all:#("meteor_app", "meteor_web"):
		meteor_final_path = os.path.join(react_path, app.replace("meteor", "final"), "bundle/exec_meteor")
		exp_mongo, mongo_default = get_mongo_exports(doc)
		mthost, mtport, forwarded_count = get_root_exports(doc, app)
		msf = get_meteor_settings(app, production=True)
		if msf:
			msf = "export %s" % msf
		script =\
"""#!/usr/bin/env bash
export ROOT_URL=%s
export PORT=%s
%s
%s
%s

%s main.js""" % (mthost, mtport, forwarded_count, exp_mongo, msf, node)
		save_file(meteor_final_path, script)

		st = os.stat(meteor_final_path)
		os.chmod(meteor_final_path, st.st_mode | stat.S_IEXEC)


def get_meteor_settings(app, production=False):
	from fluorine.utils import meteor_config
	from fluorine.utils.file import readlines

	msf=""
	msfile = meteor_config.get("meteor_settings", {}).get(app)
	content = ""
	if production and msfile:
		if os.path.exists(msfile):
			lines = readlines(msfile)
			for line in lines:
				content = content + line.strip(" \t\n\r")
			msf = "METEOR_SETTINGS='%s'" % content
	elif msfile:
		msf = " --settings %s" % msfile

	return msf


def get_meteor_environment(doc, whatfor):
	from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import get_mongo_exports, get_root_exports

	conf = frappe._dict()

	#METEOR MAIL
	if hasattr(doc, "mailurl"):
		conf.mail_url = ", MAIL_URL='{mail_url}'".format(doc.mailurl)
	else:
		conf.mail_url = ""

	mongo_url, mongo_default = get_mongo_exports(doc)

	conf.mongo_url = mongo_url.strip().replace("export MONGO_URL=", "")
	conf.root_url, conf.port, forwarded_count = get_root_exports(doc, whatfor)
	conf.forwarded_count = forwarded_count.replace("export", "").strip()
	msettings = get_meteor_settings(whatfor, production=True)
	if msettings:
		conf.msettings = "%s, " % msettings
	else:
		conf.msettings = ""

	#SUPERVISOR
	env = "{msettings}PORT={port}, ROOT_URL='{root_url}', MONGO_URL='{mongo_url}'{mail_url}, {forwarded_count}".format(**conf)

	return env


def remove_public_link():
	from fluorine.utils.react_file_loader import remove_directory
	app_path = frappe.get_app_path("fluorine")
	public_folder = os.path.join(app_path, "public")

	for app in (meteor_desk_app, ):
		folder = os.path.join(public_folder, app)
		remove_directory(folder)

"""
def make_public_link():

	app_path = frappe.get_app_path("fluorine")
	public_folder = os.path.join(app_path, "public")

	for app in (meteor_desk_app, ):
		folder = os.path.join(public_folder, app)
		frappe.create_folder(folder)
"""

def remove_from_assets():
	try:
		meteor_path = os.path.join("assets", "js", meteor_web_app)
		os.unlink(meteor_path)
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

	active_apps = []
	for app in apps:
		app_path = frappe.get_app_path(app)
		meteor_app = os.path.join(app_path, "templates", "react", meteor_desk_app)
		meteor_web = os.path.join(app_path, "templates", "react", meteor_web_app)
		if (os.path.exists(meteor_app) or os.path.exists(meteor_web)) and app not in ign_apps:
			active_apps.append(app)

	return active_apps


def check_updates(bench=".."):
	from fluorine.utils.reactivity import meteor_config
	from bench_helpers import get_current_version
	import semantic_version

	apps = get_active_apps()
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


def meteor_run(app, app_path, mongo_custom=False):
	from fluorine.utils.meteor.utils import PORT
	from fluorine.utils.reactivity import meteor_config
	import subprocess, shlex


	print "starting meteor..."
	env = None
	if mongo_custom:
		mongo_conf = meteor_config.get("meteor_mongo", None)
		if mongo_conf and mongo_conf.get("type", None) != "default":
			db = mongo_conf.get("db").strip(' \t\n\r')
			host = mongo_conf.get("host").replace("http://","").replace("mongodb://","").strip(' \t\n\r')
			mgport = mongo_conf.get("port")
			env = os.environ.copy()
			env["MONGO_URL"] = "mongodb://%s:%s/%s" % (host, mgport, db)

	args = shlex.split("meteor --port %s" % PORT.get(app))
	meteor = subprocess.Popen(args, cwd=app_path, shell=False, stdout=subprocess.PIPE, env=env)
	while True:
		line = meteor.stdout.readline()
		if "App running at" in line:
			meteor.terminate()
			break
		click.echo(line)


def meteor_init(mongo_custom=False):
	from fluorine.utils.file import get_path_reactivity

	for app in whatfor_all:#("meteor_app", "meteor_web"):
		app_path = os.path.join(get_path_reactivity(), app)
		program_json_path = os.path.join(app_path, ".meteor", "local", "build", "programs", "web.browser", "program.json")
		if not os.path.exists(program_json_path):
			try:
				meteor_run(app, app_path, mongo_custom=mongo_custom)
			except Exception as e:
				click.echo("You have to start meteor at hand before start meteor. Issue `meteor` in %s. Error: %s" % (app_path, e))
				return


def make_context(doc):
	from fluorine.utils import prepare_environment
	from fluorine.utils.reactivity import start_meteor
	from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import prepare_make_meteor_file

	make_public_folders()
	prepare_environment()
	start_meteor()
	frappe.local.request = frappe._dict()
	prepare_make_meteor_file(doc.fluor_meteor_port, "Both")

