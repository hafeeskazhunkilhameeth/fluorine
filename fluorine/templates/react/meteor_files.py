__author__ = 'luissaguas'

from fluorine.utils import meteor_web_app, meteor_desk_app


def get_files(api, whatfor):
	if whatfor == meteor_web_app:
		get_web_files(api)
	else:
		get_desk_files(api)

def get_web_files(api):

	app_path_prefix = meteor_web_app
	jinja_templates_tuple = ("Layout.xhtml", "login.xhtml", "extend_teste3.xhtml", "Header.xhtml", "highlight.xhtml", "notFound.xhtml")
	for add_jinja_file in jinja_templates_tuple:
		api.addJinjaFiles("%s/%s" % (app_path_prefix, add_jinja_file))

	for add_file in jinja_templates_tuple:
		api.addFiles("%s/%s" % (app_path_prefix, add_file.replace(".xhtml", ".html")))

	for add_file in ("clear_cache.js", "cookie_manager.js"):
		prefix = "%s/common/client" % app_path_prefix
		api.addFiles("%s/%s" % (prefix, add_file))

	for add_file in ("frappe_common.js", "get_cookie.js"):
		prefix = "%s/common/lib" % app_path_prefix
		api.addFiles("%s/%s" % (prefix, add_file))

	for add_file in ("frappe_call.js", "translation.js"):
		prefix = "%s/common/server" % app_path_prefix
		api.addFiles("%s/%s" % (prefix, add_file))

	api.addPackages("meteor_web/packages/simple")
	#api.imply("less")
	#api.imply("amplify")
	#api.export("ReactionCore")
	#api.use("accounts-password")
	#api.addFiles("templates/teste3.xhtml", app="base_vat")
	#api.addFiles("/fixtures/custom_field.json", app="jasper_erpnext_report")
	#api.addFiles("/modules.txt")

def get_desk_files(api):

	app_path_prefix = meteor_desk_app
	jinja_templates_tuple = ("Layout.xhtml",)
	for add_jinja_file in jinja_templates_tuple:
		api.addJinjaFiles("%s/%s" % (app_path_prefix, add_jinja_file))

	for add_file in jinja_templates_tuple:
		api.addFiles("%s/%s" % (app_path_prefix, add_file.replace(".xhtml", ".html")))

	for add_file in ("clear_cache.js", "get_user_from_code.js"):
		prefix = "%s/common/client" % app_path_prefix
		api.addFiles("%s/%s" % (prefix, add_file))

	for add_file in ("frappe_common.js",):
		prefix = "%s/common/lib" % app_path_prefix
		api.addFiles("%s/%s" % (prefix, add_file))

	for add_file in ("meteorlogin.js", ):
		prefix = "%s/common/server" % app_path_prefix
		api.addFiles("%s/%s" % (prefix, add_file))




