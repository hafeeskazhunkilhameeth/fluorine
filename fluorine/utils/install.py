from __future__ import unicode_literals
__author__ = 'saguas'

import frappe, os
from frappe.website import render, statics



class MeteorInstalationError(Exception):
	pass


def before_install():
	from file import get_path_reactivity
	from fluorine.commands_helpers.meteor import update_versions

	path_reactivity = get_path_reactivity()
	if not os.path.exists(path_reactivity):
		frappe.create_folder(path_reactivity)

	make_link_to_desk()
	copy_common_config(path_reactivity)
	create_meteor_apps(path_reactivity=path_reactivity)
	for package_name in ("meteor_app", "meteor_web"):
		meteor_add_package("fluorine", package_name, path_reactivity=path_reactivity)

	update_versions()
	#make_public_symbolic_link(path_reactivity)


def after_install(rebuild_website=False):
	from shutil import copyfile

	#TODO chage the hook and build files
	app_path = frappe.get_app_path("fluorine")
	hooks_default = os.path.join(app_path, "templates", "hooks_default.py")
	hooks = os.path.join(app_path, "hooks.py")
	copyfile(hooks_default, hooks)

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
	app_path = frappe.get_app_path("fluorine")
	source = os.path.join(frappe_path, "templates", "pages", "desk.html")
	link_name = os.path.join(app_path, "templates", "pages", "mdesk.html")
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


def meteor_package(app, package_name, path_reactivity=None, action="add"):
	import subprocess
	#from fluorine.utils.file import readlines

	if not path_reactivity:
		from file import get_path_reactivity
		path_reactivity = get_path_reactivity()

	app_path = frappe.get_app_path(app)
	cwd = os.path.join(path_reactivity, app)
	packages_path = os.path.join(app_path, "templates", "packages_" + action + "_" + package_name)
	if os.path.exists(packages_path):
		packages = frappe.get_file_items(packages_path)
		meteor_packages = frappe.get_file_items(os.path.join(path_reactivity, package_name, ".meteor", "packages"))

		#NOTE: Only add packages that do not exist or remove packages that exist
		for pckg in packages:
			if pckg in meteor_packages:
				if action == "add":
					packages.remove(pckg)
			elif action == "remove":
				packages.remove(pckg)

		#packages = readlines(packages_path)
		#p = subprocess.Popen(["meteor", "add", " ".join([line for line in packages if not line.startswith("#")])], cwd=cwd, shell=False, close_fds=True)
		p = subprocess.Popen(["meteor", action, " ".join(packages)], cwd=cwd, shell=False, close_fds=True)
		p.wait()


def meteor_add_package(app, package_name, path_reactivity=None):
	meteor_package(app, package_name, path_reactivity=path_reactivity, action="add")


def meteor_remove_package(app, package_name, path_reactivity=None):
	meteor_package(app, package_name, path_reactivity=path_reactivity, action="remove")

	"""
	if not path_reactivity:
		from file import get_path_reactivity
		path_reactivity = get_path_reactivity()

	app_path = frappe.get_app_path(app)
	cwd = os.path.join(path_reactivity, app)
	packages_path = os.path.join(app_path, "templates", "packages_" + app)
	#packages = readlines(packages_path)
	packages = frappe.get_file_items(packages_path)
	#p = subprocess.Popen(["meteor", "remove", " ".join([line for line in packages if not line.startswith("#")])], cwd=os.path.join(path_reactivity, app), shell=False, close_fds=True)
	p = subprocess.Popen(["meteor", "remove", " ".join(packages)], cwd=cwd, shell=False, close_fds=True)
	p.wait()
	"""


def init_singles():
	singles = [single['name'] for single in frappe.get_all("DocType", filters={'issingle': True})]
	for single in singles:
		if not frappe.db.get_singles_dict(single):
			doc = frappe.new_doc(single)
			doc.ignore_mandatory=True
			doc.ignore_validate=True
			doc.save()

