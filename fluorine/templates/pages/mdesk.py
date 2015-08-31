# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'


no_sitemap = 1
no_cache = 1
base_template_path = "templates/pages/mdesk.html"


def get_context(context):
	from fluorine.utils.spacebars_template import get_app_pages
	return get_app_pages(context)
