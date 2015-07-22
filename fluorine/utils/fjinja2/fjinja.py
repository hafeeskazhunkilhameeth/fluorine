# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'


from jinja2 import FileSystemLoader, TemplateNotFound, ChoiceLoader
from jinja2.utils import internalcode
from jinja2.environment import Environment

import os, re, frappe

class MyChoiceLoader(ChoiceLoader):
	def __init__(self, loaders):
		super(MyChoiceLoader, self).__init__(loaders)
		self.curr_loader = None

	def get_source(self, environment, template):
		for loader in self.loaders:
			try:
				l = loader.get_source(environment, template)
				self.curr_loader = loader
				return l
			except TemplateNotFound:
				pass
		raise TemplateNotFound(template)


	def get_meteor_source(self, environment, template):

		for loader in self.loaders:
			try:
				l = loader.get_meteor_source(environment, template)
				self.curr_loader = loader
				return l
			except TemplateNotFound:
				pass
		raise TemplateNotFound(template)


	@internalcode
	def load(self, environment, name, globals=None):
		for loader in self.loaders:
			try:
				l = loader.load(environment, name, globals)
				self.curr_loader = loader
				return l
			except TemplateNotFound:
				pass
		raise TemplateNotFound(name)

	def get_curr_loader(self):
		return self.curr_loader

class MyEnvironment(Environment):

	def __init__(self, **vars):
		from .. import check_dev_mode
		super(MyEnvironment, self).__init__(**vars)
		self.devmode = check_dev_mode()

	def addto_meteor_templates_list(self, path):
		#return self.get_template(path)
		return self.loader.get_meteor_source(self, path)

	def get_meteor_template_list(self):
		floader = self.loader.get_curr_loader()
		if floader:
			return floader.get_meteor_template_list()
		return None

from fluorine.utils.Templates import Templates
from collections import OrderedDict

