# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'

import frappe
import os, json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import shutil
from shutil import ignore_patterns

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


def write(file_path, content):
	import codecs
	#print "contens to write to file file_path 5 {} content {}".format(file_path, content.decode("utf-8"))
	with open(file_path, "w") as f:
	#with codecs.open(file_path, "w", encoding='utf-8') as f:
		f.write(content)
		#print "writing files in order file_temp_path 2 {}".format(file_path)


def read(file_path):
	with open(file_path, "r") as f:
		content = f.read()
	return content

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

def save_file(file_path, p, mode="w"):
	with open(file_path, mode) as f:
		f.write(p)

def get_meteor_release(cpath):
	#rpath = get_path_reactivity()
	#cpath = os.path.join(rpath, "server", "config.json")

	if os.path.exists(cpath):
		config = frappe.get_file_json(cpath)
		return config.get("meteorRelease", "")

	return ""

#def get_meteor_config(mthost, mtport, version, version_fresh, mrelease):
def get_meteor_config(mthost, mthostport, meteor_url_path_prefix, version, version_fresh, mrelease):
	#meteor_host = mthost + ":" + str(mtport)

	#print "in get_meteor_config 2 {}".format(mtport)
	meteor_config = """__meteor_runtime_config__ = {
		"meteorRelease": "%(meteorRelease)s",
		"ROOT_URL": "%(meteor_root_url)s",
		"ROOT_URL_PATH_PREFIX": "%(meteor_url_path_prefix)s",
		"autoupdateVersion": "%(meteor_autoupdate_version)s",
		"autoupdateVersionRefreshable": "%(meteor_autoupdate_version_freshable)s",
		"DDP_DEFAULT_CONNECTION_URL": "%(meteor_ddp_default_connection_url)s"
};
		""" % {"meteorRelease": mrelease, "meteor_root_url": mthost, "meteor_url_path_prefix": meteor_url_path_prefix,
				"meteor_autoupdate_version": version, "meteor_autoupdate_version_freshable": version_fresh,
				"meteor_ddp_default_connection_url": mthostport}

	return meteor_config


def empty_directory(folder, ignore=None):
	import os, shutil

	if isinstance(ignore, basestring):
		ignore = [ignore]

	for f in os.listdir(folder):
		file_path = os.path.join(folder, f)
		try:
			if os.path.isfile(file_path):
				os.unlink(file_path)
			elif os.path.isdir(file_path) and f not in ignore:
				shutil.rmtree(file_path)
		except Exception, e:
			print e


def copy_all_files_with_symlink(src, dst, whatfor, extension="js"):
	from react_file_loader import copy_client_files
	#fluorine_dst_temp_path = os.path.join(frappe.get_app_path("fluorine"), "templates", "react", "temp")
	exclude= ["temp"]
	copy_client_files(src, whatfor, extension=extension, with_wrapper=False, exclude_top=exclude, exclude_any=exclude)
	#react_path = get_path_reactivity()
	#dst = os.path.join(react_path, "app")
	for l in os.listdir(src):
		os.symlink(os.path.join(src, l), os.path.join(dst,l))

	#remove_directory(src)

def check_in_files_remove_list(app, template, list_meteor_files_remove):

	for name in list_meteor_files_remove.get(app, []):
		if name == template:
			return True

	return False


def check_dirs_in_files_remove_list(app, template, dirs, list_meteor_files_remove):
	dirToRemove = []
	for d in dirs:
		template_name = os.path.join(template, d)
		for name in list_meteor_files_remove.get(app, []):
			if name == template_name:
				dirToRemove.append(d)

	return dirToRemove


def match_path(startpath, excludes, includes):
	import fnmatch
	import re

	#includes = ['*.doc', '*.odt'] # for files only
	#excludes = ['/home/paulo-freitas/Documents'] # for dirs and files

	# transform glob patterns to regular expressions
	includes = r'|'.join([fnmatch.translate(x) for x in includes])
	excludes = r'|'.join([fnmatch.translate(x) for x in excludes]) or r'$.'

	for root, dirs, files in os.walk(startpath):

		# exclude dirs
		dirs[:] = [os.path.join(root, d) for d in dirs]
		dirs[:] = [d for d in dirs if not re.match(excludes, d)]

		# exclude/include files
		files = [os.path.join(root, f) for f in files]
		files = [f for f in files if not re.match(excludes, f)]
		files = [f for f in files if re.match(includes, f)]

		for fname in files:
			print fname


