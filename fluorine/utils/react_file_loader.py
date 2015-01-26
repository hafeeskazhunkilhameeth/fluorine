__author__ = 'luissaguas'

import frappe, os, re
import fluorine as fluor

"""
client file loader
for each module read files with extension js
special atention to files in client/compatibility
ignore files in tests, in public in private and server
files in lib first and inside lib alphabetic order
other folders deepest first
files with main.* (start with main) are load last
"""

react = {"Reactive Web": "web", "Reactive App": "app", "Both": "both"}

def copy_file(src, dst):
	import shutil
	shutil.copyfile(src, dst)

def remove_directory(path):
	import shutil
	shutil.rmtree(path)


def get_js_to_client():
	fluorine_temp_path = os.path.join(frappe.get_app_path("fluorine"), "templates", "react", "temp")
	frappe.create_folder(fluorine_temp_path)
	copy_client_files(fluorine_temp_path)
	files_in_lib, files_to_read, main_files = read_client_files(fluorine_temp_path)
	hooks_js = move_to_public(fluorine_temp_path, files_in_lib, files_to_read, main_files)

	remove_directory(fluorine_temp_path)

	return hooks_js


def move_to_public(fluorine_temp_path, files_in_lib, files_to_read, main_files):
	#{"name":file, "path": path}
	hooks_js = {"client_hooks_js":[]}
	fpath = "/assets/fluorine/js/react"


	def start_hook(where):
		if where in ("both", "app"):
			#if not hooks.web_include_js:
			#	hooks["web_include_js"] = []
			if not hooks.app_include_js:
				hooks["app_include_js"] = []

	def make_app_hook(where, name, path):
		if where in ("both", "app"):
			#hooks.web_include_js.append(os.path.join(path, name))
			hooks["app_include_js"].append(os.path.join(path, name))

	hooks = frappe.get_hooks(app_name="fluorine")

	fl = frappe.get_doc("Fluorine Reactivity")
	where = react.get(fl.fluorine_reactivity, None)

	start_hook(where)


	fluorine_publicjs_path = os.path.join(frappe.get_app_path("fluorine"), "public", "js", "react")

	for f in reversed(files_in_lib):
		dest = os.path.join(fluorine_publicjs_path, f.get("name"))
		#copy_file(f.get("path"), dest)
		copy_with_wrapper(f.get("path"), dest)
		hooks_js["client_hooks_js"].append(os.path.join(fpath, f.get("name")))
		make_app_hook(where, f.get("name"), fpath)

	for f in reversed(files_to_read):
		dest = os.path.join(fluorine_publicjs_path, f.get("name"))
		#copy_file(f.get("path"), dest)
		copy_with_wrapper(f.get("path"), dest)
		hooks_js["client_hooks_js"].append(os.path.join(fpath, f.get("name")))
		make_app_hook(where, f.get("name"), fpath)

	for f in reversed(main_files):
		dest = os.path.join(fluorine_publicjs_path, f.get("name"))
		#copy_file(f.get("path"), dest)
		copy_with_wrapper(f.get("path"), dest)
		hooks_js["client_hooks_js"].append(os.path.join(fpath, f.get("name")))
		make_app_hook(where, f.get("name"), fpath)

	fluor.save_batch_hook(hooks, frappe.get_app_path("fluorine") + "/hooks.py")
	return hooks_js


def copy_with_wrapper(src, dst):
	content = read(src)
	content = wrapper(content)
	write(dst, content)
	return content

def wrapper(content):
	w = """
	(function(){ %s })()
	"""

	return w % content


def copy_client_files(fluorine_temp_path):
	apps = frappe.get_installed_apps()#[::-1]
	for app in apps:
		pathname = frappe.get_app_path(app)
		startpath = os.path.join(pathname, "templates", "react")
		if pathname:
			for root, dirs, files in os.walk(startpath):
				relpath = os.path.relpath(root, startpath)
				#if not root.endswith("public") and not root.endswith("server") and not root.endswith("tests") and not root.endswith("private") and not root.endswith("temp"):
				#if not relpath.startswith(("public", "tests", "private", "temp", "server")):
				m = re.search(r"\b(public|tests|server|temp|private)\b",relpath)
				if not m:
					destpath = os.path.join(fluorine_temp_path, relpath)
					print "destpath {} relpath {} root {}".format(destpath, relpath, root)
					frappe.create_folder(destpath)
					for file in files:
						if file.endswith(".js"):
							copy_file(os.path.join(root, file), os.path.join(destpath, app + "_" + file))

def write(file_path, content):
	with open(file_path, "w") as f:
		f.write(content)


def read(file_path):
	with open(file_path, "r") as f:
		content = f.read()
	return content

def read_client_files(temp_folder):
	files_to_read = []
	files_in_lib = []
	main_files = []

	for root, dirs, files in os.walk(temp_folder):
		print "pathname: {}".format(root)
		for file in sorted(files, reverse=True):
			if file.endswith(".js"):
				#path = os.path.join(os.path.relpath(root, pathname), file)
				path = os.path.join(root, file)
				print "path read_client_files {}".format(path)
				obj = {"name":file, "path": path}
				#if root.endswith("lib"):
				if re.search(r"\blib\b", root):
					files_in_lib.append(obj)
				#elif root.endswith("client/compatibility"):
				elif re.search(r"\bclient/compatibility\b", root):
					obj["compatibility"] = True
					files_to_read.append(obj)
				elif re.search(r"main.*", file):
					main_files.append(obj)
				else:
					files_to_read.append(obj)

	return files_in_lib, files_to_read, main_files
