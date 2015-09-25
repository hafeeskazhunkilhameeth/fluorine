__author__ = 'luissaguas'

import frappe, os
from fluorine.utils import whatfor_all


#get the list of apps installed by current app and save it. Ignore custom packages (packages installed after app installation)
def cmd_packages_update(curr_app):
	from fluorine.utils.file import save_file
	from fluorine.commands import meteor_echo

	curr_app_path = frappe.get_app_path(curr_app)

	for whatfor in whatfor_all:
		package_file_name = "packages_add_" + whatfor
		dst = os.path.join(curr_app_path, "templates", package_file_name)
		packages_to_add = cmd_packages_from(curr_app, whatfor, package_file_name)
		meteor_echo("%s: installed_packages %s\n" % (whatfor, list(packages_to_add)), 80)
		save_file(dst, "\n".join(packages_to_add))

#get the list of apps installed by current app. Ignore custom packages (packages installed after app installation)
def cmd_packages_from(curr_app, whatfor, package_file_name):
	from fluorine.utils.file import get_path_reactivity
	from fluorine.utils.apps import get_active_apps
	import re

	react_path = get_path_reactivity()

	apps = get_active_apps(whatfor)
	apps.remove(curr_app)
	installed_packages = get_packages_list_version(whatfor, path_reactivity=react_path)
	packages_to_remove = set([])

	for app in apps:
		tmp_app_path = frappe.get_app_path(app)
		tmp_dst = os.path.join(tmp_app_path, "templates", package_file_name)
		tmp_app_pckg = frappe.get_file_items(tmp_dst)
		#Not permited upgrade packages installed by other modules
		for i_pckg in installed_packages:
			for pckg in tmp_app_pckg:
				pckg_name = pckg.split("@=")[0]
				if re.match(pckg_name, i_pckg):
					packages_to_remove.add(pckg)
					break

	return set(installed_packages).difference(packages_to_remove)


def meteor_package(whatfor, packages, path_reactivity=None, action="add"):
	import subprocess, re

	if not path_reactivity:
		from fluorine.utils.file import get_path_reactivity
		path_reactivity = get_path_reactivity()

	cwd = os.path.join(path_reactivity, whatfor)
	if packages:
		meteor_packages = frappe.get_file_items(os.path.join(cwd, ".meteor", "packages"))

		#packages_to_use = []
		#NOTE: Only add packages that do not exist or remove packages that exist

		for pckg in set(packages):
			found = False
			for i_pckg in meteor_packages:
				if re.match(pckg, i_pckg):
					if action == "add":
						packages.remove(pckg)
						print "{}: {} already exist - no action was taken. Try to update.".format(whatfor, pckg)
					found = True
					break
			if not found and action == "remove":
				packages.remove(pckg)
				print "{}: {} does not exist - no action was taken.".format(whatfor, pckg)

		if packages:
			print "{}: action: {}".format(whatfor, action)
			args = ["meteor", action]
			args.extend(packages)
			p = subprocess.Popen(args, cwd=cwd, shell=False, close_fds=True)
			p.wait()

		return True

	return False


def get_packages_list_version(whatfor, path_reactivity=None):
	import subprocess, click, re

	if not path_reactivity:
		from fluorine.utils.file import get_path_reactivity
		path_reactivity = get_path_reactivity()

	pkg_list = []
	args = ["meteor", "list"]
	cwd = os.path.join(path_reactivity, whatfor)
	click.echo("%s: Getting meteor installed packages. Please wait." % whatfor)
	package_list_version = subprocess.check_output(args, cwd=cwd, shell=False, close_fds=True)

	for package in [p.strip() for p in package_list_version.splitlines() if p.strip() and not (p.startswith("#") or p.startswith("*"))]:
		p = package.split()
		#print "p={}".format(p)
		if len(p) > 1 and re.match(r"(?:\d.?)", p[1]):
			pkg_list.append("%s@=%s" %(p[0], re.sub(r"[^\d.|^_]+", "", p[1])))

	return pkg_list


