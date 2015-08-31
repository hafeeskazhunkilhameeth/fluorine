from __future__ import unicode_literals
__author__ = 'luissaguas'

import frappe, os

from fluorine.utils import file
from fluorine.utils import assets_public_path
from fluorine.utils.fjinja2.utils import c


"""
client file loader
for each module read files with extension js
special atention to files in client/compatibility
ignore files in tests, in public in private and server
files in lib first and inside lib alphabetic order
other folders deepest first
files with main.* (start with main) are load last
"""


RE_MFRAPPE = c(r"\bmeteor_frappe\b")
RE_LIB = c(r"\blib\b")
RE_MAIN = c(r"main.*")


def copy_file(src, dst):
	import shutil
	shutil.copyfile(src, dst)

def remove_directory(path):
	import shutil
	shutil.rmtree(path)


def move_to_public(files, whatfor):
	hooks_js = {"client_hooks_js":[]}
	fpath = assets_public_path

	fluorine_publicjs_path = os.path.join(frappe.get_app_path("fluorine"), "public", "js", "react")

	for f in files:
		hooks_js["client_hooks_js"].extend(prepare_files_and_copy(f, fpath))

	return hooks_js


def prepare_files_and_copy(files, fpath):
	hooks = []
	for f in reversed(files):
		hooks.append(os.path.join(fpath, f.get("relpath"), f.get("name")))

	return hooks


def copy_with_wrapper(src, dst, use_wrapper=True):
	content = file.read(src)
	if use_wrapper:
		content = wrapper(content)
	file.write(dst, content)
	return content

def wrapper(content):
	w = """
	(function(){ %s })()
	"""

	return w % content

def get_dirs_from_list(appname, list_files):
	dirs = []
	for l in list_files.get(appname, []):
		if os.path.isdir(l):
			dirname = l.split("/")
			length = len(dirname) - 1
			dirs.append(dirname[length])

	return dirs

def get_custom_pattern(whatfor, custom_pattern=None):
	from shutil import ignore_patterns

	_whatfor = ["meteor_app", "meteor_web", "meteor_frappe"]
	exclude = [""]
	custom_pattern = custom_pattern or []
	ignored_names_top = ["public","tests","server","temp","private"]
	ignored_names_any = ["tests","server","temp"]
	if isinstance(whatfor, basestring):
		whatfor = [whatfor]

	is_for_meteor_frappe = "meteor_frappe" in whatfor
	if is_for_meteor_frappe:
		ignored_names_top.extend(["meteor_app", "meteor_web"])

	try:
		for w in whatfor:
			_whatfor.remove(w)
		exclude = _whatfor
	except:
		pass

	custom_pattern = set(custom_pattern)
	pattern = ignore_patterns(*custom_pattern)

	ignored_names_top.extend(exclude)
	ignored_names_any.extend(exclude)

	return pattern, ignored_names_any, ignored_names_top


def read_client_xhtml_files(start_folder, whatfor, appname, meteor_ignore=None, custom_pattern=None):
	import fnmatch
	from file import check_remove_files_folders

	files_to_read = []
	files_in_lib = []
	main_files = []
	main_lib_files = []

	is_for_meteor_frappe = "meteor_frappe" in whatfor
	pattern, ignored_names_any, ignored_names_top  = custom_pattern

	topfolder = True

	list_meteor_files_folders_remove = frappe.local.meteor_ignores.get("remove").get("files_folders")
	all_files_folder_remove = list_meteor_files_folders_remove.get("all")
	appname_files_folder_remove = list_meteor_files_folders_remove.get(appname)

	for root, dirs, files in os.walk(start_folder):

		ign_dirs = pattern(start_folder, dirs)
		try:
			if topfolder:
				ign_dirs.update(ignored_names_top)
				[dirs.remove(toexclude) for toexclude in ign_dirs if toexclude in dirs]
				topfolder = False
			else:
				ign_dirs.update(ignored_names_any)
				[dirs.remove(toexclude) for toexclude in ign_dirs if toexclude in dirs]
		except:
			print "remove exclude 3 {} no exclude in dirs ".format(ignored_names_top)
			pass

		#only read files within meteor_frappe folder
		if is_for_meteor_frappe:
			if not RE_MFRAPPE.search(root):
				continue

		islib = False
		relpath = os.path.relpath(root, start_folder)

		if RE_LIB.search(root):
			islib = True

		deeper = len(root.split("/"))

		files = [toinclude for toinclude in files if fnmatch.fnmatch(toinclude, "*xhtml")]

		for f in files:
			if check_remove_files_folders(f,  all_files_folder_remove) or check_remove_files_folders(f, appname_files_folder_remove):
				continue
			ext = f.rsplit(".", 1)
			path = os.path.join(root, f)
			obj = {"name":f, "path": path, "relpath": relpath, "filePath": root, "fileName": ext[0], "deep": deeper}
			if RE_MAIN.search(str(f)):
				if islib:
					main_lib_files.append(obj)
					continue
				main_files.append(obj)
			elif islib:
				files_in_lib.append(obj)
			else:
				files_to_read.append(obj)

	return (files_in_lib, files_to_read, main_lib_files, main_files)
