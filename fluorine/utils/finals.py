__author__ = 'luissaguas'

import frappe, os


def make_public_folders():
	from fluorine.utils import meteor_desk_app

	app_path = frappe.get_app_path("fluorine")
	for whatfor in (meteor_desk_app, ):#("meteor_app", "meteor_web"):
		public_app_folder = os.path.join(app_path, "public", whatfor)
		frappe.create_folder(public_app_folder)


def copy_meteor_runtime_config():
	from shutil import copyfile
	from fluorine.utils import meteor_desk_app

	app_path = frappe.get_app_path("fluorine")
	public_folder = os.path.join(app_path, "public")
	meteor_runtime_file = os.path.join(public_folder, meteor_desk_app, "meteor_runtime_config.js")
	copyfile(meteor_runtime_file, os.path.join(public_folder, "js", "meteor_runtime_config.js"))


def make_production_link():
	from fluorine.utils.file import get_path_reactivity
	from fluorine.utils import meteor_web_app

	path_reactivity = get_path_reactivity()
	final_web_path = os.path.join(path_reactivity, meteor_web_app.replace("meteor", "final"), "bundle", "programs", "web.browser")
	meteor_web_path = os.path.join("assets", "js", meteor_web_app)
	if os.path.exists(final_web_path):
		try:
			os.symlink(final_web_path, meteor_web_path)
		except:
			pass


def remove_public_link():
	from fluorine.utils.react_file_loader import remove_directory
	from fluorine.utils import meteor_desk_app

	app_path = frappe.get_app_path("fluorine")
	public_folder = os.path.join(app_path, "public")

	for app in (meteor_desk_app, ):
		folder = os.path.join(public_folder, app)
		remove_directory(folder)


def make_final_app_client(jquery=0):
	import json
	from fluorine.utils.file import get_path_reactivity, read, save_js_file
	from fluorine.utils import meteor_desk_app

	react_path = get_path_reactivity()

	meteor_final_path = os.path.join(react_path, "final_app/bundle/programs/web.browser")
	progarm_path = os.path.join(meteor_final_path, "program.json")

	if os.path.exists(progarm_path):

		fluorine_path = frappe.get_app_path("fluorine")
		build_file = os.path.join(fluorine_path, "public", "build.json")

		if os.path.exists(build_file):
			build_json_file = read(build_file)
			build_json = json.loads(build_json_file)
		else:
			build_json = frappe._dict()

		build_json["js/meteor_app.min.js"] = ["public/%s/meteor_runtime_config.js" % meteor_desk_app]
		build_json["css/meteor_app.css"] = []

		manifest = read(progarm_path)

		manifest = json.loads(manifest).get("manifest")

		build_frappe_json_files(manifest, build_json, jquery=jquery)

		save_js_file(build_file, build_json)


def build_frappe_json_files(manifest, build_json, jquery=0):
	from fluorine.utils.file import get_path_reactivity

	react_path = get_path_reactivity()

	for m in manifest:
		if m.get("where") == "client":
			path = m.get("path")
			if "jquery" in path and jquery == 0:
				continue

			pack_path = os.path.join(react_path, "final_app/bundle/programs/web.browser", path)
			type = m.get("type") == "js"
			if type:
				build_json["js/meteor_app.min.js"].append(pack_path)
			elif type == "css":
				build_json["css/meteor_app.css"].append(pack_path)