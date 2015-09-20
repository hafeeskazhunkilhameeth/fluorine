__author__ = 'luissaguas'

from fluorine.utils import meteor_web_app


def get_files(api, whatfor, context):
	print "get_files in meteor called"
	if whatfor == meteor_web_app:
		get_web_files(api)
	else:
		get_desk_files(api)


def get_web_files(api):

	for add_file in ("menu.css",):
		prefix = "client"
		api.addFiles("%s/%s" % (prefix, add_file))

	for add_file in ("routeLayout.js",):
		prefix = "client/lib"
		api.addFiles("%s/%s" % (prefix, add_file))

	for add_file in ("custom.semantic.json", ):
		prefix = "client/lib/semantic-ui"
		api.addFiles("%s/%s" % (prefix, add_file))


def get_desk_files(api):
	pass
