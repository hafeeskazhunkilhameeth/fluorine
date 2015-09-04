# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'

import frappe
import os, json
import subprocess
import shutil
from shutil import ignore_patterns



def get_common_config_file_json():

	path_reactivity = get_path_reactivity()
	common_config_file_json = os.path.join(path_reactivity, "common_site_config.json")
	if os.path.exists(common_config_file_json):
		return frappe.get_file_json(common_config_file_json)

	return


def save_custom_template(template_path):
	from fluorine.utils import get_encoding

	fluorine_path = frappe.get_app_path("fluorine")
	if not template_path.startswith("templates/pages/"):
		template_path = os.path.join("templates/pages/", template_path)
	tplt = os.path.join(fluorine_path, "templates", "pages", "fluorine_home.html")
	content = ("{%% extends '%s' %%}\n" % template_path).encode(get_encoding())
	save_file(tplt, content)


def make_meteor_file(mtport=3070, mthost="http://127.0.0.1", architecture="os.linux.x86_64", whatfor=None):
	from fluorine.utils import meteor_web_app
	import shlex

	whatfor = whatfor or meteor_web_app

	path = get_path_reactivity()
	args = shlex.split("meteor build --directory %s --server %s --architecture %s %s" % (os.path.join(path, whatfor.replace("meteor", "final")), mthost + ':' + str(mtport), architecture,\
																						"--debug" if whatfor == "meteor_app" else ""))
	print "start make meteor... {}".format(whatfor)
	subprocess.call(args, cwd=os.path.join(path, whatfor), close_fds=True)

"""
def make_meteor_config_file(mthost, mtport, version):
	import fluorine
	from fluorine.utils.meteor.utils import get_meteor_config

	config = get_meteor_config(mthost, mtport,  version, version)
	module_path = os.path.dirname(fluorine.__file__)
	meteor_config_file = os.path.join(module_path, "public", "js", "meteor_config.js")
	save_file(meteor_config_file, config)
"""

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

	with open(file_path, "w") as f:
		f.write(content)


def writelines(file_path, content):
	with open(file_path, "w") as f:
		f.writelines(content)

def readlines(file_path, sizehint=0):
	with open(file_path, "r") as f:
		content = f.readlines(sizehint)
	return content

def read(file_path):
	with open(file_path, "r") as f:
		content = f.read()
	return content

def read_file(file, mode="r"):
	d = {}
	file_path = get_path_fluorine(file)
	try:
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
	path_reactivity = get_path_reactivity()
	path = os.path.join(path_reactivity, "app", "server")
	return path

def get_path_reactivity():
	frappe_module = os.path.dirname(frappe.__file__)
	path_apps = os.path.realpath(os.path.join(frappe_module, "..", ".."))
	path_reactivity = os.path.join(path_apps, "reactivity")
	return path_reactivity

def get_path_assets_js():

	base = get_fluorine_conf("sites_path")
	if not base:
		base = frappe.utils.get_site_base_path()
		js_path = os.path.realpath(os.path.join(base, "..", "assets", "js"))
	else:
		js_path = os.path.realpath(os.path.join(base, "assets", "js"))

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
		f.flush()

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

def check_remove_files_folders(file,  files_folder_remove):
	if files_folder_remove:
		for pattern in files_folder_remove:
			if pattern.match(file):
				return True
	return False

# copy the translations files from apps from the first installed to the last installed so we can replace with new ones
# project-tap.i18n can be replaced with new data from last installed apps
def copy_meteor_languages(start_folders, dest_folder, appname, whatfor=None, custom_pattern=None):
	from fluorine.utils import get_attr_from_json
	import fnmatch

	pattern, ignored_names_any, ignored_names_top  = custom_pattern
	#list_meteor_files_folders_remove = frappe.local.meteor_ignores.get("remove").get("files_folders")
	list_meteor_files_folders_remove = get_attr_from_json([whatfor, "remove", "files_folders"], frappe.local.meteor_ignores)
	all_files_folder_remove = list_meteor_files_folders_remove.get("all")
	appname_files_folder_remove = list_meteor_files_folders_remove.get(appname)

	for st_folder in start_folders:
		for root, dirs, files in os.walk(st_folder):
			ign_dirs = pattern(st_folder, dirs)
			try:
				ign_dirs.update(ignored_names_any)
				[dirs.remove(toexclude) for toexclude in ign_dirs if toexclude in dirs]
			except:
				print "remove exclude 3 {} no exclude in dirs ".format(ignored_names_top)
				pass

			files = [toinclude for toinclude in files if fnmatch.fnmatch(toinclude, "*i18n.json") or fnmatch.fnmatch(toinclude, "*project-tap.i18n")]

			for f in files:
				if check_remove_files_folders(f,  all_files_folder_remove) or check_remove_files_folders(f, appname_files_folder_remove):
					continue
				try:
					frappe.create_folder(dest_folder)
					os.symlink(os.path.join(root, f), os.path.join(dest_folder, f))

				except:
					pass

