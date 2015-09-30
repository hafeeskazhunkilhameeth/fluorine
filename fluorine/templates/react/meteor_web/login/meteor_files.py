__author__ = 'luissaguas'

from fluorine.utils import meteor_web_app


def get_files(api, whatfor, context):
	if whatfor == meteor_web_app:
		get_web_files(api, context)
	else:
		get_desk_files(api, context)


def get_web_files(api, context):

	for add_file in ("route.js",):
		prefix = "client"
		api.addFiles("%s/%s" % (prefix, add_file))

	for add_file in ("meteorlogin.js", "meteorregister.js", "route.js"):
		prefix = "server"
		api.addFiles("%s/%s" % (prefix, add_file))

def get_desk_files(api, context):
	pass


def get_meteor_template_files(api, whatfor, template_name, context):
	import sys
	module = sys.modules[__name__]

	if hasattr(module, template_name):
		getattr(module, template_name)(api, whatfor, context)


def forgot_password(api, whatfor, context):
	for add_file in ("forgot.js",):
		prefix = "client/forgot_password"
		api.addFiles("%s/%s" % (prefix, add_file))

def home(api, whatfor, context):
	for add_file in ("home.js", ):
		prefix = "client/home"
		api.addFiles("%s/%s" % (prefix, add_file))

def login(api, whatfor, contex):
	for add_file in ("login.js", ):
		prefix = "client/login"
		api.addFiles("%s/%s" % (prefix, add_file))

def register(api, whatfor, context):
	for add_file in ("register.js", ):
		prefix = "client/register"
		api.addFiles("%s/%s" % (prefix, add_file))

def update_password(api, whatfor, context):
	for add_file in ("update_password.js", ):
		prefix = "client/update_password"
		api.addFiles("%s/%s" % (prefix, add_file))
