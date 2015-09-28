# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'

from fluorine.utils import meteor_desk_app
import frappe



no_sitemap = 1
no_cache = 1
base_template_path = "templates/pages/desk.html"


def get_context(context):
	from fluorine.utils.spacebars_template import get_app_pages
	from frappe.templates.pages.desk import get_context
	from fluorine.utils import is_making_production, check_dev_mode

	desk_result = get_context(context)

	context.developer_mode = check_dev_mode()

	if context.developer_mode:
		context = get_app_pages(context)

	production = not (context.developer_mode or is_making_production())

	make_meteor_properties(context, meteor_desk_app, production=production, site=frappe.local.site)

	desk_result.get("include_js").extend(context.meteor_package_js)
	desk_result.get("include_css").extend(context.meteor_package_css)

	return desk_result



def make_meteor_properties(context, whatfor, production=False, site=None):
	from fluorine.utils.meteor.utils import make_meteor_props
	from fluorine.utils import is_making_production


	if context.developer_mode or is_making_production():
		make_meteor_props(context, whatfor, production=production, site=site)
	#elif not context.developer_mode and not is_making_production():
	elif production:
		context.meteor_package_js = ["/assets/js/%s.min.js" % site]
		context.meteor_package_css = ["/assets/css/%s.css" % site]
		#make_includes(context)
		#print "meteor is in devmod %s" % context.meteor_package_js