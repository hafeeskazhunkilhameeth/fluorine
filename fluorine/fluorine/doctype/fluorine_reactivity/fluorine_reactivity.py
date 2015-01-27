# Copyright (c) 2013, Luis Fernandes and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, os
from frappe.model.document import Document
import fluorine as fluor
#import fluorine.utils.file as file
from fluorine.utils import file

#react = {"Reactive Web": "web", "Reactive App": "app", "Both": "both"}
from fluorine.utils import react

class FluorineReactivity(Document):
	def on_update(self, method=None):

		paths = ["/assets/fluorine/js/before_fluorine_helper.js", "/assets/fluorine/js/meteor.devel.js" if fluor.check_dev_mode() else "/assets/js/meteor.js",\
				"/assets/fluorine/js/after_fluorine_helper.js"]
		#print "self.fluorine_reactivity {}".format(self.fluorine_reactivity)
		if self.fluorine_state == "off":
			return

		objjs = reactivity(react.get(self.fluorine_reactivity, None), paths)

		if not objjs:
			return

		hooks = frappe.get_hooks(app_name="fluorine")
		hooks.pop("base_template", None)
		hooks.pop("home_page", None)
		#remove_react_from_hook(hooks, paths)

		#if hooks.app_include_js:
		#	hooks.app_include_js.extend(objjs.get("app_include_js"))
		#else:
		hooks.update(objjs)

		if self.fluorine_base_template and self.fluorine_base_template.lower() != "default" and self.fluorine_state == "on":
			#fluor.set_base_template(self.fluorine_base_template)
			#objjs["base_template"] = [self.fluorine_base_template]
			hooks["base_template"] = [self.fluorine_base_template]#frappe.get_app_path("fluorine") + "/templates" + "/fluorine_base.html"
			hooks["home_page"] = "fluorine_home"

		fluorine_publicjs_path = os.path.join(frappe.get_app_path("fluorine"), "public", "js", "react")
		frappe.create_folder(fluorine_publicjs_path)

		fluor.save_batch_hook(hooks, frappe.get_app_path("fluorine") + "/hooks.py")

		fluor.clear_frappe_caches()

		#elif self.fluorine_base_template.lower() == "default" or self.fluorine_state == "off":
		#	fluor.remove_base_template()
		#fluor.save_batch_hook_all("hooks_helper", objjs)
		#if not in dev mode compile to meteor.js
		if not fluor.check_dev_mode():
			#file.observer.stop()
			#jq = 1 if self.fluorine_base_template and self.fluorine_base_template.lower() != "default" else 0
			jq = 0
			file.make_meteor_file(jquery=jq, devmode=0)
			#file.observer.join()


def remove_react_from_hook(hooks, paths):
	appjs = hooks.app_include_js
	webjs = hooks.web_include_js
	for path in paths:
		if appjs:
			try:
				appjs.remove(path)
			except:
				pass
		if webjs:
			try:
				webjs.remove(path)
			except:
				pass



def reactivity(where, path):

	#fluor.delete_fluorine_session("hooks_helper")
	objjs = {}

	if where == "both":
		objjs["app_include_js"] = path
		#it is inserted in fluorine_home.html
		#objjs["web_include_js"] = path
	elif where == "app":
		objjs[where + "_include_js"] = path

	return objjs

