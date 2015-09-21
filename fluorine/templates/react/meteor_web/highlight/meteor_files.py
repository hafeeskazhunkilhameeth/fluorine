__author__ = 'luissaguas'

from fluorine.utils import meteor_web_app


def get_files(api, whatfor, context):
	if whatfor == meteor_web_app:
		get_web_files(api, context)
	else:
		get_desk_files(api, context)


def get_web_files(api, context):
	pass


def get_desk_files(api, context):
	pass


def get_meteor_template_files(api, whatfor, template_name, context):
	import sys
	module = sys.modules[__name__]

	if hasattr(module, template_name):
		getattr(module, template_name)(api, whatfor, context)


def highlight(api, whatfor, context):
	for add_file in ("highlight.js",):
		prefix = "highlight/client"
		api.addFiles("%s/%s" % (prefix, add_file))

	for add_file in ("highlight.css",):
		prefix = "highlight/client/css"
		api.addFiles("%s/%s" % (prefix, add_file))