def get_packages_file(app, package_name):

	app_path = frappe.get_app_path(app)
	packages_path = os.path.join(app_path, "templates", package_name)
	if os.path.exists(packages_path):
		packages = frappe.get_file_items(packages_path)
		return packages

def get_default_packages_file_name(action, whatfor):
	return "custom_packages_%s_%s" % (action, whatfor)

def meteor_package_list(whatfor, packages=None, path_reactivity=None, action="add"):
	meteor_package(whatfor, packages, path_reactivity=path_reactivity, action=action)


def meteor_reset_package(app, whatfor, file_add=None, file_remove=None, path_reactivity=None):

	if not file_add:
		file_add = get_default_packages_file_name("add", whatfor)
	if not file_remove:
		file_remove = get_default_packages_file_name("remove", whatfor)

	packages_add = get_packages_file(app, file_add)
	packages_remove = get_packages_file(app, file_remove)

	meteor_package_list(whatfor, packages=packages_remove, path_reactivity=path_reactivity, action="remove")
	meteor_package_list(whatfor, packages=packages_add, path_reactivity=path_reactivity, action="add")


def meteor_add_package(app, whatfor, file_add=None, path_reactivity=None):
	package_name = "packages_add_%s" % whatfor
	packages = get_packages_file(app, package_name)
	meteor_package_list(whatfor, packages=packages, path_reactivity=path_reactivity, action="add")

	if not file_add:
		file_add = get_default_packages_file_name("add", whatfor)

	packages_add = get_packages_file(app, file_add)
	meteor_package_list(whatfor, packages=packages_add, path_reactivity=path_reactivity, action="add")


def meteor_remove_package(app, whatfor, file_remove=None, path_reactivity=None):
	package_name = "packages_remove_%s" % whatfor
	packages = get_packages_file(app, package_name)
	meteor_package_list(whatfor, packages=packages, path_reactivity=path_reactivity, action="remove")

	if not file_remove:
		file_remove = get_default_packages_file_name("remove", whatfor)

	packages_remove = get_packages_file(app, file_remove)
	meteor_package_list(whatfor, packages=packages_remove, path_reactivity=path_reactivity, action="remove")


def get_list_packages_to_install_by_apps(curr_app, whatfor, file_add=None, file_remove=None):
	from fluorine.utils.apps import get_active_apps

	packages_to_add = {}
	packages_to_remove = {}

	def _get_file(f):
		file_src = []
		if os.path.exists(f):
			file_src = frappe.get_file_items(f)

		return file_src

	def _package(app, fadd, fremove):
		for pckg in fadd:
			#pckg_name = pckg.split("@=")[0]
			if not packages_to_add.get(app, None):
				packages_to_add[app] = []
			packages_to_add.get(app).append(pckg)

		for pckg in fremove:
			#pckg_name = pckg.split("@=")[0]
			try:
				if not packages_to_remove.get(app, None):
					packages_to_remove[app] = []
				packages_to_remove.get(app).append(pckg)
			except:
				pass

	package_file_name_add = "packages_add_" + whatfor
	package_file_name_remove = "packages_remove_" + whatfor


	if not file_add:
		file_add = get_default_packages_file_name("add", whatfor)
	if not file_remove:
		file_remove = get_default_packages_file_name("remove", whatfor)

	#apps from first installed to the last
	apps = get_active_apps(whatfor)
	apps.remove(curr_app)

	apps.append(curr_app)

	for app in apps:
		app_path = frappe.get_app_path(app)
		for file_par in [(package_file_name_add, package_file_name_remove), (file_add, file_remove)]:
			src_add = os.path.join(app_path, "templates", file_par[0])
			file_src_add = _get_file(src_add)
			src_remove = os.path.join(app_path, "templates", file_par[1])
			file_src_remove = _get_file(src_remove)
			#src_custom_add = os.path.join(app_path, "templates", file_add)
			#file_custom_add = _get_file(src_custom_add)
			#src_custom_remove = os.path.join(app_path, "templates", file_remove)
			#file_custom_remove = _get_file(src_custom_remove)

			_package(app, file_src_add, file_src_remove)
			#_package(app, file_custom_add, file_custom_remove)

	return packages_to_add, packages_to_remove