class MyFileSystemLoader(FileSystemLoader):
	def __init__(self, apps, searchpath, dbpath=None, encoding='utf-8'):
		super(MyFileSystemLoader, self).__init__(searchpath, encoding=encoding)
		self.apps = apps
		#self.db = shelve.open(dbpath, protocol=-1)
		#register the name of the jinja (xhtml files) templates founded
		self.list_apps_remove = []
		self.list_meteor_tplt_remove = frappe._dict({})
		self.list_meteor_tplt_add = frappe._dict({})
		self.list_meteor_files_remove = frappe._dict({})
		self.list_meteor_files_add = frappe._dict({})
		#self.docs = []
		self.templates_referenced = []
		self.duplicated_templates_to_remove = frappe._dict({})

		if not frappe.local.meteor_map_path:
			#self.meteor_map_path = frappe._dict({})
			#self.meteor_map_path = frappe.local.meteor_map_path = frappe._dict({})
			#keep the loaded order
			self.meteor_map_path = frappe.local.meteor_map_path = OrderedDict()#frappe._dict(OrderedDict())

		self.start_hook_lists()
		self.templates = Templates(self.list_meteor_tplt_remove, apps=self.apps)


	def start_hook_lists(self):

		#self.list_apps_remove.extend(process_hooks_apps(self.apps))
		#list_meteor_tplt_add, list_meteor_tplt_remove = process_hooks_meteor_templates(self.apps, "fluorine_meteor_templates")
		list_ignores = frappe.local.meteor_ignores
		remove = list_ignores.get("remove", {})
		add = list_ignores.get("add", {})

		self.list_apps_remove.extend(remove.get("apps", []))
		list_meteor_tplt_add = add.get("meteor_templates", frappe._dict({}))
		list_meteor_tplt_remove = remove.get("meteor_templates", frappe._dict({}))
		self.list_meteor_tplt_add.update(list_meteor_tplt_add)
		self.list_meteor_tplt_remove.update(list_meteor_tplt_remove)

	@internalcode
	def load(self, environment, name, globals=None):
		#if not self.templates.check_found_include(name):
		#	return

		template = super(MyFileSystemLoader, self).load(environment, name, globals=globals)
		#self.templates.process_include_excludes(name, template)
		return template


	def get_source(self, environment, template):
		#from file import write

		print "finding template {}".format(template)
		#if frappe.local.meteor_map_templates[template]:
			#print "template already processed 4 {} doc {}".format(template, self.meteor_map_path.get(template).doc)
		#	return False

		#app_fluorine = frappe.get_app_path("fluorine")
		#temp_path = re.sub(r"(.*)templates(?:/react)?(.*)",r"\1templates/react/temp\2", template, re.S)
		#file_temp_path = os.path.join(app_fluorine, temp_path)
		#relpath_temp = os.path.relpath(file_temp_path, os.path.normpath(os.path.join(os.path.join(os.getcwd(), ".."), "apps")))

		basename = os.path.basename(template)
		dirname = os.path.dirname(template)
		app_fluorine = frappe.get_app_path("fluorine")
		temp_path = re.sub(r"(.*)templates(?:/react)?(.*)",r"\1templates/react/temp\2", dirname, re.S|re.I)

		for app in self.apps:

			file_temp_path = os.path.join(app_fluorine, temp_path, app, basename)
			relpath_temp = os.path.relpath(file_temp_path, os.path.normpath(os.path.join(os.path.join(os.getcwd(), ".."), "apps")))
			#used in check_in_remove_list to know which template tag to remove
			#self.templates.setCurrApp(app)
			#used in check_in_remove_list to know which template file to remove the tag template name
			#self.templates.setCurrTemplate(template)
			if app in self.list_apps_remove:
				continue

			app_path = frappe.get_app_path(app)#get_package_path(app, "", "")
			filepath = os.path.join(app_path, template)
			relpath = os.path.relpath(filepath, os.path.normpath(os.path.join(os.path.join(os.getcwd(), ".."), "apps")))
			#print "filepath in get_source 2 {} template {}".format(relpath, template)#os.path.relpath("apps", app_path)
			try:
				#TODO must check timestamp
				#temp_path = template.replace("templates/react","templates/react/temp",1)

				#if not os.path.exists(file_temp_path) or not self.check_uptodate(file_temp_path, filepath):# or force==True:

				#contents, filename, uptodate = super(MyFileSystemLoader, self).get_source(environment, relpath)
				#contents, filename, uptodate = self.get_source(environment, relpath)
				contents, filename, uptodate = super(MyFileSystemLoader, self).get_source(environment, relpath)
				print "find template 6 {} appname {}".format(template, app)
				#print "content from get source template {} content {}".format(template, contents)
				#doc, contents = self.templates.make_template(contents, appname=app, template=template, relpath_temp=relpath_temp, realpath=filepath,
															#relpath=relpath, file_temp_path=file_temp_path, encoding=self.encoding)

				#self.meteor_map_path[template] = frappe._dict({"doc": doc, "from_disk": False})
				#self.meteor_map_path[template] = frappe._dict({"template":template, "relpath": relpath, "realpath": filepath, "file_temp_path": file_temp_path})
				frappe.local.meteor_map_templates[template] = frappe._dict({"appname": app, "template":template, "relpath": relpath, "realpath": filepath, "file_temp_path": file_temp_path, "refs":[]})
				self.process_references(template, contents)

				return contents, filename, uptodate
				#here file template exists and is uptodate
			except TemplateNotFound, e:
				print "Not Found {}".format(e)
				continue

		raise TemplateNotFound(template)


	def process_references(self, template, source):
		from jinja2 import meta
		from fluorine.utils.spacebars_template import fluorine_get_fenv, addto_meteor_templates_list

		env = fluorine_get_fenv()
		for referenced_template_path in meta.find_referenced_templates(env.parse(source)):
			if referenced_template_path:
				if referenced_template_path not in frappe.local.templates_referenced:
					frappe.local.templates_referenced.append(referenced_template_path)
				refs = frappe.local.meteor_map_templates.get(template).get("refs")
				refs.append(referenced_template_path)
				addto_meteor_templates_list(referenced_template_path)


	def get_jinja_dependencies(self, doc):
		from fluorine.utils.spacebars_template import fluorine_get_fenv

		docs = []
		#if not doc.extends_path:
		#	return
		#extends_path = doc.extends_path[0]
		for extends_path in doc.extends_path:
			#print "dependencies template 2 excludes {} has dependecies {} docs {}".format(doc.template, extends_path, doc.docs[0].relpath_temp)
			if extends_path not in self.meteor_map_path.keys():
				edoc = fluorine_get_fenv().addto_meteor_templates_list(extends_path)
				edoc.parent = doc
				edoc.origin = "extend"
				docs.append(edoc)

		for include_path in doc.includes_path:
			#print "dependencies template 2 includes {} has dependecies {} docs {}".format(doc.template, include_path, doc.docs[0].relpath_temp)
			if include_path not in self.meteor_map_path.keys():
				idoc = fluorine_get_fenv().addto_meteor_templates_list(include_path)
				idoc.parent = doc
				idoc.origin = "include"
				docs.append(idoc)

		doc.docs.extend(docs)

	def get_source_old(self, environment, template):
		contents, filename, uptodate = super(MyFileSystemLoader, self).get_source(environment, template)

		return contents, filename, uptodate


	def remove_dynamic_templates(self, template, contents, doc):
		c = lambda t:re.compile(t, re.S|re.M)
		t = frappe.local.meteor_dynamic_templates_remove.get(template)
		print "templates in frappe.local.meteor_dynamic_templates_remove template 2 {} obj {}".format(template, t)
		if t:
			tname = t.name
			if tname in doc.meteor_tag_templates_list:
				print "found a template in remove dynamic templates 2 {}".format(tname)
				if t.type == "template":
					tname = "spacebars_" + tname
				block_txt = r"{%\s+block\s+" + tname + r"\s+%}(.*?){%\s*endblock\s*%}"
				block = c(block_txt)
				contents = block.sub("", contents)

		return contents


	def check_uptodate(self, file_temp_path, filepath):
		try:
			return os.path.getmtime(file_temp_path) >= os.path.getmtime(filepath)
		except OSError:
			return False

	def get_meteor_template_list(self):
		from fluorine.utils.spacebars_template import fluorine_get_fenv

		#app_fluorine = frappe.get_app_path("fluorine")
		templates_list = []

		for template, value in self.meteor_map_path.iteritems():
			if template not in self.templates_referenced:
				doc = value
				print "templates com make == True template {} relpath {}".format(doc.template, doc.relpath)
				t = fluorine_get_fenv().get_template(doc.relpath)
				templates_list.append(frappe._dict({"template":t, "tpath":template, "doc": value}))

		return templates_list

	def compile_templates(self):

		#remove only files xhtml and is folders for xhtml that was replaced
		for d in self.duplicated_templates_to_remove.values():
			d.make_template_remove_regexp()
		#for doc in self.docs:#reversed(self.docs):
		#extends and includes first
		for key, value in self.meteor_map_path.iteritems():
			doc = value.doc
			#doc.make_template_remove_regexp()
			if not doc.extends_found:
				doc.make_path_add(doc)
			print "order of templates to make final 2 {}".format(doc.template)
			doc.make_final_list_of_templates()

