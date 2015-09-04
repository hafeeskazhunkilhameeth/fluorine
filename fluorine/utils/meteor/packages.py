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
	from fluorine.commands_helpers.meteor import get_active_apps
	import re

	react_path = get_path_reactivity()

	apps = get_active_apps()
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

		for pckg in packages[:]:
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
	from fluorine.commands_helpers.meteor import get_active_apps

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
	apps = get_active_apps()
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
	from fluorine.commands_helpers.meteor import get_active_apps
	import re

	packages_to_add = set([])
	packages_to_remove = set([])
	package_add, package_remove = get_list_packages_to_install_by_apps(curr_app, whatfor, file_add=file_add, file_remove=file_remove)

	react_path = get_path_reactivity()
	installed_packages = get_packages_list_version(whatfor, path_reactivity=react_path)

	apps = get_active_apps()
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