def get_package_list_updates(curr_app, whatfor, file_add=None, file_remove=None):
	from fluorine.utils.file import get_path_reactivity
	from fluorine.utils.apps import get_active_apps
	import re

	packages_to_add = set([])
	packages_to_remove = set([])
	package_add, package_remove = get_list_packages_to_install_by_apps(curr_app, whatfor, file_add=file_add, file_remove=file_remove)

	react_path = get_path_reactivity()
	installed_packages = get_packages_list_version(whatfor, path_reactivity=react_path)

	apps = get_active_apps(whatfor)
	apps.remove(curr_app)

	apps.append(curr_app)

	#apps first installed to last installed. Current app last
	for app in apps:
		pckgs = package_remove.get(app) or []
		for pckg in pckgs:
			found = False
			pckg_name = pckg.split("@=")[0]
			for i_pckg in installed_packages:
				if re.match(pckg_name, i_pckg):
					found = True
					break
			if found:
				packages_to_remove.add(pckg)

			if pckg in packages_to_add:
				packages_to_add.remove(pckg)

		pckgs = package_add.get(app) or []
		for pckg in pckgs:
			found = False
			pckg_name = pckg.split("@=")[0]
			for i_pckg in installed_packages:
				if re.match(pckg_name, i_pckg):
					found = True
					break
			if not found:
				packages_to_add.add(pckg)

			if pckg in packages_to_remove:
				packages_to_remove.remove(pckg)

	pckg_remove = [pckg.split("@=")[0] for pckg in packages_to_remove]

	return packages_to_add, pckg_remove, installed_packages


def update_packages_list(curr_app, file_add=None, file_remove=None):

	for whatfor in whatfor_all:
		pckg_add, pckg_remove, i_pckgs = get_package_list_updates(curr_app, whatfor, file_add=file_add, file_remove=file_remove)
		print_meteor_packages_list(whatfor, pckg_add, pckg_remove, i_pckgs)
		meteor_package(whatfor, pckg_remove, path_reactivity=None, action="remove")
		meteor_package(whatfor, pckg_add, path_reactivity=None, action="add")


def print_meteor_packages_list(whatfor, pckg_add, pckg_remove, i_pckgs):
	from fluorine.commands import meteor_echo

	meteor_echo("%s:\n packages to add = %s\n packages to remove = %s\n\n installed_packages %s\n" % (whatfor, list(pckg_add), list(pckg_remove), i_pckgs), 80)


#used with directives api.use and api.addFile and api.add_file
def get_list_package_directive(directive, content):
	import re

	use = re.findall("%s\([\"'](.+?)[\"']" % directive.strip(), content, re.S|re.M)
	return use


def get_package_name_from_content(content):
	import re

	name = None
	for line in content.split("\n"):
		line_search = re.search("name:\s*[\"'](.*?)[\"']", line, re.S)
		if line_search:
			name = line_search.group(1)
			break
	#use = re.findall("%s\([\"'](.+?)[\"']" % directive.strip(), content, re.S|re.M)
	return name


def get_list_diff(original_list, new_list):
	return set(original_list).difference(set(new_list))

def make_list_installed_packages():
	from fluorine.utils import get_meteor_path, fluorine_common_data
	import os

	for whatfor in whatfor_all:
		meteor_path = get_meteor_path(whatfor)

		packages_path = os.path.join(meteor_path, ".meteor", "packages")
		packages_list = frappe.get_file_items(packages_path)

		fluorine_common_data.meteor_packages_list[whatfor] = packages_list

	return


def get_list_installed_packages(whatfor):
	from fluorine.utils import fluorine_common_data

	packages_list = fluorine_common_data.meteor_packages_list.get(whatfor)

	return packages_list


def is_meteor_package_installed(pckg, whatfor):
	installed_packg = get_list_installed_packages(whatfor)

	pckg_strip_version = pckg.split("@")[0]
	if pckg_strip_version in installed_packg:
		return True

	return False