from profilehooks import profile, timecall, coverage

"""
@profile
def make_all_files_with_symlink_old(dst, whatfor, meteor_ignore=None, custom_pattern=None):
	_whatfor = ["meteor_app", "meteor_web", "meteor_frappe"]
	folders_path = []
	exclude = ["private", "public"]
	custom_pattern = custom_pattern or []

	if isinstance(whatfor, basestring):
		whatfor = [whatfor]

	try:
		for w in whatfor:
			_whatfor.remove(w)
		exclude.extend(_whatfor)
	except:
		pass

	custom_pattern = set(custom_pattern)
	custom_pattern.update(['*.pyc', '.DS_Store', '*.py', "*.tmp", "temp"])
	pattern = ignore_patterns(*custom_pattern)

	#first installed app first
	apps = frappe.get_installed_apps()#[::-1]
	for app in apps:
		top_folder = True
		pathname = frappe.get_app_path(app)
		startpath = os.path.join(pathname, "templates", "react", whatfor[0])
		meteorpath = os.path.join(pathname, "templates", "react")
		if os.path.exists(meteorpath):
			folders_path.append(app)
			app_folders = "/".join(folders_path)
			destpath = os.path.join(dst, app_folders)

			process_top_folder(meteorpath, dst, app, app_folders, pattern, meteor_ignore=meteor_ignore)
			process_pubpriv_folder(meteorpath, dst, app, app_folders, pattern, meteor_ignore=meteor_ignore)
			process_pubpriv_folder(startpath, dst, app, app_folders, pattern, meteor_ignore=meteor_ignore)

			for root, dirs, files in os.walk(startpath):

				#start with templates/react
				#meteor_relpath = os.path.relpath(root, os.path.join(meteorpath, "..", ".."))
				meteor_relpath = os.path.relpath(root, frappe.get_app_path(app))
				meteor_ignore_folders(app, meteor_relpath, root, dirs, meteor_ignore=meteor_ignore)

				ign_names = pattern(meteorpath, files)
				ign_dirs = pattern(meteorpath, dirs)
				if top_folder:
					ign_dirs.update(exclude)
					[dirs.remove(toexclude) for toexclude in ign_dirs if toexclude in dirs]
					top_folder = False
				else:
					[dirs.remove(toexclude) for toexclude in ign_dirs if toexclude in dirs]
				relpath = os.path.relpath(root, startpath)
				for f in files:
					if f in ign_names or meteor_ignore_files(app, meteor_relpath, root, f, meteor_ignore=meteor_ignore):
						continue

					frappe.create_folder(os.path.realpath(os.path.join(destpath, relpath)))
					os.symlink(os.path.join(root, f), os.path.realpath(os.path.join(destpath, relpath, f)))
"""
"""
@profile
def make_all_files_with_symlink(dst, whatfor, context, meteor_ignore=None, custom_pattern=None):
	import fnmatch, re
	c = lambda t:re.compile(t, re.S|re.M)

	_whatfor = ["meteor_app", "meteor_web", "meteor_frappe"]
	folders_path = []
	exclude = ["private", "public"]
	custom_pattern = custom_pattern or []

	if isinstance(whatfor, basestring):
		whatfor = [whatfor]

	try:
		for w in whatfor:
			_whatfor.remove(w)
		exclude.extend(_whatfor)
	except:
		pass

	custom_pattern = set(custom_pattern)
	custom_pattern.update(['*.pyc', '.DS_Store', '*.py', "*.tmp", "temp", "*.xhtml"])
	pattern = ignore_patterns(*custom_pattern)

	#first installed app first
	#apps = frappe.get_installed_apps()#[::-1]
	#for app in apps:
	for app, paths in context.files_to_add.iteritems():
		#top_folder = True
		pathname = frappe.get_app_path(app)
		#startpath = os.path.join(pathname, "templates", "react", whatfor[0])
		meteorpath = os.path.join(pathname, "templates", "react", whatfor[0])
		if os.path.exists(meteorpath) and paths:
			folders_path.append(app)
			app_folders = "/".join(folders_path)
			destpath = os.path.join(dst, app_folders)
			#process_top_folder(meteorpath, dst, app, app_folders, pattern, meteor_ignore=meteor_ignore)
			#process_pubpriv_folder(meteorpath, dst, app, app_folders, pattern, meteor_ignore=meteor_ignore)
			#process_pubpriv_folder(startpath, dst, app, app_folders, pattern, meteor_ignore=meteor_ignore)
			for obj in paths:
				tpath = obj.get("tname") or obj.get("apppath")
				relpath = os.path.relpath(tpath[:-6], os.path.join("templates", "react", whatfor[0]))
				madd = obj.get("path")
				#for path in context.files_to_add:
				#re_file = fnmatch.translate(filespath)
				#madd = c(re_file)
				startpath = os.path.normpath(os.path.join(meteorpath, relpath, ".."))
				print "path to add appname 9 {} tpath {} relpath {} startpath {}".format(app, tpath, relpath, startpath)
				for root, dirs, files in os.walk(startpath):
					#relative_path = os.path.relpath(root, startpath) + "/"
					#re.match(relative_path, re_file, re.S)
					#found = m.match(root)
					#print "in file make all files symlink root 16 {} dirs {} files {} re_file {} files_path {} found {}".format(root, dirs, files, re_file, filespath, found)
					#if found:
					#start with templates/react
					#meteor_relpath = os.path.relpath(root, frappe.get_app_path(app))
					#meteor_ignore_folders(app, meteor_relpath, root, dirs, meteor_ignore=meteor_ignore)
					ign_names = pattern(startpath, files)
				#if top_folder:
				#	ign_dirs.update(exclude)
				#	[dirs.remove(toexclude) for toexclude in ign_dirs if toexclude in dirs]
				#	top_folder = False
				#else:
					#[dirs.remove(toexclude) for toexclude in ign_dirs if toexclude in dirs]
				#relpath = os.path.relpath(root, startpath)
					for f in files:
						if f in ign_names: #or meteor_ignore_files(app, meteor_relpath, root, f, meteor_ignore=meteor_ignore):
							continue
						if check_remove(context, root, f):
							continue
						#if f in ign_names or meteor_ignore_files(app, meteor_relpath, root, f, meteor_ignore=meteor_ignore):
						found = madd.match(os.path.join(root,f))
						relative_file = os.path.relpath(root, startpath)
						common = root.rsplit("/",1)[1]
						print "in file make all files symlink root files root 2 {} common {} file {} found {} relative_file {}".format(root, common, f, found, relative_file)
						if common == "common":
							found = True

						if found:
							try:
								frappe.create_folder(os.path.realpath(os.path.join(destpath, relative_file)))
								os.symlink(os.path.join(root, f), os.path.realpath(os.path.join(destpath, os.path.join(relative_file,f))))
							except:
								pass
"""

