from __future__ import unicode_literals
__author__ = 'luissaguas'

import os

import frappe

import fluorine as fluor
#import fluorine.utils
#import fluorine.utils.file as file
from fluorine.utils import file


def check_jquery(hook, hooks):
	found = False
	iweb = hooks.get(hook, None)
	for a in ("jquery.min.js", "jquery.js"):
		if iweb and any(a in s for s in iweb):
			found = True
			break
	if not found:
		iweb.insert(0, "/assets/frappe/js/lib/jquery/jquery.min.js")
		print "jquery not found, inserting frappe jquery!"


def check_includes(hook, hooks):
	iweb = hooks.get(hook, None)
	if iweb and not any("before_fluorine_helper" in s for s in iweb):
		update_includes(hook,iweb)
	elif iweb:
		to_remove = []
		for include in iweb:
			if "before_fluorine_helper" in include or "after_fluorine_helper" in include:
				to_remove.append(include)
		for i in to_remove:
			iweb.remove(i)
		update_includes(hook, iweb)


def update_includes(hook, iweb):
	#d = file.read_file("hook_help.txt")
	d = fluor.get_cached_value("hooks_helper")

	if not d:
		return

	fweb = d.get(hook, None)
	if fweb:
		iweb.insert(0, fweb[0])
		iweb.insert(1, fweb[1])
		if fweb[2:]:
			iweb.extend(fweb[2:])
		fluor.clear_frappe_caches()
	#print "hooks {} name {}".format(iweb, hook)

"""
original_get_hooks = frappe.get_hooks

def flourine_get_hooks(hook=None, default=None, app_name=None):
	#print "has hooks called"
	hooks = original_get_hooks(hook, default, app_name)
	if hook == "base_template":
		d = fluor.get_cached_value("hooks_helper")#read_file("hook_help.txt")
		if d and d.get(hook, None):
			hooks.extend(d.get(hook))
			fluor.clear_frappe_caches()
		return hooks

	if not app_name and not hook:
		check_includes('web_include_js', hooks)
		check_includes('app_include_js', hooks)
		d = fluor.get_cached_value("hooks_helper")
		if d and d.get("base_template", None):
			check_jquery('web_include_js', hooks)

	#if app_name == "fluorine":
		#d = file.read_file("hook_help.txt")
		#print "hooks in fluorine {} {}".format(hook, hooks)
		#check_includes('web_include_js', hooks)
		#check_includes('app_include_js', hooks)
		#d = fluor.get_cached_value("hooks_helper")
		#if d and d.get("base_template", None):
		#	check_jquery('web_include_js', hooks)


		#d = fluor.get_cached_value("hooks_helper")
		#if hook in ["app_include_js", "web_include_js", "base_template"]:
		#	if d and d.get(hook, None):
		#		hooks[hook] = d.get(hook)
		#		fluor.clear_frappe_caches()
		#elif not hook:
		#	hooks.update(d)
		#	fluor.clear_frappe_caches()

		#print "get_hooks hooks hooks {}".format(hooks)

	return hooks

frappe.get_hooks = flourine_get_hooks
"""

def start_reactivity():
	path = file.get_path_server_observe()
	#file.observe_dir(path)
	print fluor.utils.start_hash(path)
	path_reactivity = file.get_path_reactivity()
	js_path = file.get_path_assets_js()
	meteor_files = ("meteor.devel.js", "meteor.js")
	boot_file = os.path.join(path_reactivity, "server", "boot.js")
	print "in start_reactivity js_path {} boot_file {} curr path {}".format(js_path, boot_file, os.getcwd())
	for f in meteor_files:
		path_file = os.path.join(js_path, f)
		if os.path.exists(path_file) and os.path.exists(boot_file):
			file.run_reactivity(path_reactivity)
			break

print "frappe.__file__ {}".format(os.getcwd())

#for key, val in hooks.items():
#	print key, val


import sys

if any("--serve"==s for s in sys.argv):
	print "starting reactivity... {}".format(sys.argv)
	start_reactivity()