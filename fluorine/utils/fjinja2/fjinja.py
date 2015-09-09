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


from collections import OrderedDict

class MyFileSystemLoader(FileSystemLoader):
	def __init__(self, apps, searchpath, dbpath=None, encoding='utf-8'):
		super(MyFileSystemLoader, self).__init__(searchpath, encoding=encoding)
		self.apps = apps
		#register the name of the jinja (xhtml files) templates founded
		self.list_apps_remove = []
		self.list_meteor_tplt_remove = frappe._dict({})
		self.list_meteor_tplt_add = frappe._dict({})
		self.list_meteor_files_remove = frappe._dict({})
		self.list_meteor_files_add = frappe._dict({})
		self.templates_referenced = []
		self.duplicated_templates_to_remove = frappe._dict({})

		if not frappe.local.meteor_map_path:
			#keep the loaded order
			self.meteor_map_path = frappe.local.meteor_map_path = OrderedDict()

		self.start_hook_lists()


	def start_hook_lists(self):

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
		template = super(MyFileSystemLoader, self).load(environment, name, globals=globals)
		return template


	def get_source(self, environment, template):
		basename = os.path.basename(template)
		dirname = os.path.dirname(template)
		app_fluorine = frappe.get_app_path("fluorine")
		temp_path = re.sub(r"(.*)templates(?:/react)?(.*)",r"\1templates/react/temp\2", dirname, re.S|re.I)

		for app in self.apps:

			file_temp_path = os.path.join(app_fluorine, temp_path, app, basename)
			if app in self.list_apps_remove:
				continue

			app_path = frappe.get_app_path(app)
			filepath = os.path.join(app_path, template)
			relpath = os.path.relpath(filepath, os.path.normpath(os.path.join(os.path.join(os.getcwd(), ".."), "apps")))
			try:
				contents, filename, uptodate = super(MyFileSystemLoader, self).get_source(environment, relpath)
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
			#check if referenced_template_path exists and don't reference it self
			if referenced_template_path and referenced_template_path != template:
				if referenced_template_path not in frappe.local.templates_referenced:
					frappe.local.templates_referenced.append(referenced_template_path)
				refs = frappe.local.meteor_map_templates.get(template).get("refs")
				refs.append(referenced_template_path)
				addto_meteor_templates_list(referenced_template_path)
			else:
				frappe.throw("The template reference %s does't exist or it reference it self %s" % (referenced_template_path, template))

	def get_source_old(self, environment, template):
		contents, filename, uptodate = super(MyFileSystemLoader, self).get_source(environment, template)

		return contents, filename, uptodate


	def remove_dynamic_templates(self, template, contents, doc):
		c = lambda t:re.compile(t, re.S|re.M)
		t = frappe.local.meteor_dynamic_templates_remove.get(template)
		if t:
			tname = t.name
			if tname in doc.meteor_tag_templates_list:
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

		templates_list = []

		for template, value in self.meteor_map_path.iteritems():
			if template not in self.templates_referenced:
				doc = value
				t = fluorine_get_fenv().get_template(doc.relpath)
				templates_list.append(frappe._dict({"template":t, "tpath":template, "doc": value}))

		return templates_list

	def compile_templates(self):
		#remove only files xhtml and is folders for xhtml that was replaced
		for d in self.duplicated_templates_to_remove.values():
			d.make_template_remove_regexp()
		#extends and includes first
		for key, value in self.meteor_map_path.iteritems():
			doc = value.doc
			if not doc.extends_found:
				doc.make_path_add(doc)
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

	for app in apps:
		hooks = frappe.get_hooks(hook=hook_name, default={}, app_name=app)
		for k,v in hooks.items():
			remove = v.get("remove") or []
			process_remove(k, remove)
			add = v.get("add") or []
			process_add(k, add)

	return list_meteor_tplt_add, list_meteor_tplt_remove

def process_hooks_apps_old(apps):
	from fluorine.utils.file import process_ignores_from_modules

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

	for app in apps:
		hooks = frappe.get_hooks(hook="fluorine_apps", default={}, app_name=app)
		process(hooks)
		n += 1
		if n <= list_max:
			process(modules_list[n])

	return list_apps_remove


def process_hooks_apps(apps):
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

	for app in apps:
		hooks = frappe.get_hooks(hook="fluorine_apps", default={}, app_name=app)
		process(hooks)

	return list_apps_remove