@profile
def make_all_files_with_symlink(dst, whatfor, meteor_ignore=None, custom_pattern=None):
	import re
	c = lambda t:re.compile(t, re.S|re.M)

	_whatfor = ["meteor_app", "meteor_web", "meteor_frappe"]
	folders_path = []
	exclude = ["private", "public"]
	custom_pattern = custom_pattern or []

	if isinstance(whatfor, basestring):
		whatfor = [whatfor]

	try:
		for w in whatfor:
			_whatfor.remove(w)
		exclude.extend(_whatfor)
	except:
		pass

	custom_pattern = set(custom_pattern)
	custom_pattern.update(['*.pyc', '.DS_Store', '*.py', "*.tmp", "temp", "*.xhtml"])
	pattern = ignore_patterns(*custom_pattern)

	#first installed app first
	#apps = frappe.get_installed_apps()#[::-1]
	#for app in apps:
	for app, paths in frappe.local.files_to_add.iteritems():#context.files_to_add.iteritems():
		#top_folder = True
		print "apps in frappe.local.files_to_add 2 {}".format(frappe.local.files_to_add)
		pathname = frappe.get_app_path(app)
		#startpath = os.path.join(pathname, "templates", "react", whatfor[0])
		meteorpath = os.path.join(pathname, "templates", "react", whatfor[0])
		if os.path.exists(meteorpath) and paths:
			folders_path.append(app)
			app_folders = "/".join(folders_path)
			destpath = os.path.join(dst, app_folders)
			#process_top_folder(meteorpath, dst, app, app_folders, pattern, meteor_ignore=meteor_ignore)
			#process_pubpriv_folder(meteorpath, dst, app, app_folders, pattern, meteor_ignore=meteor_ignore)
			#process_pubpriv_folder(startpath, dst, app, app_folders, pattern, meteor_ignore=meteor_ignore)
			for obj in paths:
				tpath = obj.get("tname") or obj.get("apppath")
				relpath = os.path.relpath(tpath[:-6], os.path.join("templates", "react", whatfor[0]))
				pat = obj.get("pattern")
				#for path in context.files_to_add:
				#re_file = fnmatch.translate(filespath)
				madd = c(pat)
				startpath = os.path.normpath(os.path.join(meteorpath, relpath, ".."))
				#print "path to add appname 10 {} tpath {} relpath {} startpath {}".format(app, tpath, relpath, startpath)
				for root, dirs, files in os.walk(startpath):
					#relative_path = os.path.relpath(root, startpath) + "/"
					#re.match(relative_path, re_file, re.S)
					#found = m.match(root)
					#print "in file make all files symlink root 16 {} dirs {} files {} re_file {} files_path {} found {}".format(root, dirs, files, re_file, filespath, found)
					#if found:
					#start with templates/react
					#meteor_relpath = os.path.relpath(root, frappe.get_app_path(app))
					#meteor_ignore_folders(app, meteor_relpath, root, dirs, meteor_ignore=meteor_ignore)
					ign_names = pattern(startpath, files)
				#if top_folder:
				#	ign_dirs.update(exclude)
				#	[dirs.remove(toexclude) for toexclude in ign_dirs if toexclude in dirs]
				#	top_folder = False
				#else:
					#[dirs.remove(toexclude) for toexclude in ign_dirs if toexclude in dirs]
				#relpath = os.path.relpath(root, startpath)
					for f in files:
						if f in ign_names: #or meteor_ignore_files(app, meteor_relpath, root, f, meteor_ignore=meteor_ignore):
							continue

						relative_file = os.path.relpath(root, meteorpath)
						source = os.path.normpath(os.path.join("templates", "react", whatfor[0], relative_file, f))

						if check_remove(source):
							continue
						#if f in ign_names or meteor_ignore_files(app, meteor_relpath, root, f, meteor_ignore=meteor_ignore):
						#found = madd.match(os.path.join(root,f))
						curr_dir = root.rsplit("/",1)[1]
						found = madd.match(source)

						#print "in file make all files symlink root files root 5 {} pattern {} relative_file {} found {}".format(root, source, relative_file, found)
						if curr_dir == "common":
							found = True

						if found:
							try:
								frappe.create_folder(os.path.realpath(os.path.join(destpath, relative_file)))
								os.symlink(os.path.join(root, f), os.path.realpath(os.path.join(destpath, os.path.join(relative_file,f))))
							except:
								pass


