from __future__ import unicode_literals
__author__ = 'saguas'

import frappe, os
from frappe.website import render, statics



class MeteorInstalationError(Exception):
	pass


def before_install():
	from shutil import copyfile


	print "prepare to copy hooks"
	frappe_module = os.path.dirname(frappe.__file__)
	path_apps = os.path.realpath(os.path.join(frappe_module, "..", ".."))
	#TODO chage the hook and build files
	#fluorine_path = frappe.get_app_path("fluorine")
	fluorine_path = os.path.join(path_apps, "fluorine", "fluorine")
	hooks_default = os.path.join(fluorine_path, "templates", "hooks_default.py")
	hooks = os.path.join(fluorine_path, "hooks.py")
	copyfile(hooks_default, hooks)

	#print "bench current working dir {}".format(os.getcwd())
	#app_path = frappe.get_app_path("fluorine")
	#path_reactivity = os.path.realpath(os.path.join(cwd, ".."))
	path_reactivity = os.path.join(path_apps, "reactivity")

	if not os.path.exists(path_reactivity):
		frappe.create_folder(path_reactivity)

	copy_common_config(path_reactivity)
	#from file import get_path_reactivity

	#path_reactivity = get_path_reactivity()

	make_link_to_desk()

	#from fluorine.utils.reactivity import meteor_config
	from fluorine.utils import get_meteor_configuration_file
	get_meteor_configuration_file()

	create_meteor_apps(path_reactivity=path_reactivity)
	for whatfor in ("meteor_app", "meteor_web"):
		meteor_add_package("fluorine", whatfor, path_reactivity=path_reactivity)

	from fluorine.commands_helpers.meteor import update_versions
	bench = "../../bench-repo/"
	update_versions(bench=bench)
	#make_public_symbolic_link(path_reactivity)


def after_install(rebuild_website=False):
	#gitignore file for hook.py
	#gitignore_default = os.path.join(fluorine_path, "templates", "gitignore")
	#copyfile(gitignore_default, os.path.join(fluorine_path, ".gitignore"))


	version = frappe.utils.cint(frappe.__version__.split(".", 1)[0])
	if version >= 5:
		return
	if rebuild_website:
		render.clear_cache()
		statics.sync().start()

	init_singles()
	frappe.db.commit()
	frappe.clear_cache()

"""
def make_public_symbolic_link(path_reactivity):
	app_path = frappe.get_app_path("fluorine")
	public_folder = os.path.join(app_path, "public")

	for app in ("meteor_app", "meteor_web"):
		folder = os.path.join(public_folder, app)
		frappe.create_folder(folder)
		#source = os.path.join(path_reactivity, app, ".meteor", "local", "build", "programs", "web.browser")
		#link_name = os.path.join(folder, "webbrowser")

		#os.symlink(source, link_name)
"""

def make_link_to_desk():
	frappe_path = frappe.get_app_path("frappe")
	fluorine_path = frappe.get_app_path("fluorine")
	source = os.path.join(frappe_path, "templates", "pages", "desk.html")
	link_name = os.path.join(fluorine_path, "templates", "pages", "mdesk.html")
	if not os.path.exists(link_name):
		os.symlink(source, link_name)

def copy_common_config(path_reactivity):
	from shutil import copyfile

	app_path = frappe.get_app_path("fluorine")
	src = os.path.join(app_path, "templates", "common_site_config.json")
	dst = os.path.join(path_reactivity, "common_site_config.json")

	copyfile(src, dst)

	try:
		src = os.path.join(app_path, "templates", "permission_files.json")
		dst = os.path.join(path_reactivity, "permission_files.json")
		copyfile(src, dst)
	except:
		pass

def create_meteor_apps(path_reactivity=None):
	import subprocess
	import glob

	if not path_reactivity:
		from file import get_path_reactivity
		path_reactivity = get_path_reactivity()

	try:
		for app in ("meteor_app", "meteor_web"):
			if not os.path.exists(os.path.join(path_reactivity, app)):
				p = subprocess.Popen(["meteor", "create", app], cwd=path_reactivity, shell=False, close_fds=True)
				p.wait()
				meteor_app = os.path.join(path_reactivity, app)
				for f in glob.glob(os.path.join(meteor_app,"meteor_*")):
					os.remove(f)

			elif not os.path.exists(os.path.join(path_reactivity, app, ".meteor")):
				raise MeteorInstalationError("Meteor %s folder exists." % app)

			#p = subprocess.Popen(["meteor", "run"], cwd=os.path.join(path_reactivity, app), shell=False, close_fds=True)
			#p.wait()
	except:
		print """Error. You must install meteor and node before you can use this app. After that you must create two apps in apps/reactivity folder.
				For that, cd to apps/reactivity and issue 'meteor create meteor_app' and 'meteor create meteor_web'.
				Install the packages that you like and start use frappe. Good Luck!"""


