# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'


no_sitemap = 1
base_template_path = "templates/fluorine_base.html"
no_cache = 1

def get_context(context):
	from fluorine.utils.spacebars_template import get_web_pages

	return get_web_pages(context)