def check_remove(source):
	for rapp, rpaths in frappe.local.files_to_remove.iteritems():
		for obj in rpaths:
			mrm = obj.get("pattern")
			found = mrm.match(source)
			if found:
				return True
	return False

def process_pubpriv_folder(meteorpath, dst, app, app_folders, pattern, meteor_ignore=None):
	ign_top = ("meteor_app", "meteor_web", "meteor_frappe", "temp")
	for root, dirs, files in os.walk(meteorpath):
		#start with templates/react
		#meteor_relpath = os.path.relpath(root, os.path.join(meteorpath, "..", "..", ".."))
		meteor_relpath = os.path.relpath(root, frappe.get_app_path(app))
		print "meteor_relpath in make all app 8 {} links {}".format(app, meteor_relpath)
		meteor_ignore_folders(app, meteor_relpath, root, dirs, meteor_ignore=meteor_ignore)
		ign_names = pattern(meteorpath, files)
		meteor_relpath = os.path.relpath(root, meteorpath)
		folders = meteor_relpath.split("/",1)
		[dirs.remove(toexclude) for toexclude in ign_top if toexclude in dirs]
		for f in files:
			if f in ign_names or meteor_ignore_files(app, meteor_relpath, root, f, meteor_ignore=meteor_ignore):
				continue

			if meteor_relpath.startswith(("public", "private")):
				if len(folders) > 1:
					frappe.create_folder(os.path.join(dst, folders[0], app_folders, folders[1]))
					os.symlink(os.path.join(root, f), os.path.join(dst, folders[0], app_folders, folders[1], f))
				else:
					frappe.create_folder(os.path.join(dst, folders[0], app_folders))
					os.symlink(os.path.join(root, f), os.path.join(dst, folders[0], app_folders, f))


