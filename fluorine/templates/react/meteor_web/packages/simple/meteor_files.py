__author__ = 'luissaguas'

from fluorine.utils import meteor_web_app, meteor_desk_app


def get_files(api, whatfor):
	describe = {
		"name": 'fluorine:simple',
		"version": '0.0.1',
		"summary": '',
		"git": '',
		"documentation": 'README.md'
	}

	#api.Npm({
	#  'faker': "3.0.1",
	#  'node-geocoder': "3.0.0"
	#})
	api.versionsFrom('1.1.0.3')
	api.use("templating", "client")
	api.describe(describe)
	if whatfor == meteor_web_app:
		get_web_files(api)
	else:
		get_desk_files(api)

def get_web_files(api):

	jinja_templates_tuple = ("aTemplate.xhtml", )
	for add_jinja_file in jinja_templates_tuple:
		api.addJinjaFiles("%s" % add_jinja_file)

	for add_file in jinja_templates_tuple:
		api.addFiles("%s" % add_file.replace(".xhtml", ".html"))

	for add_file in ("simple.js",):
		api.addFiles("%s" % add_file)

	#api.imply("less")
	#api.imply("amplify")
	#api.export("ReactionCore")
	#api.use("accounts-password")
	#api.addFiles("templates/teste3.xhtml", app="base_vat")
	#api.addFiles("/fixtures/custom_field.json", app="jasper_erpnext_report")
	#api.addFiles("/modules.txt")

def get_desk_files(api):
	pass



