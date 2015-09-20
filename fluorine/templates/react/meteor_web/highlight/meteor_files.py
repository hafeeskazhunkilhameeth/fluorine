__author__ = 'luissaguas'

from fluorine.utils import meteor_web_app


def get_files(api, whatfor, context):
	if whatfor == meteor_web_app:
		get_web_files(api)
	else:
		get_desk_files(api)


def get_web_files(api):

	for add_file in ("highlight.js",):
		prefix = "highlight/client"
		api.addFiles("%s/%s" % (prefix, add_file))

	for add_file in ("highlight.css",):
		prefix = "highlight/client/css"
		api.addFiles("%s/%s" % (prefix, add_file))


def get_desk_files(api):
	pass