def process_top_folder(meteorpath, dst, app, app_folders, pattern, meteor_ignore=None):
	ign_top = ("meteor_app", "meteor_web", "meteor_frappe", "public", "private", "temp")
	destpath = os.path.join(dst, app_folders)
	for root, dirs, files in os.walk(meteorpath):
		meteor_relpath = os.path.relpath(root, frappe.get_app_path(app))
		#print "meteor_relpath in make all app 8 {} links {}".format(app, meteor_relpath)
		meteor_ignore_folders(app, meteor_relpath, root, dirs, meteor_ignore=meteor_ignore)

		ign_names = pattern(meteorpath, files)
		meteor_relpath = os.path.relpath(root, meteorpath)
		folders = meteor_relpath.split("/",1)
		[dirs.remove(toexclude) for toexclude in ign_top if toexclude in dirs]
		for f in files:
			if f in ign_names or meteor_ignore_files(app, meteor_relpath, root, f, meteor_ignore=meteor_ignore):
				continue

			c = len(folders)
			frappe.create_folder(os.path.join(destpath, folders[c]))
			os.symlink(os.path.join(root, f), os.path.join(destpath, folders[c], f))


def meteor_ignore_folders(app, meteor_relpath, root, dirs, meteor_ignore=None):
	if meteor_ignore:
		files_folders = meteor_ignore.get("remove").get("files_folders")
		dirsToRemove = check_dirs_in_files_remove_list(app, meteor_relpath, dirs, files_folders)
		for d in dirsToRemove:
			dirs.remove(d)

	templates_to_remove = meteor_ignore.get("templates_to_remove")
	app_remove = templates_to_remove.get(app, None)
	if app_remove:
		for d in dirs:
			dirpath = os.path.join(root, d)
			for k,v in app_remove.iteritems():
				c = v.get("compiled")
				if c.match(dirpath):
					if not has_valid_add_templates(app, v.get("order"), dirpath, meteor_ignore=meteor_ignore):
						try:
							dirs.remove(d)
						except:
							pass


def meteor_ignore_files(app, meteor_relpath, root, file, meteor_ignore=None):

	if meteor_ignore:
		filePath = os.path.join(meteor_relpath, file)
		templates = meteor_ignore.get("remove").get("meteor_files_templates")
		files_folders = meteor_ignore.get("remove").get("files_folders")
		for l in  (templates, files_folders):
			if check_in_files_remove_list(app, filePath, l):
				return True

	templates_to_remove = meteor_ignore.get("templates_to_remove")
	app_remove = templates_to_remove.get(app, None)
	if app_remove:
		filepath = os.path.join(root, file)
		for k,v in app_remove.iteritems():
			c = v.get("compiled")
			if c.match(filepath):
				if not has_valid_add_templates(app, v.get("order"), filepath, meteor_ignore=meteor_ignore):
					return True
				else:
					return False

	return False