def process_hooks_meteor_templates(apps, hook_name):
	list_meteor_tplt_add = frappe._dict({})
	list_meteor_tplt_remove = frappe._dict({})


	def check_in_remove_list(k, v):
		lrm = list_meteor_tplt_remove.get(k)
		if not lrm:
			return False

		for l in lrm:
			if l == v:
				return True

		return False

	def check_in_add_list(k, v):
		ladd = list_meteor_tplt_add.get(k)
		if not ladd:
			return False

		for l in ladd:
			if l == v:
				return True

		return False

	def process_remove(k, remove):
		lrm = list_meteor_tplt_remove.get(k)
		for r in remove:
			if not check_in_add_list(k, r):
				if not lrm:
					list_meteor_tplt_remove[k] = remove
					process_xhtml_files(k, remove)
					break
				elif not check_in_remove_list(k, r):
					lrm.append(r)
					process_xhtml_files(k, [r])

	def process_add(k, add):
		ladd = list_meteor_tplt_add.get(k)
		for a in add:
			if not check_in_remove_list(k, a):
				if not ladd:
					list_meteor_tplt_add[k] = add
					break
				elif not check_in_add_list(k, a):
					ladd.append(a)

	#remove the html files generated from this xhtml files
	def process_xhtml_files(k, remove):
		if hook_name == "fluorine_meteor_templates":
			return
		lrm = list_meteor_tplt_remove.get(k)
		for r in remove:
			ext = r.rsplit(".", 1)
			if len(ext) > 1 and ext[1] == "xhtml":
				html = ext[0] + ".html"
				lrm.append(html)

	#map_hooks = frappe._dict({"fluorine_files_templates": "get_meteor_files_templates", "fluorine_meteor_templates": "get_meteor_templates",
	#						"fluorine_files_folders": "get_meteor_files_folders"})

	from fluorine.utils.file import process_ignores_from_modules

	#modules_list = process_ignores_from_modules(apps, map_hooks.get(hook_name))
	#n = -1
	#list_max = len(modules_list) - 1

	for app in apps:
		hooks = frappe.get_hooks(hook=hook_name, default={}, app_name=app)
		#if hooks:
		for k,v in hooks.items():
			remove = v.get("remove") or []
			#print "hooks meteor templates 4 {} remove {}".format(hooks, remove)
			process_remove(k, remove)
			add = v.get("add") or []
			process_add(k, add)

		#n=0 is the last installed app. Same order as the for cycle
		"""
		n += 1
		if n <= list_max:
			hooks = modules_list[n]
			for k,v in hooks.items():
				remove = v.get("remove") or []
				#print "hooks meteor templates 4 {} remove {}".format(hooks, remove)
				process_remove(k, remove)
				add = v.get("add") or []
				process_add(k, add)
		"""

	#print "meteor templates lists add {} remove {}".format(list_meteor_tplt_add, list_meteor_tplt_remove)
	return list_meteor_tplt_add, list_meteor_tplt_remove

