__author__ = 'luissaguas'

from fluorine.utils import meteor_web_app


def get_files(api, whatfor, context):
	if whatfor == meteor_web_app:
		get_web_files(api)
	else:
		get_desk_files(api)


def get_web_files(api):

	for add_file in ("route.js",):
		prefix = "client"
		api.addFiles("%s/%s" % (prefix, add_file))

	for add_file in ("forgot.js",):
		prefix = "client/forgot_password"
		api.addFiles("%s/%s" % (prefix, add_file))

	for add_file in ("home.js", ):
		prefix = "client/home"
		api.addFiles("%s/%s" % (prefix, add_file))

	for add_file in ("login.js", ):
		prefix = "client/login"
		api.addFiles("%s/%s" % (prefix, add_file))

	for add_file in ("register.js", ):
		prefix = "client/register"
		api.addFiles("%s/%s" % (prefix, add_file))

	for add_file in ("update_password.js", ):
		prefix = "client/update_password"
		api.addFiles("%s/%s" % (prefix, add_file))

	for add_file in ("meteorlogin.js", "meteorregister.js", "route.js"):
		prefix = "server"
		api.addFiles("%s/%s" % (prefix, add_file))

def get_desk_files(api):
	pass
