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


def make_meteor_file(site, mtport=3070, mthost="http://127.0.0.1", architecture="os.linux.x86_64", whatfor=None):
	from fluorine.utils import meteor_web_app, get_meteor_final_name, get_meteor_folder_for_site
	import shlex

	whatfor = whatfor or meteor_web_app

	final_app_name = get_meteor_final_name(site, whatfor)
	path = get_path_reactivity()

	folder = get_meteor_folder_for_site(whatfor, frappe.local.site)
	cwd = os.path.join(path, folder)
	args = shlex.split("meteor build --directory %s --server %s --architecture %s %s" % (os.path.join(path, final_app_name), mthost + ':' + str(mtport), architecture,
																						"--debug" if whatfor == "meteor_app" else ""))
	print "start make meteor... {}".format(whatfor)
	subprocess.call(args, cwd=cwd, close_fds=True)


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

"""
def get_path_server_observe():
	path_reactivity = get_path_reactivity()
	path = os.path.join(path_reactivity, "app", "server")
	return path
"""

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

def empty_directory(folder, remove=None):
	from fluorine.utils import APPS as apps
	import os, shutil

	if isinstance(remove, basestring):
		ignore = [remove]

	for f in os.listdir(folder):
		file_path = os.path.join(folder, f)
		try:
			if os.path.isdir(file_path) and f in apps or f in remove:
				shutil.rmtree(file_path)
		except Exception, e:
			print e

def check_files_folders_patterns(f, relpath, files_folder):
	# Remove the first pattern found.
	# This is from the current dev app or one from the last installed app to the first.
	files_folder = files_folder or []
	path = os.path.join(relpath, f)
	for pattern in files_folder:
		if pattern.match(f) or pattern.match(path):
			return True
	return False

# copy the translations files from apps from the first installed to the last installed so we can replace with new ones
# project-tap.i18n can be replaced with new data from last installed apps
def copy_meteor_languages(start_folders, dest_folder, appname, psf_out, custom_pattern=None):
	import fnmatch

	pattern, ignored_names_any, ignored_names_top  = custom_pattern
	list_meteor_files_folders_remove = psf_out.get_remove_files_folders()
	all_files_folder_remove = list_meteor_files_folders_remove.get("all")
	appname_files_folder_remove = list_meteor_files_folders_remove.get(appname)

	for st_folder in start_folders:
		for root, dirs, files in os.walk(st_folder):
			ign_dirs = pattern(st_folder, dirs)

			ign_dirs.update(ignored_names_any)

			for toexclude in ign_dirs:
				if toexclude in dirs:
					dirs.remove(toexclude)

			relative_react = os.path.relpath(root, st_folder)
			files = [toinclude for toinclude in files if fnmatch.fnmatch(toinclude, "*i18n.json") or fnmatch.fnmatch(toinclude, "*project-tap.i18n")]

			for f in files:
				if check_files_folders_patterns(f,  relative_react, all_files_folder_remove) or\
						check_files_folders_patterns(f, relative_react, appname_files_folder_remove):
					continue
				try:
					frappe.create_folder(dest_folder)
					os.symlink(os.path.join(root, f), os.path.join(dest_folder, f))

				except:
					pass

def copy_project_translation(apps, whatfor, pfs_out, custom_pattern=None):
	from fluorine.utils import get_meteor_folder_for_site

	folder = get_meteor_folder_for_site(whatfor, frappe.local.site)
	path_reactivity = get_path_reactivity()
	i18n_files_route = "tap-i18n"
	project_file = "project-tap.i18n"
	destpath = os.path.join(path_reactivity, folder, project_file)

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

		copy_meteor_languages([os.path.join(path, i18n_files_route), os.path.join(path, whatfor, i18n_files_route)], os.path.join(path_reactivity, whatfor, i18n_files_route), app, pfs_out, custom_pattern=custom_pattern)


"""
Get the mobile-config.js from current-app. If not exists then copy from the most recent app to the last.
"""
def copy_mobile_config_file(apps, whatfor):
	from fluorine.utils import get_meteor_folder_for_site

	folder = get_meteor_folder_for_site(whatfor, frappe.local.site)
	mobile_file = "mobile-config.js"
	path_reactivity = get_path_reactivity()
	destpath = os.path.join(path_reactivity, folder, mobile_file)

	#from more recent to last.
	for app in apps:
		app_path = frappe.get_app_path(app)
		srcpath = os.path.join(app_path, "templates", "react", whatfor, mobile_file)
		if os.path.exists(srcpath):
			os.symlink(srcpath, destpath)
			return

def remove_templates_react_path_from_source_path(whatfor, source_relative_path):

	if source_relative_path.startswith("templates/react/%s/" % whatfor):
		source_relative_path = source_relative_path.replace("templates/react/%s/" % whatfor, "", 1)
	elif source_relative_path.startswith("templates/react/"):
		source_relative_path = source_relative_path.replace("templates/react/", "", 1)
	elif source_relative_path.startswith("templates/"):
		source_relative_path = source_relative_path.replace("templates/", "", 1)

	return source_relative_path


