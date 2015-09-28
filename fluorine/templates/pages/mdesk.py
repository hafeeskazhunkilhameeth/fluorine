# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'


no_sitemap = 1
no_cache = 1
base_template_path = "templates/pages/desk.html"


def get_context(context):
	from fluorine.utils.spacebars_template import get_app_pages
	from frappe.templates.pages.desk import get_context

	desk_result = get_context(context)

	context = get_app_pages(context)

	desk_result.get("include_js").extend(context.meteor_package_js)
	desk_result.get("include_css").extend(context.meteor_package_css)

	return desk_result
