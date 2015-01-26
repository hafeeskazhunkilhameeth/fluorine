from __future__ import unicode_literals
__author__ = 'luissaguas'

import frappe
from frappe.utils import get_site_base_path
import os, json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
#import fluorine
import fluorine.utils
import pprint
#import fluorine.utils
#from . import utils
#import utils
import signal
import sys

#pprint.pprint(sys.path)
print "dir file {}".format(dir())

observer = None
react = None


class FileSystemHandler(FileSystemEventHandler):
	def __init__(self):
		pass

	def process(self, event):
		hash = fluorine.utils.make_hash(event.src_path)
		os.environ["AUTOUPDATE_VERSION"] = str(130)
		#import zerorpc
		#c = zerorpc.Client()
		#c.connect("tcp://127.0.0.1:4242")
		#print c.autoupdate(130)
		print event.src_path, event.event_type, hash  # print now only for debug

	def on_modified(self, event):
		self.process(event)
	def on_created(self, event):
		#self.process(event)
		p = fluorine.utils.addjs_file(event.src_path)
		save_js_file(event.src_path, p)

def observe_dir(dir_path):
	global observer
	if not os.path.exists(dir_path):
		print "problems, observer not started!! path {}".format(dir_path)
		return
	#base = get_site_base_path()
	#path = os.path.realpath(os.path.join(base, "..", "..", "apps", "reactivity","server","app", "server"))
	observer = Observer()
	observer.schedule(FileSystemHandler(), dir_path, recursive=True)
	observer.start()
	print "start observer!"

#not used for now
class cd:
	"""Context manager for changing the current working directory"""
	def __init__(self, newPath):
		self.newPath = newPath

	def __enter__(self):
		self.savedPath = os.getcwd()
		os.chdir(self.newPath)

	def __exit__(self, etype, value, traceback):
		os.chdir(self.savedPath)


def make_meteor_file(packages=[], jquery=0, client_only=0, devmode=1):
	#module_path = os.path.dirname(fluorine.__file__)
	#path = os.path.realpath(os.path.join(module_path, "..", "reactivity"))
	#base = get_site_base_path()
	#path = os.path.realpath(os.path.join(base, "..", "..", "apps", "reactivity"))
	path = get_path_reactivity()
	#js_path = os.path.realpath(os.path.join(base,"..", "assets", "js"))
	if not devmode:
		js_path = get_path_assets_js()
	else:
		js_path = frappe.get_app_path("fluorine") + "/public/js"
	#packages.append("iron:router")
	print "meteor_file_path js_path {} path  {}".format(js_path, path)
	#with cd(path):
		#subprocess.call(['./build-meteor-client.sh', js_path, str(frappe.conf.developer_mode), " ".join(packages)])
	proc = subprocess.Popen([path + '/build-meteor-client.sh', js_path, str(devmode), " ".join(packages), str(jquery), str(client_only)], cwd=path, close_fds=True)
	proc.wait()
	run_reactivity(path)
	#observe_dir(get_path_server_observe())

def run_reactivity(path, version=128):
	if fluorine.utils.is_open_port():
		print "Port is open!"
		return

	import copy
	print "Port is not open!"
	environ = copy.copy(os.environ)
	if not os.environ.get("FLUOR_ROOT_URL", None):
		#os.environ["ROOT_URL"] = "http://localhost"
		environ["ROOT_URL"] = "http://localhost"
	if not os.environ.get("FLUOR_PORT", None):
		#os.environ["PORT"] = str(3000)
		environ["PORT"] = str(3000)
	if not os.environ.get("FLUOR_MONGO_URL", None):
		#os.environ["MONGO_URL"] = "mongodb://localhost:27017/ekaiser"
		environ["MONGO_URL"] = "mongodb://localhost:27017/ekaiser"

	#os.environ["AUTOUPDATE_VERSION"] = str(128)
	environ["AUTOUPDATE_VERSION"] = str(version)
	#subprocess.Popen(["node", path + "/main.js"], cwd=path, env=os.environ)
	global react
	#react = subprocess.Popen(["node", path + "/main.js"], cwd=path, shell=False, close_fds=True, env=environ)
	#react = subprocess.Popen(["node", path + "/rundevserver.js"], cwd=path, shell=False, close_fds=True, env=environ)
	react = subprocess.Popen(["python", path + "/startfluorine.py", path + "/app"], cwd=path, shell=False, close_fds=True, env=environ)

def remove_file(file):
	module_path = os.path.dirname(fluorine.__file__)
	old_file = os.path.join(module_path, file)
	if os.path.exists(old_file):
		os.remove(old_file)


def read_file(file):
	d = {}
	#module_path = os.path.dirname(fluorine.__file__)
	try:
		#file_path = os.path.join(module_path, file)
		file_path = get_path_fluorine(file)
		with open(file_path, "r") as f:
			for line in f:
				(key, val) = line.split("=")
				try:
					d[key] = json.loads(val)
				except:
					d[key] = val
	except:
		print "Error file {} doesn't exist".format(file_path)

	return d

def get_path_fluorine(file):
	module_path = os.path.dirname(fluorine.__file__)
	file_path = os.path.join(module_path, file)
	return file_path

def get_path_server_observe():
	#base = get_site_base_path()
	#path = os.path.realpath(os.path.join(base, "..", "..", "apps", "reactivity","app", "server"))
	path_reactivity = get_path_reactivity()
	path = os.path.join(path_reactivity, "app", "server")
	return path

def get_path_reactivity():
	#base = get_site_base_path()
	#path = os.path.realpath(os.path.join(base, "..", "..", "apps", "reactivity"))
	path_module = os.path.dirname(fluorine.__file__)
	print "PATH MODULE {}".format(path_module)
	path_reactivity = os.path.realpath(os.path.join(path_module, "..", ".."))
	path = os.path.join(path_reactivity, "reactivity")
	return path

def get_path_assets_js():
	#base = get_site_base_path()
	base = get_fluorine_conf("sites_path")
	if not base:
		base = get_site_base_path()
		#print "sites path in get_path_assets_js {}".format(os.path.realpath(base))
		js_path = os.path.realpath(os.path.join(base, "..", "assets", "js"))
		#if not base:
		#	base = os.getcwd()
		#	js_path = os.path.realpath(os.path.join(base, "..", "assets", "js"))
	else:
		js_path = os.path.realpath(os.path.join(base, "assets", "js"))

	#js_path = os.path.realpath(os.path.join(base, "..", "assets", "js"))
	print "js_path {}".format(js_path)
	return js_path

def get_fluorine_conf(name):
	path_reactivity = get_path_reactivity()
	common_site_config = os.path.join(path_reactivity, "common_site_config.json")
	if os.path.exists(common_site_config):
		f = frappe.get_file_json(common_site_config)
		return f.get(name, None)
	return None

def get_fluorine_server_conf():
	path_reactivity = get_path_reactivity()
	program_conf = os.path.join(path_reactivity, "program.json")
	if os.path.exists(program_conf):
		return frappe.get_file_json(program_conf)
	return None

def save_js_file(file_path, p):
	with open(file_path, "w") as f:
		f.write(json.dumps(p))