def has_valid_add_templates(app, order, path, meteor_ignore=None):
	templates_to_add = meteor_ignore.get("templates_to_add")
	app_add = templates_to_add.get(app, None)
	if app_add:
		for k,v in app_add.iteritems():
			c = v.get("compiled")
			if c.match(path):
				dorder = v.get("order")
				if dorder >= order:
					return False
				else:
					return True
			elif os.path.isdir(path):
				#in this case if the template teste10/ is in folder /.../test10/ or this folder /.../teste10/.../ we don't exclude this folders
				#in this way we can remove every thing in the folder but the added files and folders
				tname = v.get("tname")
				npath = path + "/"
				if tname in npath:
					return True
				return False
	return False

"""
This function is call before process the files of the app
This function call reactignores.py module inside each app templates folder with the list of hook ignores
This way we can from code change the list adding or removing

The list of functions to call are: get_meteor_apps; get_meteor_files_folders; get_meteor_files_templates; get_meteor_templates;
And one list that's get all the ignor list: proces_all_meteor_lists

The list_ignores has the following structure:

{
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
	}

}

and the list in each key has the following structure:

{
	"appname1": [object or string],
	"appname2": [object or string]
}


meteor_templates: list_meteor_tplt_remove is a list of dict with this structure:
{"name":"template or block name", "file":"templates/react/meteor_web or meteor_app/.../a.xhtml"}
Here we can remove any meteor template tag or jinja2 block tag with the given name from the gives file

meteor_files_templates: list_meteor_files_remove is a list with this structure:
"templates/react/meteor_web or meteor_app/.../a.xhtml"
Here we can remove any meteor file with extension xhtml and all its blocks and templates

files_folders: list_meteor_files_folders_remove is a list with this structure:
"templates/react/meteor_web or meteor_app/.../" or "templates/react/meteor_web or meteor_app/.../any_file.any_ext"
Here we can remove any folder or file

list_apps_remove: list_apps_remove is a list.
["appname1", "appname2"]
Here we can remove any app

"""

def process_ignores_from_modules(apps, func, list_ignores=None):

	all_list = []

	for app in apps:
		pathname = frappe.get_app_path(app)
		ignorpath = os.path.join(pathname, "templates")
		controller_path = os.path.join(ignorpath, "reactignores.py")
		if controller_path:
			controller = app + "." + os.path.relpath(controller_path, pathname).replace(os.path.sep, ".")[:-3]
			try:
				module = frappe.get_module(controller)
				if module:
					if hasattr(module, func):
						cfunc = getattr(module, func)
						#add, remove = cfunc(currapp, list_ignores)
						"""
						Must return a dict:
						{
							"appname":{
								"remove": [object or string]
							}
						}
						"""
						list_from_func = cfunc(list_ignores)
						#list_files = frappe._dict({})
						#a = frappe._dict({})
						#a[currapp] = frappe._dict({
						#	"remove":remove or [],
						#	"add":add or []
						#})
						#all_list.append(a)
						if list_from_func:
							all_list.append(list_from_func)
						#list_files[func[4:]] = a
							#module.get_meteor_files_templates(list_ignores)
					#if hasattr(module, "get_meteor_apps"):
					#	apps = module.get_meteor_apps(list_ignores)
					#if hasattr(module, "get_meteor_files_folders"):
					#	ifolders = module.get_ignor_folders(list_ignores)
			except:
				pass

	return all_list

