from __future__ import unicode_literals
__author__ = 'luissaguas'

import os, frappe

from fluorine.utils import meteor_desk_app, meteor_web_app
from fluorine.utils import file
from fluorine.utils.fjinja2.utils import c


global_ignores = ['*.pyc', '.DS_Store', '*.py', "*.tmp", "temp", ".gitignore"]



RE_MFRAPPE = c(r"\bmeteor_frappe\b")
RE_LIB = c(r"\blib\b")
RE_MAIN = c(r"main.*")


def copy_file(src, dst):
	import shutil
	shutil.copyfile(src, dst)

def remove_directory(path, ignore_errors=True):
	import shutil
	shutil.rmtree(path, ignore_errors=ignore_errors)

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
