from __future__ import unicode_literals
__author__ = 'luissaguas'

import os, subprocess
from fluorine.utils import start_hash
import file
import fcache


def check_jquery(hook, hooks):
	found = False
	iweb = hooks.get(hook, None)
	for a in ("jquery.min.js", "jquery.js"):
		if iweb and any(a in s for s in iweb):
			found = True
			break
	if not found:
		iweb.insert(0, "/assets/frappe/js/lib/jquery/jquery.min.js")
		print "jquery not found, inserting frappe jquery!"


def check_includes(hook, hooks):
	iweb = hooks.get(hook, None)
	if iweb and not any("before_fluorine_helper" in s for s in iweb):
		update_includes(hook,iweb)
	elif iweb:
		to_remove = []
		for include in iweb:
			if "before_fluorine_helper" in include or "after_fluorine_helper" in include:
				to_remove.append(include)
		for i in to_remove:
			iweb.remove(i)
		update_includes(hook, iweb)


def update_includes(hook, iweb):
	#d = file.read_file("hook_help.txt")
	d = fcache.get_cached_value("hooks_helper")

	if not d:
		return

	fweb = d.get(hook, None)
	if fweb:
		iweb.insert(0, fweb[0])
		iweb.insert(1, fweb[1])
		if fweb[2:]:
			iweb.extend(fweb[2:])
		fcache.clear_frappe_caches()
	#print "hooks {} name {}".format(iweb, hook)

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

def run_reactivity(path, version, mthost="http://localhost", mtport=3000, mghost="http://localhost", mgport=27017, mgdb="fluorine", restart=False):
	#if make_meteor_config:
	#make_meteor_config_file(mthost, mtport, version)
	from . import is_open_port
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

	#os.environ["AUTOUPDATE_VERSION"] = str(128)
	environ["AUTOUPDATE_VERSION"] = str(version)

	if restart:
		#TODO - find a way to communicate with the process started with popen
		print "kill react watch "
		import zerorpc
		try:
			c = zerorpc.Client()
			c.connect("tcp://127.0.0.1:5252")
			c.stop_and_exit()
		except:
			print "stop and exit exception"
	#subprocess.Popen(["node", path + "/main.js"], cwd=path, env=os.environ)
	#react = subprocess.Popen(["node", path + "/main.js"], cwd=path, shell=False, close_fds=True, env=environ)
	#react = subprocess.Popen(["node", path + "/rundevserver.js"], cwd=path, shell=False, close_fds=True, env=environ)
	subprocess.Popen(["python", path + "/startfluorine.py", path + "/app"], cwd=path, shell=False, close_fds=True, env=environ)


def start_reactivity():
	from . import meteor_autoupdate_version
	path = file.get_path_server_observe()
	#file.observe_dir(path)
	print start_hash(path)
	path_reactivity = file.get_path_reactivity()
	js_path = file.get_path_assets_js()
	meteor_files = ("meteor.devel.js", "meteor.js")
	boot_file = os.path.join(path_reactivity, "server", "boot.js")
	print "in start_reactivity js_path {} boot_file {} curr path {}".format(js_path, boot_file, os.getcwd())
	for f in meteor_files:
		path_file = os.path.join(js_path, f)
		if os.path.exists(path_file) and os.path.exists(boot_file):
			run_reactivity(path_reactivity, meteor_autoupdate_version())
			break

print "frappe.__file__ 2 {}".format(os.getcwd())

import sys

if any("--serve"==s for s in sys.argv):
	print "starting reactivity... {}".format(sys.argv)
	start_reactivity()