"""
def make_all_files_with_symlink3(dst, whatfor, ignore=None, custom_pattern=None):
	_whatfor = ["meteor_app", "meteor_web", "meteor_frappe"]
	folders_path = []
	exclude = [""]
	custom_pattern = custom_pattern or ('*.pyc', '.DS_Store', '*.py')

	if isinstance(whatfor, basestring):
		whatfor = [whatfor]

	try:
		for w in whatfor:
			_whatfor.remove(w)
		exclude = _whatfor
	except:
		pass

	apps = frappe.get_installed_apps()[::-1]
	for app in apps:
		topfolder = True
		pathname = frappe.get_app_path(app)
		startpath = os.path.join(pathname, "templates", "react", whatfor[0])
		meteorpath = os.path.join(pathname, "templates", "react")
		if os.path.exists(meteorpath):
			folders_path.append(app)
			app_folders = "/".join(folders_path)
			destpath = os.path.join(dst, app_folders)
			for root, dirs, files in os.walk(meteorpath):
				pattern = ignore_patterns(*custom_pattern)
				ign_names = pattern(meteorpath, files)
				[dirs.remove(toexclude) for toexclude in exclude if toexclude in dirs]
				relpath = os.path.relpath(root, meteorpath)
				if not relpath.startswith(("meteor_app", "meteor_web", "meteor_frappe", "public", "private")):
					topfolder = True
				relpath = os.path.relpath(root, startpath)
				meteor_relpath = os.path.relpath(root, meteorpath)
				for f in files:
					if f in ign_names:
						continue
					print "relpath meteorpath {} startpath {}".format(os.path.relpath(root, meteorpath), os.path.relpath(root, startpath))
					#if relpath.startswith((os.path.join(whatfor[0], "public"), os.path.join(whatfor[0], "private"))):
					if relpath.startswith(("public", "private")):
						folders = relpath.split("/",1)
						if len(folders) > 1:
							frappe.create_folder(os.path.join(dst, folders[0], app_folders, folders[1]))
							os.symlink(os.path.join(root, f), os.path.join(dst, folders[0], app_folders, folders[1], f))
						else:
							frappe.create_folder(os.path.join(dst, folders[0], app_folders))
							os.symlink(os.path.join(root, f), os.path.join(dst, folders[0], app_folders, f))
					elif meteor_relpath.startswith(("public", "private")):
						folders = meteor_relpath.split("/",1)
						if len(folders) > 1:
							frappe.create_folder(os.path.join(dst, folders[0], app_folders, folders[1]))
							os.symlink(os.path.join(root, f), os.path.join(dst, folders[0], app_folders, folders[1], f))
						else:
							frappe.create_folder(os.path.join(dst, folders[0], app_folders))
							os.symlink(os.path.join(root, f), os.path.join(dst, folders[0], app_folders, f))
					elif topfolder:
						relpath = os.path.relpath(root, meteorpath)
						paths = relpath.split("/", 1)
						if len(paths) > 1:
							frappe.create_folder(os.path.join(destpath, paths[1]))
							os.symlink(os.path.join(root, f), os.path.join(destpath, paths[1], f))
						else:
							frappe.create_folder(os.path.join(destpath, paths[0]))
							os.symlink(os.path.join(root, f), os.path.join(destpath, paths[0], f))
					else:
						frappe.create_folder(os.path.realpath(os.path.join(destpath, relpath)))
						os.symlink(os.path.join(root, f), os.path.realpath(os.path.join(destpath, relpath, f)))



def make_all_files_with_symlink2(dst, whatfor, ignore=None, custom_pattern=None):
	_whatfor = ["meteor_app", "meteor_web", "meteor_frappe"]
	folders_path = []
	exclude = [""]
	custom_pattern = custom_pattern or ('*.pyc', '.DS_Store', '*.py')

	if isinstance(whatfor, basestring):
		whatfor = [whatfor]

	try:
		for w in whatfor:
			_whatfor.remove(w)
		exclude = _whatfor
	except:
		pass

	apps = frappe.get_installed_apps()[::-1]
	for app in apps:
		pathname = frappe.get_app_path(app)
		startpath = os.path.join(pathname, "templates", "react", whatfor[0])
		if os.path.exists(startpath):
			folders_path.append(app)
			app_folders = "/".join(folders_path)
			destpath = os.path.join(dst, app_folders)
			for root, dirs, files in os.walk(startpath):
				pattern = ignore_patterns(*custom_pattern)
				ign_names = pattern(startpath, files)
				[dirs.remove(toexclude) for toexclude in exclude if toexclude in dirs]
				for f in files:
					if f in ign_names:
						continue
					relpath = os.path.relpath(root, startpath)
					if relpath.startswith(("public", "private")):
						folders = relpath.split("/",1)
						if len(folders) > 1:
							frappe.create_folder(os.path.join(dst, folders[0], app_folders, folders[1]))
							os.symlink(os.path.join(root, f), os.path.join(dst, folders[0], app_folders, folders[1], f))
						else:
							frappe.create_folder(os.path.join(dst, folders[0], app_folders))
							os.symlink(os.path.join(root, f), os.path.join(dst, folders[0], app_folders, f))
					else:
						frappe.create_folder(os.path.join(destpath, relpath))
						os.symlink(os.path.join(root, f), os.path.join(destpath, relpath, f))


def make_files_with_symlink(dst, whatfor, ignore=None):
	ignore = ignore or ["public", "private"]
	_whatfor = ["meteor_app", "meteor_web", "meteor_frappe"]
	folders_path = []
	exclude = [""]

	if isinstance(whatfor, basestring):
		whatfor = [whatfor]

	try:
		for w in whatfor:
			_whatfor.remove(w)
		exclude = _whatfor
	except:
		pass

	apps = frappe.get_installed_apps()[::-1]
	for app in apps:
		pathname = frappe.get_app_path(app)
		startpath = os.path.join(pathname, "templates", "react", whatfor[0])
		if os.path.exists(startpath):
			meteorpath = os.path.join(pathname, "templates", "react")
			names = os.listdir(meteorpath)
			pattern = ignore_patterns('*.pyc', '.*', '*.py')
			ign_names = pattern(meteorpath, names)

			folders_path.append(app)
			app_folders = "/".join(folders_path)
			destpath = os.path.join(dst, app_folders)
			frappe.create_folder(destpath)
			#only one whatfor or for app or for web
			for l in names:
				if l in exclude or l in ign_names:
					continue

				if l in ignore:
					if l == "public":
						dst_ign_path = os.path.join(dst, l, app)
						ppath = os.path.join(meteorpath, "public")
						process_pub_priv_folder(meteorpath, dst_ign_path, dst_ign_path, ppath, exclude)
					elif l == "private":
						dst_ign_path = os.path.join(dst, l, app_folders[:-len(app)-1])
						linkpath = os.path.join(dst_ign_path, "private_" + app)
						ppath = os.path.join(meteorpath, "private")
						curr_app = app
						process_pub_priv_folder(meteorpath, dst_ign_path, linkpath, ppath, exclude, curr_app)
				else:
					if l == whatfor[0]:
						process_folder(os.path.join(meteorpath, l), destpath, exclude)
					else:
						os.symlink(os.path.join(meteorpath, l), os.path.join(destpath, l))



def process_folder(src, dst, exclude, ignore=None):
	names = os.listdir(src)
	pattern = ignore_patterns('*.pyc', '.*', '*.py')
	ign_names = pattern(src, names)
	ignore = ignore or ["public", "private"]
	for l in names:
		if l in exclude or l in ignore or l in ign_names:
			continue

		print "process_folder src {} dst {}".format(os.path.join(src, l), os.path.join(dst, l))
		os.symlink(os.path.join(src, l), os.path.join(dst, l))

def process_pub_priv_folder(src, dst, linkpath, privpath, exclude, app=""):

	names = os.listdir(privpath)
	pattern = ignore_patterns('*.pyc', '.*', '*.py')
	ign_names = pattern(src, names)

	for l in names:
		if l in exclude or l in ign_names:
			continue

		frappe.create_folder(os.path.join(dst, app))
		if os.path.isdir(l):
			os.symlink(os.path.join(src, l), linkpath)
		else:
			os.symlink(os.path.join(src, l), os.path.join(dst, app, l))
"""
"""
def process_public_folder(src, dst, linkpath, privpath, exclude):

	names = os.listdir(privpath)
	pattern = ignore_patterns('*.pyc', '.*', '*.py')
	ign_names = pattern(src, names)

	for l in names:
		if l in exclude or l in ign_names:
			continue

		frappe.create_folder(dst)
		if os.path.isdir(l):
			os.symlink(os.path.join(src, l), linkpath)
		else:
			os.symlink(os.path.join(src, l), os.path.join(dst, l))
"""
#TODO
"""
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
"""
"""
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
"""