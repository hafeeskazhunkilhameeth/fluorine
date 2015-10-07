__author__ = 'luissaguas'


import frappe,os
from fluorine.utils import whatfor_all, meteor_desk_app, meteor_web_app


active_apps = {meteor_desk_app: None, meteor_web_app: None}


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


def get_list_all_sites(bench=None):
	from fluorine.commands_helpers.bench_helpers import execute_bench_func

	if not bench:
		bench = "../../bench-repo/"

	sites = execute_bench_func("utils", "get_sites", bench)

	return sites


def get_active_apps(whatfor):
	from fluorine.utils import APPS as apps, get_attr_from_json, meteor_config
	from fluorine.utils.permission_file import make_ignor_apps_list, list_ignores, is_app_for_site


	if active_apps.get(whatfor) != None:
		return active_apps.get(whatfor)[:]

	list_ignores = make_ignor_apps_list()

	ign_apps = get_attr_from_json([whatfor, "remove", "apps"], list_ignores)

	only_for_sites = get_attr_from_json([whatfor, "only_for_sites"], list_ignores)


	known_apps = apps[::]

	for ign in ign_apps:
		try:
			known_apps.remove(ign)
		except:
			pass

	curr_app = meteor_config.get("current_dev_app", "").strip()
	if curr_app != known_apps[-1]:
		#set current dev app in last
		known_apps.remove(curr_app)
		known_apps.append(curr_app)

	aapps = []
	#current dev apps go in last
	for app in known_apps:
		if is_app_for_site(app, only_for_sites):
			aapps.append(app)

	active_apps[whatfor] = aapps

	return active_apps.get(whatfor)[:]


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


def get_apps_path_order(appname, apps):

	path = ""

	for app in apps:
		path = os.path.join(path, app)
		if app == appname:
			break

	return path