def process_hooks_apps_old(apps):
	from fluorine.utils.file import process_ignores_from_modules
	#from fhooks import FrappeContext

	list_apps_add = []
	list_apps_remove = []

	def process(hooks):

		for k,v in hooks.items():
			if v.get("remove",[0])[0]:
				if k not in list_apps_add:
					list_apps_remove.append(k)
			elif v.get("add",[0])[0]:
				if k not in list_apps_remove:
					list_apps_add.append(k)

	#get from files
	modules_list = process_ignores_from_modules(apps, "get_meteor_apps")
	n = - 1
	list_max = len(modules_list) - 1

	#with FrappeContext("site1.local", "Administrator") as f:
	for app in apps:
		hooks = frappe.get_hooks(hook="fluorine_apps", default={}, app_name=app)
		process(hooks)
		n += 1
		#n=0 is the last installed app. Same order as the for cycle
		if n <= list_max:
			process(modules_list[n])

	return list_apps_remove


def process_hooks_apps(apps):
	#from file import process_ignores_from_modules
	#from fhooks import FrappeContext

	list_apps_add = []
	list_apps_remove = []

	def process(hooks):

		for k,v in hooks.items():
			if v.get("remove",[0])[0]:
				if k not in list_apps_add:
					list_apps_remove.append(k)
			elif v.get("add",[0])[0]:
				if k not in list_apps_remove:
					list_apps_add.append(k)

	#with FrappeContext("site1.local", "Administrator") as f:
	for app in apps:
		hooks = frappe.get_hooks(hook="fluorine_apps", default={}, app_name=app)
		process(hooks)

	return list_apps_remove