def copy_project_translation(apps, whatfor, custom_pattern=None):

	path_reactivity = get_path_reactivity()
	i18n_files_route = "tap-i18n"#"translations"
	project_file = "project-tap.i18n"
	destpath = os.path.join(path_reactivity, whatfor, project_file)

	#from first installed to the last installed
	for app in apps:
		pathname = frappe.get_app_path(app)
		path = os.path.join(pathname, "templates", "react")
		src_project_path_root = os.path.join(path, project_file)
		src_project_path_app = os.path.join(path, whatfor, project_file)

		if os.path.exists(src_project_path_app):
			os.symlink(src_project_path_app, destpath)
		elif os.path.exists(src_project_path_root):
			os.symlink(src_project_path_root, destpath)

		copy_meteor_languages([os.path.join(path, i18n_files_route), os.path.join(path, whatfor, i18n_files_route)], os.path.join(path_reactivity, whatfor, i18n_files_route), app, custom_pattern=custom_pattern)


"""
Get the mobile-config.js from current-app. If not exists then copy from the most recent app to the last.
"""
def copy_mobile_config_file(apps, whatfor):

	mobile_file = "mobile-config.js"
	path_reactivity = get_path_reactivity()
	destpath = os.path.join(path_reactivity, whatfor, mobile_file)

	#from more recent to last.
	for app in apps:
		app_path = frappe.get_app_path(app)
		srcpath = os.path.join(app_path, "templates", "react", whatfor, mobile_file)
		if os.path.exists(srcpath):
			os.symlink(srcpath, destpath)
			return


#from profilehooks import profile, timecall, coverage
import re
c = lambda t:re.compile(t, re.S|re.M)
common_pattern = c(r"templates/(.*)/?common/(.*)")

#@profile
def make_all_files_with_symlink(dst, whatfor, custom_pattern=None):
	from fluorine.utils import meteor_desk_app, meteor_web_app

	_whatfor = [meteor_desk_app, meteor_web_app]
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
	custom_pattern.update(['*.pyc', '.DS_Store', '*.py', "*.tmp", "temp", "*.xhtml", ".gitignore"])
	pattern = ignore_patterns(*custom_pattern)
	dst_public_assets_path = os.path.join(get_path_reactivity(), whatfor[0], "public", "assets")
	dst_private_path = os.path.join(get_path_reactivity(), whatfor[0], "private")
	dst_tests_path = os.path.join(get_path_reactivity(), whatfor[0], "tests")

	for app, paths in frappe.local.files_to_add.iteritems():
		pathname = frappe.get_app_path(app)
		meteorpath = os.path.join(pathname, "templates", "react", whatfor[0])
		app_path = frappe.get_app_path(app)

		if os.path.exists(meteorpath) and paths:
			folders_path.append(app)
			app_folders = "/".join(folders_path)
			destpath = os.path.join(dst, app_folders)
			make_public(pathname, dst_public_assets_path, app, whatfor, custom_pattern=custom_pattern)
			make_private(meteorpath, dst_private_path, app, whatfor, custom_pattern=custom_pattern)
			make_tests(meteorpath, dst_tests_path, app, whatfor, custom_pattern=custom_pattern)

			for obj in paths:
				tpath = obj.get("tname")
				if tpath:
					relpath = os.path.relpath(tpath[:-6], os.path.join("templates", "react", whatfor[0]))
					startpath = os.path.normpath(os.path.join(meteorpath, relpath, ".."))
				else:
					startpath = os.path.join(app_path, os.path.join("templates", "react", whatfor[0]))

				pat = obj.get("pattern")
				madd = c(pat)

				for root, dirs, files in os.walk(startpath):

					ign_names = pattern(root, files)

					for f in files:
						if f in ign_names:
							continue

						relative_file = os.path.relpath(root, meteorpath)

						source = os.path.normpath(os.path.join("templates", "react", whatfor[0], relative_file, f))

						if check_remove(source):
							continue

						found = madd.match(source) or common_pattern.match(source)
						if found:
							try:
								frappe.create_folder(os.path.realpath(os.path.join(destpath, relative_file)))
								os.symlink(os.path.join(root, f), os.path.realpath(os.path.join(destpath, os.path.join(relative_file,f))))
							except:
								pass


