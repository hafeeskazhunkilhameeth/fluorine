# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'

import os, frappe

def get_app_context(context, path, app, app_path, pyname):
	ret = None

	if os.path.exists(path):
		# add website route
		controller_path = os.path.join(path, pyname)
		if os.path.exists(controller_path):
			controller = app + "." + os.path.relpath(controller_path,
				app_path).replace(os.path.sep, ".")[:-3]
			module = frappe.get_module(controller)
			if module:
				if hasattr(module, "get_context"):
					ret = module.get_context(context)
				if hasattr(module, "get_children"):
					context.get_children = module.get_children
				for prop in ("template", "condition_field"):
					if hasattr(module, prop):
						context[prop] = getattr(module, prop)
	return ret


def get_app_module(path, app, app_path, pyname):
	module = None

	if os.path.exists(path):
		controller_path = os.path.join(path, pyname)
		if os.path.exists(controller_path):
			controller = app + "." + os.path.relpath(controller_path,
				app_path).replace(os.path.sep, ".")[:-3]
			module = frappe.get_module(controller)

	return module