__author__ = 'luissaguas'

import frappe


def prepare_make_meteor_file(whatfor):
	from fluorine.templates.pages.fluorine_home import get_context as fluorine_get_context
	from fluorine.utils import meteor_desk_app, fluor_get_context as get_context

	#prepare_compile_environment(whatfor)
	if whatfor == meteor_desk_app:
		frappe.local.path = "desk"
		return get_context("desk")
	else:
		return fluorine_get_context(frappe._dict())
