from __future__ import unicode_literals
__author__ = 'saguas'

import frappe, os
from frappe.website import render, statics


def before_install():
	from file import get_path_reactivity

	path_reactivity = get_path_reactivity()
	if not os.path.exists(path_reactivity):
		frappe.create_folder(path_reactivity)

	make_link_to_desk()
	copy_common_config(path_reactivity)
	create_meteor_apps(path_reactivity)
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

def create_meteor_apps(path_reactivity):
	import subprocess
	import glob

	try:
		app_path = frappe.get_app_path("fluorine")
		for app in ("meteor_app", "meteor_web"):
			p = subprocess.Popen(["meteor", "create", app], cwd=path_reactivity, shell=False, close_fds=True)
			p.wait()
			meteor_app = os.path.join(path_reactivity, app)
			for f in glob.glob(os.path.join(meteor_app,"meteor_*")):
				os.remove(f)

			meteor_add_package(app_path, app, path_reactivity)
			#p = subprocess.Popen(["meteor", "run"], cwd=os.path.join(path_reactivity, app), shell=False, close_fds=True)
			#p.wait()
	except:
		print """Error. You must install meteor and node before you can use this app. After that you must create two apps in apps/reactivity folder.
				For that, cd to apps/reactivity and issue 'meteor create meteor_app' and 'meteor create meteor_web'.
				Install the packages that you like and start use frappe. Good Luck!"""


def meteor_add_package(app_path, app, path_reactivity):
	import subprocess
	from fluorine.utils.file import readlines

	packages_path = os.path.join(app_path, "templates", "packages_" + app)
	packages = readlines(packages_path)
	p = subprocess.Popen(["meteor", "add", " ".join([line for line in packages if not line.startswith("#")])], cwd=os.path.join(path_reactivity, app), shell=False, close_fds=True)
	p.wait()


def meteor_remove_package(app_path, app, path_reactivity):
	import subprocess
	from fluorine.utils.file import readlines

	packages_path = os.path.join(app_path, "templates", "packages_" + app)
	packages = readlines(packages_path)
	p = subprocess.Popen(["meteor", "remove", " ".join([line for line in packages if not line.startswith("#")])], cwd=os.path.join(path_reactivity, app), shell=False, close_fds=True)
	p.wait()


def init_singles():
	singles = [single['name'] for single in frappe.get_all("DocType", filters={'issingle': True})]
	for single in singles:
		if not frappe.db.get_singles_dict(single):
			doc = frappe.new_doc(single)
			doc.ignore_mandatory=True
			doc.ignore_validate=True
			doc.save()

