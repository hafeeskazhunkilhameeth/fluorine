from __future__ import unicode_literals
__author__ = 'luissaguas'

import os, subprocess
from . import meteor_config

"""
original_get_hooks = frappe.get_hooks

def flourine_get_hooks(hook=None, default=None, app_name=None):
	#print "has hooks called"
	hooks = original_get_hooks(hook, default, app_name)
	if hook == "base_template":
		d = fluor.get_cached_value("hooks_helper")#read_file("hook_help.txt")
		if d and d.get(hook, None):
			hooks.extend(d.get(hook))
			fluor.clear_frappe_caches()
		return hooks

	if not app_name and not hook:
		check_includes('web_include_js', hooks)
		check_includes('app_include_js', hooks)
		d = fluor.get_cached_value("hooks_helper")
		if d and d.get("base_template", None):
			check_jquery('web_include_js', hooks)

	#if app_name == "fluorine":
		#d = file.read_file("hook_help.txt")
		#print "hooks in fluorine {} {}".format(hook, hooks)
		#check_includes('web_include_js', hooks)
		#check_includes('app_include_js', hooks)
		#d = fluor.get_cached_value("hooks_helper")
		#if d and d.get("base_template", None):
		#	check_jquery('web_include_js', hooks)


		#d = fluor.get_cached_value("hooks_helper")
		#if hook in ["app_include_js", "web_include_js", "base_template"]:
		#	if d and d.get(hook, None):
		#		hooks[hook] = d.get(hook)
		#		fluor.clear_frappe_caches()
		#elif not hook:
		#	hooks.update(d)
		#	fluor.clear_frappe_caches()

		#print "get_hooks hooks hooks {}".format(hooks)

	return hooks

frappe.get_hooks = flourine_get_hooks
"""

"""
def run_meteor(path, mthost="http://localhost", mtport=3000, mghost="http://localhost", mgport=27017, mgdb="fluorine", restart=False):
	#if make_meteor_config:
	#make_meteor_config_file(mthost, mtport, version)
	import frappe
	import os
	import signal
	from . import is_open_port, __file__
	if is_open_port() and not restart:
		print "Port {} is open!".format(mtport)
		return

	import copy
	print "Port {} is not open!".format(mtport)
	environ = copy.copy(os.environ)
	if not os.environ.get("FLUOR_METEOR_ROOT_URL", None):
		#os.environ["ROOT_URL"] = "http://localhost"
		environ["ROOT_URL"] = mthost.strip(' \t\n\r')#"http://localhost"
	if not os.environ.get("FLUOR_METEOR_PORT", None):
		#os.environ["PORT"] = str(3000)
		environ["PORT"] = str(mtport)
	if not os.environ.get("FLUOR_MONGO_URL", None):
		#os.environ["MONGO_URL"] = "mongodb://localhost:27017/ekaiser"
		mghost = mghost.replace("http://","").replace("mongodb://","").strip(' \t\n\r')
		environ["MONGO_URL"] = "mongodb://" + mghost + ":" + str(mgport) + "/" + mgdb#"mongodb://localhost:27017/ekaiser"

	environ["ROOT_URL_PATH_PREFIX"] = "/assets/fluorine/meteor_web/webbrowser"#"http://localhost"
	#environ["AUTOUPDATE_VERSION"] = str(version)
	pidfile = os.path.join(os.path.dirname(__file__), "pids.json")
	if restart:
		#TODO - find a way to communicate with the process started with popen
		print "kill react watch "
		if os.path.exists(pidfile):
			f = frappe.get_file_json(pidfile)
			pid = f.get("meteorapp")
			try:
				os.kill(pid, signal.SIGKILL)#signal.SIGQUIT
				print "process with pid {} was killed".format(pid)
			except:
				print "process with pid {} was not killed".format(pid)
		#import zerorpc
		#try:
		#	c = zerorpc.Client()
		#	c.connect("tcp://127.0.0.1:5252")
		#	c.stop_and_exit()
		#except:
		#	print "stop and exit exception"
	#subprocess.Popen(["node", path + "/main.js"], cwd=path, env=os.environ)
	#react = subprocess.Popen(["node", path + "/main.js"], cwd=path, shell=False, close_fds=True, env=environ)
	#react = subprocess.Popen(["node", path + "/rundevserver.js"], cwd=path, shell=False, close_fds=True, env=environ)
	p = subprocess.Popen(["meteor", "--port=" + str(mtport)], cwd=path, shell=False, close_fds=True, env=environ)
	file.save_js_file(pidfile, {"meteorapp": p.pid})
"""
"""
def run_reactivity(path, mthost="http://localhost", mtport=3000, mghost="http://localhost", mgport=27017, mgdb="fluorine", restart=False):
	#if make_meteor_config:
	#make_meteor_config_file(mthost, mtport, version)
	import frappe
	import os
	import signal
	from . import is_open_port, __file__
	if is_open_port() and not restart:
		print "Port is open!"
		return

	import copy
	print "Port is not open!"
	environ = copy.copy(os.environ)
	if not os.environ.get("FLUOR_METEOR_ROOT_URL", None):
		#os.environ["ROOT_URL"] = "http://localhost"
		environ["ROOT_URL"] = mthost.strip(' \t\n\r')#"http://localhost"
	if not os.environ.get("FLUOR_METEOR_PORT", None):
		#os.environ["PORT"] = str(3000)
		environ["PORT"] = str(mtport)
	if not os.environ.get("FLUOR_MONGO_URL", None):
		#os.environ["MONGO_URL"] = "mongodb://localhost:27017/ekaiser"
		mghost = mghost.replace("http://","").replace("mongodb://","").strip(' \t\n\r')
		environ["MONGO_URL"] = "mongodb://" + mghost + ":" + str(mgport) + "/" + mgdb#"mongodb://localhost:27017/ekaiser"

	#environ["AUTOUPDATE_VERSION"] = str(version)
	pidfile = os.path.join(os.path.dirname(__file__), "pids.txt")
	if restart:
		#TODO - find a way to communicate with the process started with popen
		print "kill react watch "
		if os.path.exists(pidfile):
			f = frappe.get_file_json(pidfile)
			pid = f.get("startfluorine")
			try:
				os.kill(pid, signal.SIGKILL)#signal.SIGQUIT
				print "process with pid {} was killed".format(pid)
			except:
				print "process with pid {} was not killed".format(pid)
		#import zerorpc
		#try:
		#	c = zerorpc.Client()
		#	c.connect("tcp://127.0.0.1:5252")
		#	c.stop_and_exit()
		#except:
		#	print "stop and exit exception"
	#subprocess.Popen(["node", path + "/main.js"], cwd=path, env=os.environ)
	#react = subprocess.Popen(["node", path + "/main.js"], cwd=path, shell=False, close_fds=True, env=environ)
	#react = subprocess.Popen(["node", path + "/rundevserver.js"], cwd=path, shell=False, close_fds=True, env=environ)
	p = subprocess.Popen(["python", path + "/startfluorine.py", path + "/app"], cwd=path, shell=False, close_fds=True, env=environ)
	file.save_js_file(pidfile, {"startfluorine": p.pid})

"""


