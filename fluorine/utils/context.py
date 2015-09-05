__author__ = 'luissaguas'

import frappe,os, click
from fluorine.utils import whatfor_all, meteor_desk_app


class MeteorContext(object):
	def __init__(self, production=True):
		self.context = frappe._dict({meteor_desk_app:None})
		frappe.local.making_production = production

	def meteor_init(self, mongo_custom=False):
		from fluorine.utils.file import get_path_reactivity
		from fluorine.commands_helpers.meteor import meteor_run


		for app in whatfor_all:
			app_path = os.path.join(get_path_reactivity(), app)
			program_json_path = os.path.join(app_path, ".meteor", "local", "build", "programs", "web.browser", "program.json")
			if not os.path.exists(program_json_path) and os.path.exists(os.path.join(app_path, ".meteor")):
				try:
					meteor_run(app, app_path, mongo_custom=mongo_custom)
				except Exception as e:
					click.echo("You have to start meteor at hand before start meteor. Issue `meteor` in %s. Error: %s" % (app_path, e))
					return

	def make_context(self):
		from fluorine.utils import prepare_environment
		from fluorine.utils.reactivity import start_meteor
		from fluorine.utils.finals import make_public_folders
		#from fluorine.command import prepare_make_meteor_file

		make_public_folders()
		prepare_environment()
		start_meteor()
		frappe.local.request = frappe._dict()

		for w in whatfor_all:
			#prepare_compile_environment(w)
			ctx = prepare_context_meteor_file( w)
			if w == meteor_desk_app:
				self.context[meteor_desk_app] = ctx

	def make_meteor_properties(self):
		from fluorine.utils.meteor.utils import make_meteor_props
		from fluorine.utils.spacebars_template import make_includes

		context = self.context.get(meteor_desk_app)
		make_meteor_props(context, meteor_desk_app, production=True)
		make_includes(context)


def prepare_context_meteor_file(whatfor):
	from fluorine.templates.pages.fluorine_home import get_context as fluorine_get_context
	from fluorine.utils import meteor_desk_app, fluor_get_context as get_context


	if whatfor == meteor_desk_app:
		frappe.local.path = "desk"
		return get_context("desk")
	else:
		return fluorine_get_context(frappe._dict())