def get_read_order_apps():
	ordered_apps = []

	for v in frappe.local.meteor_map_templates.values():
		appname = v.get("appname")
		if appname not in ordered_apps:
			ordered_apps.append(appname)

	return ordered_apps


def get_valid_dir_packages_from_path(packagespath, whatfor):
	dirs = os.listdir(packagespath)

	for dir in dirs[:]:
		if not is_meteor_package_installed(dir, whatfor):
			dirs.remove(dir)

	return dirs

def get_appname_from_package_addFile_directive(filepath, use_default=None):
	from fluorine.utils import APPS as system_apps

	appname = filepath.split("/",1)[0]

	if appname in system_apps:
		return appname

	return use_default


def process_meteor_packages_from_apps_first(whatfor):

	API_ADDFILES = "api.addFiles"
	API_ADD_FILES = "api.add_files"
	processed_packages = []
	#readed_apps = frappe.local.files_to_add.keys()
	ordered_apps = get_read_order_apps()

	for app in ordered_apps:
		pathname = frappe.get_app_path(app)
		reactpath = os.path.join(pathname, "templates", "react")
		app_packages_path = os.path.join(reactpath, whatfor, "packages")
		if os.path.exists(app_packages_path):
			dirs = os.listdir(app_packages_path)
			for dir in dirs:
				package_start_path = os.path.join(app_packages_path, dir)
				packagejs_file_path = os.path.join(package_start_path, "package.js")
				if os.path.exists(packagejs_file_path):
					packagejs_file_content = frappe.read_file(packagejs_file_path)
					name_package = get_package_name_from_content(packagejs_file_content)
					if name_package in processed_packages or not is_meteor_package_installed(name_package, whatfor):
						continue

					processed_packages.append(name_package)
					list_api_addFile = get_list_package_directive(API_ADDFILES, packagejs_file_content)
					list_api_add_file = get_list_package_directive(API_ADD_FILES, packagejs_file_content)
					list_api_addFile.extend(list_api_add_file)
					print "list addFile {}".format(list_api_addFile)
					copy_file_package_to_meteor_packages(app, dir, whatfor, list_api_addFile)


def process_meteor_packages_from_apps(whatfor):

	copy_file_package_to_meteor_packages(app, dir, whatfor, list_api_addFile)


def copy_file_package_to_meteor_packages(app, dir, whatfor, list_api_addFile):
	from fluorine.utils.file import get_path_reactivity

	reactivity_path = get_path_reactivity()
	dest_meteor_packages_path = os.path.join(reactivity_path, whatfor, "packages")

	print "copying... whatfor {} app {} list {}".format(whatfor, app, list_api_addFile)
	for filepath in list_api_addFile:
		appname = get_appname_from_package_addFile_directive(filepath, use_default=app)
		#for root, packg_dirs, files in os.walk(package_start_path):
		if appname == app:
			filepath = filepath.replace("%s/" % appname, "", 1)

		pathname = frappe.get_app_path(appname)
		reactpath = os.path.join(pathname, "templates", "react")
		app_packages_path = os.path.join(reactpath, whatfor, "packages")

		source_path = os.path.join(app_packages_path, dir, filepath.replace("%s/" % appname, "", 1))

		filepathlist = filepath.rsplit("/", 1)
		if len(filepathlist) > 1:
			filename = filepathlist[1]
		else:
			filename = filepathlist[0]

		file_path_dir = os.path.dirname(filepath)
		dest_package_path_dir = os.path.join(dest_meteor_packages_path, dir, file_path_dir)
		frappe.create_folder(dest_package_path_dir)
		os.symlink(source_path, os.path.join(dest_package_path_dir, filename))

	#copy package.js from processed app
	pathname = frappe.get_app_path(app)
	reactpath = os.path.join(pathname, "templates", "react")
	app_packages_path = os.path.join(reactpath, whatfor, "packages")
	dest_package_path = os.path.join(dest_meteor_packages_path, dir, "package.js")
	frappe.create_folder(os.path.dirname(dest_package_path))
	os.symlink(os.path.join(app_packages_path, dir, "package.js"), os.path.join(dest_meteor_packages_path, dir, "package.js"))