def run_meteor(path, mthost="http://localhost", mtport=3000, mghost="http://localhost", mgport=27017, mgdb="fluorine", restart=False):
	import os, copy
	from . import is_open_port

	if is_open_port() and not restart:
		print "Port {} is open!".format(mtport)
		return

	print "Port {} is not open!".format(mtport)
	environ = copy.copy(os.environ)
	if not os.environ.get("FLUOR_METEOR_ROOT_URL", None):
		environ["ROOT_URL"] = mthost.strip(' \t\n\r')#"http://localhost"
	if not os.environ.get("FLUOR_METEOR_PORT", None):
		environ["PORT"] = str(mtport)
	if not os.environ.get("FLUOR_MONGO_URL", None):
		#os.environ["MONGO_URL"] = "mongodb://localhost:27017/ekaiser"
		mghost = mghost.replace("http://","").replace("mongodb://","").strip(' \t\n\r')
		environ["MONGO_URL"] = "mongodb://" + mghost + ":" + str(mgport) + "/" + mgdb#"mongodb://localhost:27017/ekaiser"

	subprocess.Popen(["meteor", "--port=" + str(mtport)], cwd=path, shell=False, close_fds=True, env=environ)


def start_meteor():
	import frappe
	import file

	path_reactivity = file.get_path_reactivity()

	conf = meteor_config
	meteor = conf.get("meteor_dev") or {}
	mongo = conf.get("meteor_mongo") or {}
	mtport_web = meteor.get("port") or 3000
	mtport_app = mtport_web + 80
	mthost = meteor.get("host") or "http://localhost"
	mghost = mongo.get("host") or "http://localhost"
	mgport = mongo.get("port") or 27017
	mgdb = mongo.get("db") or "fluorine"

	frappesite = conf.get("site")

	extras_context_methods.update(get_extras_context_method(frappesite))

	tostart = {"Both": ("meteor_app", "meteor_web"), "Reactive App": ("meteor_app", ), "Reactive Web": ("meteor_web", )}
	fluorine_recativity = frappe.db.get_value("Fluorine Reactivity", fieldname="fluorine_reactivity")

	frappe.set_user("guest")

	for app in tostart[fluorine_recativity]:
		meteor_path = os.path.join(path_reactivity, app)
		path_meteor = os.path.join(meteor_path, ".meteor")
		mtport = mtport_web if app == "meteor_web" else mtport_app
		if os.path.exists(path_meteor):
			run_meteor(meteor_path, mtport=mtport, mthost=mthost, mghost=mghost, mgport=mgport, mgdb=mgdb)

extras_context_methods = set([])

def get_extras_context_method(site):
	#from fhooks import FrappeContext
	from fluorine.utils.fhooks import get_extras_context

	#try:
	#	make_meteor_ignor_files()
	#	hooks = get_extras_context()
	#except:
	user = "Administrator"
	#with FrappeContext(site, "Administrator") as f:
	frappe.init(site=site)
	frappe.connect()
	frappe.set_user(user)
	make_meteor_ignor_files()
	hooks = get_extras_context()
	#frappe.set_user("guest")
	print "with Frappe Context extra hooks {}!!!".format(hooks)

	return hooks

