from __future__ import unicode_literals
__author__ = 'luissaguas'

import frappe
import os, json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import shutil


observer = None


class FileSystemHandler(FileSystemEventHandler):
	def __init__(self):
		pass

	def process(self, event):
		from . import make_hash
		hash = make_hash(event.src_path)
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
		from . import addjs_file
		p = addjs_file(event.src_path)
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


def make_meteor_file(packages=None, jquery=0, client_only=0, devmode=1, whatfor="meteor_web"):
	#module_path = os.path.dirname(fluorine.__file__)
	#path = os.path.realpath(os.path.join(module_path, "..", "reactivity"))
	#base = get_site_base_path()
	#path = os.path.realpath(os.path.join(base, "..", "..", "apps", "reactivity"))
	w = {"meteor_web": "web", "meteor_app": "app", "common":"common"}
	packages = packages or []
	path = get_path_reactivity()
	#js_path = os.path.realpath(os.path.join(base,"..", "assets", "js"))
	#if not devmode:
	#	js_path = get_path_assets_js()
	#else:
	js_path = os.path.join(frappe.get_app_path("fluorine"), "public/js")
	#packages.append("iron:router")
	print "meteor_file_path js_path {} path  {}".format(js_path, path)
	#fluorine_publicjs_path = os.path.join(frappe.get_app_path("fluorine"), "public", "js", "react")
	#file.remove_folder_content(fluorine_publicjs_path)
	#copy_all_files(os.path.join(path, "app"), "meteor_web")
	#with cd(path):
		#subprocess.call(['./build-meteor-client.sh', js_path, str(frappe.conf.developer_mode), " ".join(packages)])
	proc = subprocess.Popen([path + '/build-meteor-client.sh', js_path, str(devmode), " ".join(packages), str(jquery), str(client_only), w[whatfor]], cwd=path, close_fds=True)
	proc.wait()
	#observe_dir(get_path_server_observe())


def make_meteor_config_file(mthost, mtport, version):
	import fluorine
	config = get_meteor_config(mthost, mtport,  version, version)
	module_path = os.path.dirname(fluorine.__file__)
	meteor_config_file = os.path.join(module_path, "public", "js", "meteor_config.js")
	save_file(meteor_config_file, config)

def remove_file(file):
	import fluorine
	module_path = os.path.dirname(fluorine.__file__)
	old_file = os.path.join(module_path, file)
	if os.path.exists(old_file):
		os.remove(old_file)


def remove_folder_content(folder):
	for root, dirs, files in os.walk(folder):
		for f in files:
			os.unlink(os.path.join(root, f))
		for d in dirs:
			shutil.rmtree(os.path.join(root, d))


def read_file(file, mode="r"):
	d = {}
	#module_path = os.path.dirname(fluorine.__file__)
	file_path = get_path_fluorine(file)
	try:
		#file_path = os.path.join(module_path, file)
		with open(file_path, mode) as f:
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
	import fluorine
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
	import fluorine
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
		base = frappe.utils.get_site_base_path()
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

def save_js_file(file_path, p, indent=4):
	save_file(file_path, json.dumps(p, indent=indent))

def save_file(file_path, p):
	with open(file_path, "w") as f:
		f.write(p)

def get_meteor_release():
	rpath = get_path_reactivity()
	cpath = os.path.join(rpath, "server", "config.json")

	if os.path.exists(cpath):
		config = frappe.get_file_json(cpath)
		return config.get("meteorRelease", "")

	return ""

def get_meteor_config(mthost, mtport,  version, version_fresh):

	meteor_host = mthost + ":" + str(mtport)

	print "in get_meteor_config 2 {}".format(mtport)
	meteor_config = """var __meteor_runtime_config__ = {
		"meteorRelease": "%(meteorRelease)s",
		"ROOT_URL": "%(meteor_root_url)s",
		"ROOT_URL_PATH_PREFIX": "%(meteor_url_path_prefix)s",
		"autoupdateVersion": "%(meteor_autoupdate_version)s",
		"autoupdateVersionRefreshable": "%(meteor_autoupdate_version_freshable)s",
		"DDP_DEFAULT_CONNECTION_URL": "%(meteor_ddp_default_connection_url)s"
};
		""" % {"meteorRelease": get_meteor_release(), "meteor_root_url": meteor_host, "meteor_url_path_prefix": "",
				"meteor_autoupdate_version": version, "meteor_autoupdate_version_freshable": version_fresh,
				"meteor_ddp_default_connection_url": meteor_host}

	return meteor_config


def copy_all_files_with_symlink(src, dst, whatfor, extension="js"):
	from react_file_loader import copy_client_files
	#fluorine_dst_temp_path = os.path.join(frappe.get_app_path("fluorine"), "templates", "react", "temp")
	copy_client_files(src, whatfor, extension=extension, with_wrapper=False)
	#react_path = get_path_reactivity()
	#dst = os.path.join(react_path, "app")
	for l in os.listdir(src):
		os.symlink(os.path.join(src, l), os.path.join(dst,l))

	#remove_directory(src)

#TODO
def copy_all_files(dst, whatfor, extension="js"):
	from react_file_loader import copy_client_files, remove_directory
	fluorine_dst_temp_path = os.path.join(frappe.get_app_path("fluorine"), "templates", "react", "temp")
	copy_client_files(fluorine_dst_temp_path, whatfor, extension=extension, with_wrapper=False)
	apps = frappe.get_installed_apps()
	for app in apps:
		pathname = frappe.get_app_path(app)
		src = os.path.join(pathname, "templates", "react")
		if pathname and os.path.exists(src):
			copytree(src, dst, whatfor)

	remove_directory(fluorine_dst_temp_path)

#patch copytree to support meteor_web and meteor_app folders
def copytree(src, dst, whatfor, symlinks=False, ignore=None):
	from shutil import copy2, copystat, Error, WindowsError
	names = os.listdir(src)
	if ignore is not None:
		ignored_names = ignore(src, names)
	else:
		ignored_names = set()

	if not os.path.exists(dst):
		os.makedirs(dst)
	errors = []
	for name in names:
		if name in ignored_names:
			continue

		#patch - remove meteor_app or meteor_web from path
		if whatfor in dst:
			head, tail = dst.split(whatfor)
			if tail and tail.startswith("/"):
				tail = tail[1:]
			dst = os.path.join(head,tail)
			print "dst whatfor {}".format(dst)

		srcname = os.path.join(src, name)
		if whatfor in name:
			name = ""
		dstname = os.path.join(dst, name)

		try:
			if symlinks and os.path.islink(srcname):
				linkto = os.readlink(srcname)
				os.symlink(linkto, dstname)
			elif os.path.isdir(srcname):
				copytree(srcname, dstname, whatfor, symlinks, ignore)
			else:
				copy2(srcname, dstname)
			# XXX What about devices, sockets etc.?
		except (IOError, os.error) as why:
			errors.append((srcname, dstname, str(why)))
		# catch the Error from the recursive copytree so that we can
		# continue with other files
		except Error as err:
			errors.extend(err.args[0])
	try:
		copystat(src, dst)
	except WindowsError:
		# can't copy file access times on Windows
		pass
	except OSError as why:
		errors.extend((src, dst, str(why)))
	if errors:
		raise Error(errors)