def make_tests(app_path, dst_tests_path, app, whatfor, custom_pattern=None):

	folder_path = os.path.join(app_path, "tests")
	_make_public_private(folder_path, dst_tests_path, app, whatfor, "tests", custom_pattern=custom_pattern)


def make_public(app_path, dst_public_assets_path, app, whatfor, custom_pattern=None):

	folder_path = os.path.join(app_path, "public")
	_make_public_private(folder_path, dst_public_assets_path, app, whatfor, "public", custom_pattern=custom_pattern)


def make_private(meteorpath, dst_private_path, app, whatfor, custom_pattern=None):
	"""
	dst_private_app_path = os.path.join(dst_private_path, app)
	private_path = os.path.join(meteorpath, "private")
	if os.path.exists(private_path):
		os.symlink(private_path, dst_private_app_path)
	"""
	folder_path = os.path.join(meteorpath, "private")
	_make_public_private(folder_path, dst_private_path, app, whatfor, "private", custom_pattern=custom_pattern)


def _make_public_private(folder_path, dst_folder_path, app, whatfor, folder, custom_pattern=None):
	from fluorine.utils import meteor_desk_app, meteor_web_app

	_whatfor = [meteor_desk_app, meteor_web_app]
	exclude = []
	try:
		for w in whatfor:
			_whatfor.remove(w)
		exclude.extend(_whatfor)
	except:
		pass

	dst_folder_app_path = os.path.join(dst_folder_path, app)

	custom_pattern = custom_pattern or []
	custom_pattern = set(custom_pattern)
	if folder == "public":
		custom_pattern.update(["build.json"])
	custom_pattern.update(exclude)
	pattern = ignore_patterns(*custom_pattern)

	if os.path.exists(folder_path):
		files = os.listdir(folder_path)
		custom_ign_names = pattern(folder_path, files)

		for f in files:
			if f in custom_ign_names:
				continue
			if folder == "public" and app == "fluorine" and f in whatfor:
				continue

			frappe.create_folder(os.path.dirname(os.path.join(dst_folder_app_path, f)))
			os.symlink(os.path.join(folder_path, f), os.path.join(dst_folder_app_path, f))


def check_remove(source):
	for rapp, rpaths in frappe.local.files_to_remove.iteritems():
		for obj in rpaths:
			mrm = obj.get("pattern")
			pattern = c(mrm)
			found = pattern.match(source)
			if found:
				return True
	return False


def process_pubpriv_folder(meteorpath, dst, app, app_folders, pattern, meteor_ignore=None):
	from fluorine.utils import meteor_desk_app, meteor_web_app

	ign_top = (meteor_desk_app, meteor_web_app, "temp")

	for root, dirs, files in os.walk(meteorpath):
		meteor_relpath = os.path.relpath(root, frappe.get_app_path(app))
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
	from fluorine.utils import meteor_desk_app, meteor_web_app

	ign_top = (meteor_desk_app, meteor_web_app, "public", "private", "temp")
	destpath = os.path.join(dst, app_folders)
	for root, dirs, files in os.walk(meteorpath):
		meteor_relpath = os.path.relpath(root, frappe.get_app_path(app))
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

def set_config(fobj):
	fobj = fobj or {}
	path_reactivity = get_path_reactivity()
	common_site_config = os.path.join(path_reactivity, "common_site_config.json")
	if os.path.exists(common_site_config):
		config = frappe.get_file_json(common_site_config)
		config.update(fobj)
	else:
		config = fobj

	save_js_file(common_site_config, config)

	return

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
						list_from_func = cfunc(list_ignores)
						if list_from_func:
							all_list.append(list_from_func)
			except:
				pass

	return all_list