def meteor_package(whatfor, packages, path_reactivity=None, action="add"):
	import subprocess

	if not path_reactivity:
		from file import get_path_reactivity
		path_reactivity = get_path_reactivity()

	#app_path = frappe.get_app_path(app)
	cwd = os.path.join(path_reactivity, whatfor)
	#packages_path = os.path.join(app_path, "templates", package_name)
	#if os.path.exists(packages_path):
	if packages:
		#packages = frappe.get_file_items(packages_path)
		meteor_packages = frappe.get_file_items(os.path.join(cwd, ".meteor", "packages"))

		#NOTE: Only add packages that do not exist or remove packages that exist
		for pckg in packages[:]:
			if pckg in meteor_packages:
				if action == "add":
					packages.remove(pckg)
					print "{}: {} already exist - no action was taken.".format(whatfor, pckg)
			elif action == "remove":
				packages.remove(pckg)
				print "{}: {} does not exist - no action was taken.".format(whatfor, pckg)

		#packages = readlines(packages_path)
		#p = subprocess.Popen(["meteor", "add", " ".join([line for line in packages if not line.startswith("#")])], cwd=cwd, shell=False, close_fds=True)
		if packages:
			print "{}: action: {}".format(whatfor, action)
			args = ["meteor", action]
			args.extend(packages)
			p = subprocess.Popen(args, cwd=cwd, shell=False, close_fds=True)
			p.wait()

		return True

	return False


def get_packages_file(app, package_name):

	app_path = frappe.get_app_path(app)
	packages_path = os.path.join(app_path, "templates", package_name)
	if os.path.exists(packages_path):
		packages = frappe.get_file_items(packages_path)
		return packages

def get_default_packages_file(action, whatfor):
	return "custom_packages_%s_%s" % (action, whatfor)

def meteor_package_list(whatfor, packages=None, path_reactivity=None, action="add"):
	meteor_package(whatfor, packages, path_reactivity=path_reactivity, action=action)


def meteor_reset_package(app, whatfor, file_add=None, file_remove=None, path_reactivity=None):

	if not file_add:
		file_add = get_default_packages_file("add", whatfor)
	if not file_remove:
		file_remove = get_default_packages_file("remove", whatfor)

	packages_add = get_packages_file(app, file_add)
	packages_remove = get_packages_file(app, file_remove)

	#meteor_package(whatfor, packages_add, path_reactivity=path_reactivity, action="remove")
	meteor_package_list(whatfor, packages=packages_remove, path_reactivity=path_reactivity, action="remove")
	#meteor_package(whatfor, packages_remove, path_reactivity=path_reactivity, action="add")
	meteor_package_list(whatfor, packages=packages_add, path_reactivity=path_reactivity, action="add")


def meteor_add_package(app, whatfor, file_add=None, path_reactivity=None):
	package_name = "packages_add_%s" % whatfor
	packages = get_packages_file(app, package_name)
	#meteor_package(whatfor, packages, path_reactivity=path_reactivity, action="add")
	meteor_package_list(whatfor, packages=packages, path_reactivity=path_reactivity, action="add")

	if not file_add:
		file_add = get_default_packages_file("add", whatfor)

	packages_add = get_packages_file(app, file_add)

	#meteor_package(whatfor, packages_add, path_reactivity=path_reactivity, action="add")
	meteor_package_list(whatfor, packages=packages_add, path_reactivity=path_reactivity, action="add")


def meteor_remove_package(app, whatfor, file_remove=None, path_reactivity=None):
	#package_name = "packages_remove_%s" % whatfor
	#meteor_package(app, whatfor, package_name, path_reactivity=path_reactivity, action="remove")
	if not file_remove:
		file_remove = get_default_packages_file("remove", whatfor)

	packages_remove = get_packages_file(app, file_remove)

	meteor_package_list(whatfor, packages=packages_remove, path_reactivity=path_reactivity, action="remove")
	#meteor_package(whatfor, packages_remove, path_reactivity=path_reactivity, action="remove")


def init_singles():
	singles = [single['name'] for single in frappe.get_all("DocType", filters={'issingle': True})]
	for single in singles:
		if not frappe.db.get_singles_dict(single):
			doc = frappe.new_doc(single)
			doc.ignore_mandatory=True
			doc.ignore_validate=True
			doc.save()

