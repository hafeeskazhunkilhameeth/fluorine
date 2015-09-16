from __future__ import unicode_literals
__author__ = 'luissaguas'

import os, frappe

from fluorine.utils import meteor_desk_app, meteor_web_app
from fluorine.utils import file
from fluorine.utils.fjinja2.utils import c


global_ignores = ['*.pyc', '.DS_Store', '*.py', "*.tmp", "temp", ".gitignore"]

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

def remove_directory(path, ignore_errors=True):
	import shutil
	shutil.rmtree(path, ignore_errors=ignore_errors)

"""
def move_to_public(files, whatfor):
	hooks_js = {"client_hooks_js":[]}
	fpath = assets_public_path

	fluorine_publicjs_path = os.path.join(frappe.get_app_path("fluorine"), "public", "js", "react")

	for f in files:
		hooks_js["client_hooks_js"].extend(prepare_files_and_copy(f, fpath))

	return hooks_js
"""

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


def get_default_custom_pattern(custom_pattern=None):

	custom_pattern = custom_pattern or []
	custom_pattern = set(custom_pattern)
	custom_pattern.update(global_ignores)

	return custom_pattern

def get_custom_pattern(whatfor, custom_pattern=None):
	from shutil import ignore_patterns

	_whatfor = [meteor_desk_app, meteor_web_app]

	custom_pattern = custom_pattern or []
	ignored_names_top = ["public","tests","server","temp","private"]
	ignored_names_any = ["tests","server","temp"]

	_whatfor.remove(whatfor)

	custom_pattern = set(custom_pattern)
	pattern = ignore_patterns(*custom_pattern)

	ignored_names_top.extend(_whatfor)
	ignored_names_any.extend(_whatfor)

	return pattern, ignored_names_any, ignored_names_top


def read_client_xhtml_files(start_folder, appname, psf_in, meteor_ignore=None, custom_pattern=None):
	from fluorine.utils.file import check_files_folders_patterns

	files_to_read = []
	files_in_lib = []
	main_files = []
	main_lib_files = []

	pattern, ignored_names_any, ignored_names_top  = custom_pattern

	topfolder = True

	#list_meteor_files_folders_remove = get_attr_from_json(["remove", "files_folders"], meteor_ignore)
	list_meteor_files_folders_remove = psf_in.get_remove_files_folders()
	all_files_folder_remove = list_meteor_files_folders_remove.get("all")
	appname_files_folder_remove = list_meteor_files_folders_remove.get(appname)

	for root, dirs, files in os.walk(start_folder):

		ign_dirs = pattern(start_folder, dirs)

		if topfolder:
			ign_dirs.update(ignored_names_top)
			topfolder = False
		else:
			ign_dirs.update(ignored_names_any)

		for toexclude in ign_dirs:
			if toexclude in dirs:
				dirs.remove(toexclude)

		#get the relative path between start_folder (app/templates/react) and root folder
		#so dirs to exclude must have as base root dirs inside react folder. Ex. meteor_web/highlight as meteor_web is inside react folder.
		relpath = os.path.relpath(root, start_folder)
		for dir in dirs[::]:
			#f = os.path.join(relpath, dir)
			for source in (all_files_folder_remove, appname_files_folder_remove):
				if check_files_folders_patterns(dir, relpath, source):
					dirs.remove(dir)
					break

		islib = False

		if RE_LIB.search(root):
			islib = True

		files = [toinclude for toinclude in files if check_read_file_pattern(toinclude)]

		for f in files:
			if f in meteor_ignore or check_files_folders_patterns(f, relpath, all_files_folder_remove) or check_files_folders_patterns(f, relpath, appname_files_folder_remove):
				continue
			path = os.path.join(root, f)
			obj = {"name": f, "path": path}
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


def check_read_file_pattern(f):
	from fluorine.utils.reactivity import get_read_file_patterns
	import fnmatch

	patterns = get_read_file_patterns()
	for pattern in patterns.keys():
		if fnmatch.fnmatch(f, pattern):
			return True
	return False