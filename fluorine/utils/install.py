from __future__ import unicode_literals
__author__ = 'saguas'

import frappe, os
from frappe.website import render, statics
from fluorine.utils import whatfor_all


class MeteorInstalationError(Exception):
	pass


def before_install():

	frappe_module = os.path.dirname(frappe.__file__)
	path_apps = os.path.realpath(os.path.join(frappe_module, "..", ".."))
	path_reactivity = os.path.join(path_apps, "reactivity")

	if not os.path.exists(path_reactivity):
		frappe.create_folder(path_reactivity)

	copy_common_config(path_reactivity)

	from fluorine.utils import get_meteor_configuration_file
	get_meteor_configuration_file()

	update_meteor_config_file()

	create_meteor_apps(path_reactivity=path_reactivity)
	from fluorine.utils.meteor.packages import meteor_add_package, meteor_remove_package
	
	for whatfor in whatfor_all:#("meteor_app", "meteor_web"):
		meteor_add_package("fluorine", whatfor, path_reactivity=path_reactivity)
		meteor_remove_package("fluorine", whatfor, path_reactivity=path_reactivity)

	from fluorine.commands_helpers.meteor import update_versions
	bench = "../../bench-repo/"
	update_versions(bench=bench)


def after_install(rebuild_website=False):

	version = frappe.utils.cint(frappe.__version__.split(".", 1)[0])
	if version >= 5:
		return
	if rebuild_website:
		render.clear_cache()
		statics.sync().start()

	init_singles()
	frappe.db.commit()
	frappe.clear_cache()


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

	#src = os.path.join(app_path, "templates", "permission_files.json")
	#if os.path.exists(src):
	#	dst = os.path.join(path_reactivity, "permission_files.json")
	#	copyfile(src, dst)

def create_meteor_apps(path_reactivity=None):
	import subprocess
	import glob

	if not path_reactivity:
		from file import get_path_reactivity
		path_reactivity = get_path_reactivity()

	try:
		for app in whatfor_all:
			if not os.path.exists(os.path.join(path_reactivity, app)):
				p = subprocess.Popen(["meteor", "create", app], cwd=path_reactivity, shell=False, close_fds=True)
				p.wait()
				meteor_app = os.path.join(path_reactivity, app)
				for f in glob.glob(os.path.join(meteor_app,"meteor_*")):
					os.remove(f)

			elif not os.path.exists(os.path.join(path_reactivity, app, ".meteor")):
				raise MeteorInstalationError("Meteor %s folder exists." % app)

	except:
		print """Error. You must install meteor and node before you can use this app. After that you must create two apps in apps/reactivity folder.
				For that, cd to apps/reactivity and issue 'meteor create meteor_app' and 'meteor create meteor_web'.
				Install the packages that you like and start use frappe. Good Luck!"""


def update_meteor_config_file():
	from fluorine.utils import meteor_config
	from fluorine.commands_helpers import get_default_site
	from fluorine.utils.meteor.utils import update_common_config

	meteor_config["site"] = get_default_site()

	update_common_config(meteor_config)


def init_singles():
	singles = [single['name'] for single in frappe.get_all("DocType", filters={'issingle': True})]
	for single in singles:
		if not frappe.db.get_singles_dict(single):
			doc = frappe.new_doc(single)
			doc.ignore_mandatory=True
			doc.ignore_validate=True
			doc.save()

