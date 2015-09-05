__author__ = 'luissaguas'


import frappe,os
from fluorine.utils import whatfor_all


def is_valid_fluorine_app(app, whatfor=None):

	if not whatfor:
		whatfor = whatfor_all
	elif isinstance(whatfor, basestring):
		whatfor = [whatfor]

	for w in whatfor:
		apps = get_active_apps(w)
		if app in apps:
			return True

	return False


def get_active_apps(whatfor):
	from fluorine.utils import APPS as apps, get_attr_from_json
	from fluorine.utils.reactivity import make_meteor_ignor_files, list_ignores

	if not list_ignores:
		list_ignores = make_meteor_ignor_files()

	#ign_apps = ign_files.remove.get("apps")
	ign_apps = get_attr_from_json([whatfor, "remove", "apps"], list_ignores)

	active_apps = []
	for app in apps:
		app_path = frappe.get_app_path(app)
		meteor_app = os.path.join(app_path, "templates", "react", whatfor)
		#meteor_web = os.path.join(app_path, "templates", "react", meteor_web_app)
		#if (os.path.exists(meteor_app) or os.path.exists(meteor_web)) and app not in ign_apps:
		if os.path.exists(meteor_app) and app not in ign_apps:
			active_apps.append(app)

	return active_apps


def check_meteor_apps_created(with_error=True):
	from fluorine.utils.file import get_path_reactivity
	from frappe import _
	from fluorine.utils import meteor_desk_app, meteor_web_app

	path_reactivity = get_path_reactivity()
	meteor_web = os.path.join(path_reactivity, meteor_web_app, ".meteor")
	meteor_app = os.path.join(path_reactivity, meteor_desk_app, ".meteor")
	msg = "Please install meteor app first. From command line issue 'bench fluorine create-meteor-apps.'"
	error = False

	web_folder_exist = os.path.exists(meteor_web)
	app_folder_exist = os.path.exists(meteor_app)

	if not (web_folder_exist and app_folder_exist):
		error = True

	if with_error and error:
		frappe.throw(_(msg))

	return not error