def make_all_files_with_symlink(known_apps, dst, whatfor):
	from fluorine.utils.apps import get_apps_path_order
	from jinja2 import Environment, PackageLoader


	env = Environment(loader=PackageLoader('fluorine', 'templates'), trim_blocks=True)
	template = env.get_template('package.template')

	pckg_config = frappe._dict({
		"describe": None,
		"versionsFrom": None,
		"api": frappe._dict({"use": [], "imply": [], "export": [], "addFiles": []}),
		"Npm": frappe._dict({}),
		"Cordova": frappe._dict({}),
		"registerBuildPlugin": None
	})

	def add_to_packagejs(api, pckg_config):

		if not pckg_config.describe and api._describe:
			pckg_config.describe = api._describe

		if not pckg_config.registerBuildPlugin:
			pckg_config.registerBuildPlugin = api.registerBuildPlugin

		if not pckg_config.versionsFrom and api._versionsFrom:
			pckg_config.versionsFrom = api._versionsFrom

		pckg_config.api.use.extend(api.api_use)
		pckg_config.api.imply.extend(api.api_imply)
		pckg_config.api.export.extend(api.api_export)

		if api._Npm and api._Npm._depends:
			pckg_config.Npm.update(api._Npm._depends)

		if api._Cordova and api._Cordova._depends:
			pckg_config.Cordova.update(api._Cordova._depends)

	def make_dest_path(type, add_file_path_obj):
		file_appname = add_file_path_obj.get("app")
		source_relative_path = add_file_path_obj.get("relative_path")
		source_relative_path = remove_templates_react_path_from_source_path(whatfor, source_relative_path)
		apps_path_order = get_apps_path_order(file_appname, known_apps)

		if type == "private":
			destpath = os.path.join(dst, "private", apps_path_order)
			dest = os.path.join(destpath, source_relative_path)
			#make_private(meteorpath, destpath, file_appname, whatfor, custom_pattern=None)
		elif type == "tests":
			destpath = os.path.join(dst, "tests", apps_path_order)
			dest = os.path.join(destpath, source_relative_path)
		else:
			destpath = os.path.join(dst, apps_path_order)
			dest = os.path.join(destpath, source_relative_path)

		return dest

	def make_symlink(pckg_obj, dict_files_to_add):
		for add_file_path, add_file_path_obj in dict_files_to_add.iteritems():
			dest_file = os.path.join(pckg_obj.real_path, ".%s" % pckg_obj.folder_name, add_file_path_obj.internal_path)
			if os.path.exists(add_file_path):
				pckg_config.api.addFiles.append({"filenames": add_file_path_obj.internal_path, "architecture": add_file_path_obj.architecture, "options": add_file_path_obj.options})
				os.symlink(add_file_path, dest_file)


	for pckg_name, pckg_obj in frappe.local.packages.iteritems():
		if pckg_name == "fluorine:core":
			for api in pckg_obj.apis:
				for add_file_path, add_file_path_obj in api.get_dict_final_files_add().iteritems():
					dest = make_dest_path(add_file_path_obj.type, add_file_path_obj)
					if os.path.exists(add_file_path):
						if not os.path.exists(dest):
							frappe.create_folder(os.path.dirname(dest))
							os.symlink(add_file_path, dest)
		else:
			for api in pckg_obj.apis:
				add_to_packagejs(api, pckg_config)
				make_symlink(pckg_obj, api.get_dict_final_files_add())
				make_symlink(pckg_obj, api.get_dict_final_Assets_add())

			config = template.render(**pckg_config)
			#print "package.js %s %s" % (config, dest)
			dest = os.path.join(pckg_obj.real_path, ".%s" % pckg_obj.folder_name)
			frappe.create_folder(dest)
			save_file(os.path.join(dest, "package.js"), config)

def make_public(app_path, dst_public_assets_path, app, whatfor, custom_pattern=None):

	folder_path = os.path.join(app_path, "public")
	_make_public_folder(folder_path, dst_public_assets_path, app, whatfor, custom_pattern=custom_pattern)

def _make_public_folder(folder_path, dst_folder_path, app, whatfor, custom_pattern=None):
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
	custom_pattern.update(["build.json"])
	custom_pattern.update(exclude)
	pattern = ignore_patterns(*custom_pattern)

	if os.path.exists(folder_path):
		files = os.listdir(folder_path)
		custom_ign_names = pattern(folder_path, files)

		for f in files:
			if f in custom_ign_names:
				continue
			if app == "fluorine" and f in whatfor:
				continue

			final_dst_path = os.path.join(dst_folder_app_path, f)
			frappe.create_folder(os.path.dirname(final_dst_path))
			if not os.path.exists(final_dst_path):
				os.symlink(os.path.join(folder_path, f), final_dst_path)

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