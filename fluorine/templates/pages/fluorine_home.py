__author__ = 'luissaguas'

import fluorine
from fluorine.utils.spacebars_template import fluorine_build_context
import frappe


def get_context(context):

	print "fluorine get_context called again!!!"
	frappe.local.fenv = None
	frappe.local.floader = None
	context.developer_mode = fluorine.check_dev_mode()
	context.jquery_include = True

	return fluorine_build_context(context)