list_ignores = None

def process_permission_apps(apps):

	list_apps_add = []
	list_apps_remove = []

	for k, v in apps.iteritems():
		if v.get("remove", 0):
			if k not in list_apps_add:
				list_apps_remove.append(k)
		elif v.get("add", 0):
			if k not in list_apps_remove:
				list_apps_add.append(k)

	return list_apps_remove

def process_permission_files_folders(ff):
	from fluorine.utils.fjinja2.utils import c

	list_ff_add = frappe._dict()
	list_ff_remove = frappe._dict()

	for k, v in ff.iteritems():
		remove = v.get("remove") or []
		for r in remove:
			if not list_ff_remove.get(k):
				list_ff_remove[k] = []
			pattern = c(r.get("pattern"))
			list_ff_remove[k].append(pattern)

		add = v.get("add") or []
		for a in add:
			if not list_ff_add.get(k):
				list_ff_add[k] = []
			pattern = c(a.get("pattern"))
			list_ff_add[k].append(pattern)

	return list_ff_add, list_ff_remove

def make_meteor_ignor_files():
	import file
	#from fluorine.utils.fjinja2.fjinja import process_hooks_apps, process_hooks_meteor_templates

	#apps = frappe.get_installed_apps()
	#from file import process_ignores_from_modules#, save_js_file, get_path_reactivity

	#if not frappe.local.meteor_ignores:
	#apps_last_first = apps[::-1]
	path_reactivity = file.get_path_reactivity()
	perm_path = os.path.join(path_reactivity, "permission_files.json")

	if not os.path.exists(perm_path):
		file.save_js_file(perm_path, {"apps":{}, "files_folders":{}})

	conf = frappe.get_file_json(perm_path)

	#list_apps_remove = process_hooks_apps(apps_last_first)
	list_apps_remove = process_permission_apps(conf.get("apps") or {})
	list_meteor_files_folders_add, list_meteor_files_folders_remove = process_permission_files_folders(conf.get("files_folders") or {})
	#list_meteor_files_add, list_meteor_files_remove = process_hooks_meteor_templates(apps_last_first, "fluorine_files_templates")
	#list_meteor_files_folders_add, list_meteor_files_folders_remove = process_hooks_meteor_templates(apps_last_first, "fluorine_files_folders")
	#list_meteor_tplt_add, list_meteor_tplt_remove = process_hooks_meteor_templates(apps_last_first, "fluorine_meteor_templates")

	global list_ignores

	list_ignores = frappe._dict({
		"remove":{
			"apps": list_apps_remove,
			"files_folders": list_meteor_files_folders_remove
		},
		"add":{
			"apps": [],
			"files_folders": list_meteor_files_folders_add
		}
	})

	print "list apps to remove {}".format(list_ignores)

	"""
	list_ignores = frappe._dict({
		"remove":{
			"apps": list_apps_remove,
			"files_folders": list_meteor_files_folders_remove,
			"meteor_files_templates": list_meteor_files_remove,
			"meteor_templates": list_meteor_tplt_remove
		},
		"add":{
			"files_folders": list_meteor_files_folders_add,
			"meteor_files": list_meteor_files_add,
			"meteor_templates": list_meteor_tplt_add
		},
		"templates_to_remove": frappe.local.templates_found_remove,
		"templates_to_add": frappe.local.templates_found_add

	})
	"""

	#this is for teste how it will stay when cached
	#save_js_file(os.path.join(get_path_reactivity(), "teste_list_dump.json"), list_ignores)

	# Process list_ignores from all installed apps.
	# Last installed app process last.
	# In this way last installed app can remove or add what others added or removed
	#apps_last_last = apps
	#process_ignores_from_modules(apps_last_last, "proces_all_meteor_lists", frappe.local.meteor_ignores)

"""
def start_reactivity():
	import frappe
	path = file.get_path_server_observe()
	#file.observe_dir(path)
	print start_hash(path)
	path_reactivity = file.get_path_reactivity()
	#js_path = file.get_path_assets_js()
	js_path = os.path.join(frappe.get_app_path("fluorine"), "public/js")
	meteor_files = ("meteor_common.devel.js", "meteor_app.devel.js", "meteor_web.devel.js", "meteor_app.js", "meteor_web.js")
	boot_file = os.path.join(path_reactivity, "server", "boot.js")
	print "in start_reactivity js_path {} boot_file {} curr path {}".format(js_path, boot_file, os.getcwd())
	for f in meteor_files:
		path_file = os.path.join(js_path, f)
		if os.path.exists(path_file) and os.path.exists(boot_file):
			run_reactivity(path_reactivity)
			break
"""
print "frappe.__file__ 2 {}".format(os.getcwd())

import sys

if any("--serve"==s or "--start"==s for s in sys.argv):
	import frappe
	print "starting reactivity... {}".format(sys.argv)
	#start_reactivity()
	start_meteor()