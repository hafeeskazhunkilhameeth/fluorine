# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'


from jinja2 import FileSystemLoader, TemplateNotFound, ChoiceLoader
from jinja2.utils import internalcode
from jinja2.environment import Environment

try:
	from cStringIO import StringIO
except ImportError:
	from StringIO import StringIO

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
		from . import check_dev_mode
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

"""
def delimeter_match(m):
	print "m group in fjinja.py ", m.group(0)
	if m.group(0).startswith("{{%"):
		#print m.group(2)
		source = "{% endraw %}\n{{"+ m.group(2) +"}}{% raw %}\n"
	elif m.group(1) and m.group(1).startswith("end"):
		source = m.group(0) + "\n" + "{% raw %}\n"
	else:
		source = "\n" + "{% endraw %}\n" + m.group(0)

	return source

def jinjarepl(m):
	#print "my group 2 {}".format(m.group(2))
	source = re.sub(r"{%-?\s+(.*?)\s+-?%}|{{%(-?\s+.*?\s+-?)}}", delimeter_match, m.group(3))
	#print source
	source = '\n{% block '+ "{}".format(m.group(1)) + ' %}\n{% raw %}\n' + "<template name='{0}'{1}>".format(m.group(1), m.group(2)) + source + '\n{% endraw %}\n</template>\n{% endblock %}\n'
	#print "source in jinjareple {}".format(source)
	return source
"""

from Templates import Templates
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

				#self.meteor_map_path[template] = frappe._dict({"make_template": doc.make_template, "relpath": relpath_temp, "realpath": filepath, "file_temp_path": file_temp_path,
				#												"template": template, "appname": app, "doc":doc, "from_disk":False})
				"""
				try:
					encoded_contents = contents.encode(self.encoding)
					frappe.create_folder(os.path.dirname(file_temp_path))
					#print "writing files in order template {} file_temp_path {}".format(doc.template, file_temp_path)
					write(file_temp_path, encoded_contents)
				except Exception as e:
					print "exception when save error is {}".format(e)
				"""
				"""
				else:
					#anotate in map of path that we will use this template
					#if os.path.exists(file_temp_path[:-6] + ".pickle"):
					#with FluorDb(os.path.join(app_fluorine, "templates/react/temp", "fluorinedb")) as db:
					#with shelve.open(os.path.join(app_fluorine, "templates/react/temp", "fluorinedb")) as db:
					#with open(file_temp_path[:-6] + ".pickle", "rb") as f:
						#doc = pickle.load(f)

					key = str("fluorine:" + app + ":" + template)
					#doc = frappe.cache().get_value(key)
					#if not doc:
					doc = self.db[key]
					#else:
					#	print "from cache !!!!!"
						#self.meteor_map_path[template] = frappe._dict({"make_template": doc.make_template, "relpath": relpath_temp, "realpath": filepath, "file_temp_path": file_temp_path,
						#										"template": template, "appname": app, "doc":doc, "from_disk":True})
					self.get_jinja_dependencies(doc)
					self.meteor_map_path[template] = frappe._dict({"doc": doc, "from_disk": True})
				"""
				#self.docs.append(doc)

				#docs = self.process_references(content, force=True)
				#self.docs.extend(docs)
				#print "filepath in get_source 3 template {}".format(template)#os.path.relpath("apps", app_path)

				return contents, filename, uptodate
					#return contents, filename, uptodate
				#here file template exists and is uptodate
			except TemplateNotFound, e:
				print "Not Found {}".format(e)
				continue

		raise TemplateNotFound(template)


	def process_references(self, template, source):
		from jinja2 import meta
		from fluorine.utils.spacebars_template import fluorine_get_fenv
		from spacebars_template import addto_meteor_templates_list

		env = fluorine_get_fenv()
		for referenced_template_path in meta.find_referenced_templates(env.parse(source)):
			if referenced_template_path:
				if referenced_template_path not in frappe.local.templates_referenced:
					frappe.local.templates_referenced.append(referenced_template_path)
				refs = frappe.local.meteor_map_templates.get(template).get("refs")
				refs.append(referenced_template_path)
				addto_meteor_templates_list(referenced_template_path)


	def get_jinja_dependencies(self, doc):
		from spacebars_template import fluorine_get_fenv

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
		from spacebars_template import fluorine_get_fenv

		#app_fluorine = frappe.get_app_path("fluorine")
		templates_list = []

		for template, value in self.meteor_map_path.iteritems():
			if template not in self.templates_referenced:
				doc = value
				print "templates com make == True template {} relpath {}".format(doc.template, doc.relpath)
				t = fluorine_get_fenv().get_template(doc.relpath)
				templates_list.append(frappe._dict({"template":t, "tpath":template, "doc": value}))

		return templates_list

	def cache(self, key):
		doc = self.db.get(key)
		return doc

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

		#for key, value in self.meteor_map_path.iteritems():
		#	doc = value.doc
		#	flat_and_remove_docs(doc)
			#print "compilling .... tname 16 template {} doc content {}".format(doc.template, doc.content)


	"""
	def make_final_list_of_templates(self, doc):

		flat = self.flat_and_remove_docs(doc)

		if doc.extends_found:
			lastdoc = flat[0]
			#if self.templates_to_remove:
			#	from file import read
			#	content = read(doc.file_temp_path)
			#	doc._content = self.change_doc_content_remove(doc, content)
			if doc.templates_to_include: #and doc.template not in self.includes_path:
				#if doc.template not in self.includes_path:
				lastdoc._content = doc.change_doc_content_include(lastdoc)
				lastdoc._save_to_temp = False

		#put here to let extends and include same meteor template name from different sources
		for tname in doc.meteor_tag_templates_list.keys():

			if tname in frappe.local.meteor_Templates.keys():
				t = frappe.local.meteor_Templates.get(tname)
				doc.insere_template_to_remove_path(t.appname, tname)
			elif doc.extends_found:
				#if name of template not in any template yet then as we are extending the template will be removed by jinja so remove is folder
				#last = flat[0]
				#if tname in last.meteor_tag_templates_list:
				doc.insere_template_to_remove_path(doc.appname, tname)
				continue

			frappe.local.meteor_Templates[tname] = doc.meteor_tag_templates_list.get(tname)

	def flat_and_remove_docs(self, doc):

		flat = []

		for d in doc.docs:
			d._save = False
			doc.make_path_remove(d)
			#for tname in self.templates_to_remove:
			#	if tname in d.meteor_tag_templates_list:
					#self.insere_template_to_remove_path(d.appname, tname)
			d._content = doc.change_doc_content_remove(d)
			if d.docs:
				flat.extend(doc.flat_and_remove_docs(d))

			flat.append(d)

		return flat
	"""
"""
class MyFileSystemLoader(FileSystemLoader):
	def __init__(self, apps, searchpath, encoding='utf-8'):
		super(MyFileSystemLoader, self).__init__(searchpath, encoding=encoding)
		self.apps = apps
		#register the name of the jinja (xhtml files) templates founded
		self.jinja_xhtml_template_list = []
		self.templates_to_remove = []
		self.templates_to_include = []
		self.remove_next_close_template = False
		self.remove_next_close_block = False
		self.extends_found = False
		self.include_found = 0
		#register the name of templates tags founded
		self.meteor_tag_templates_list = []
		self.extends_path = []
		self.includs_path = []
		#register the name of jinja2 blocks tags founded
		self.jinja_tag_blocks_list = []
		#register the founded templates
		self.templates_found = []
		self.list_apps_remove = []
		self.list_meteor_tplt_remove = frappe._dict({})
		self.list_meteor_tplt_add = frappe._dict({})
		self.list_meteor_files_remove = frappe._dict({})
		self.list_meteor_files_add = frappe._dict({})
		self.curr_app = ""
		self.curr_template = ""
		self.c = c = lambda t:re.compile(t, re.S)
		#TODO add to cache? or add to initialization in develop mode
		self.ENDTEMPLATE = c(r"</\s*template\s*>")
		self.ENDBLOCK = c(r"{%\s+endblock\s+%}")
		self.STARTTEMPLATE = c(r"<\s*template\s+")
		self.METEOR_TEMPLATE_CALL = c(r"{{>(.+?)}}")
		self.METEOR_TEMPLATE_PERCENT_EXPR = c(r"{{%(.+?)}}")
		self.METEOR_TEMPLATE_BANG_EXPR = c(r"{{!(.+?)}}")
		self.BLOCKBEGIN = c(r"{%\s+block(.+?)%}")
		self.STARTTEMPLATE_SUB = c(r"<\s*template\s+name=['\"](.+?)['\"](.*?)(remove|include)?\s*>")
		self.EXTENDS = c(r"{%\s*extends(.+?) (.*?)%}")
		self.INCLUDE = c(r"{%\s*include(.+?) (.*?)%}")
		self.start_hook_lists()



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
		#A template with the same name was already found in a more recent installed app... ignore
		print "inload func name 5 {} includs_path {}".format(name, self.includs_path)
		if name in self.templates_found or name in self.includs_path:
			print "load func name 6 {} include_path {} templTES FOUND {}".format(name, self.includs_path, self.templates_found)
			for n in self.jinja_xhtml_template_list:
				if n.get("name") == name:
					self.jinja_xhtml_template_list.remove(n)
					break
			return
		template = super(MyFileSystemLoader, self).load(environment, name, globals=globals)
		save_to_file = True
		if name in self.extends_path or name in self.includs_path:
			print "load func name 3 {} extends_path {} include_path {} jinja template list {}".format(name, self.extends_path, self.includs_path, self.jinja_xhtml_template_list)
			#for n in self.jinja_xhtml_template_list:
			#	print "load func before save removing from list jinja templates 7 {} jinja {} extends {} found {} jinja template list {}".format(name, n.get("name"), self.extends_path, self.include_found, self.jinja_xhtml_template_list)
			#	if n.get("name") == name:
			#		self.jinja_xhtml_template_list.remove(n)
			#		break
			#save_to_file = False
			return template
		#else:
		self.jinja_xhtml_template_list.append({"name": name, "template": template, "save": save_to_file})
		return template

	def get_source(self, environment, template):
		#find the first template in revers order of installed apps and return

		for app in self.apps:
			#used in check_in_remove_list to know which template tag to remove
			self.curr_app = app
			#used in check_in_remove_list to know which template file to remove the tag template name
			self.curr_template = template
			if app in self.list_apps_remove:
				continue

			app_path = frappe.get_app_path(app)#get_package_path(app, "", "")
			filepath = os.path.join(app_path, template)
			relpath = os.path.relpath(filepath, os.path.normpath(os.path.join(os.path.join(os.getcwd(), ".."), "apps")))
			print "filepath in get_source {} template {} included path {}".format(relpath, template, self.includs_path)#os.path.relpath("apps", app_path)
			try:
				contents, filename, uptodate = super(MyFileSystemLoader, self).get_source(environment, relpath)
				#contents = re.sub("<template name=['\"](.+?)['\"](.*?)>(.*?)</template>", jinjarepl, contents, flags=re.S)

				contents = self.replace_for_templates(contents)
				self.templates_found.append(template)
				self.process_references(contents)
				if self.include_found and template not in self.extends_path:
					self.includs_path.append(template)
					self.include_found -= 1
					print "included found {}".format(template)

				return contents, filename, uptodate
			except TemplateNotFound, e:
				print "Not Found {}".format(e)
				continue

		raise TemplateNotFound(template)

	#Process dependencies in template.
	#Finds all the referenced templates from the AST. This will return an iterator over all
	#the hardcoded template extensions, inclusions and imports. If dynamic inheritance
	#or inclusion is used, None will be yielded.
	def process_references(self, source):
		from jinja2 import meta
		from fluorine.utils.spacebars_template import fluorine_get_fenv

		env = fluorine_get_fenv()
		for referenced_template_path in meta.find_referenced_templates(env.parse(source)):
			if referenced_template_path:
				#self.load(referenced_template_path)
				fluorine_get_fenv().addto_meteor_templates_list(referenced_template_path)

	def replace_for_templates(self, contents):
		new_content = []
		self.extends_found = False
		#self.include_found = False
		#print "start replace templ list is 5 {} content {}".format(self.meteor_tag_templates_list, contents)
		def close_template(line):
			if self.remove_next_close_template:
				#line = re.sub(r"</\s*template\s*>", '', line, 1, flags=re.S)
				line = self.ENDTEMPLATE.sub('', line, 1)
				self.remove_next_close_template = False
			else:
				#line = re.sub(r"</\s*template\s*>", '\n</template>\n{% endblock %}\n', line, flags=re.S)
				line = self.ENDTEMPLATE.sub('\n</template>\n{% endblock %}\n', line)

			return line

		def close_jinja_block(line):
			if self.remove_next_close_block:
				self.remove_next_close_block = False
				#line = re.sub(r"{%\s+endblock\s+%}", '', line, 1, flags=re.S)
				line = self.ENDBLOCK.sub('', line, 1)

			return line

		for line in contents.splitlines():
			#if re.search(r"</\s*template\s*>", line):
			if self.ENDTEMPLATE.search(line):
				line = close_template(line)

			#if re.search(r"{%\s+endblock\s+%}", line):
			if self.ENDBLOCK.search(line):
				line = close_jinja_block(line)

			if self.remove_next_close_template or self.remove_next_close_block:
				continue

			include = self.INCLUDE.search(line)
			if include:
				self.include_found += 1
				for n in self.jinja_xhtml_template_list:
					if n.get("name") == include.group(1).replace(" ","").replace("\'",""):
						#print "removing from list jinja templates 5 {} jinja {}".format(include.group(1), self.jinja_xhtml_template_list)
						self.includs_path.append(n.get("name"))
						self.jinja_xhtml_template_list.remove(n)
						self.include_found -= 1
						break
				#self.includs_path.append(include.group(1).replace(" ","").replace("\'",""))

			extends = self.EXTENDS.search(line)
			if extends:
				#import ast
				self.extends_found = True
				#print "extends group 2 {}".format(ast.literal_eval(extends.group(1).replace(" ","")))
				#self.extends_path.append(ast.literal_eval(extends.group(1).replace(" ","")))
				self.extends_path.append(extends.group(1).replace(" ","").replace("\'",""))

			#if re.search(r"<\s*template\s+", line):
			if self.STARTTEMPLATE.search(line):
				#line = re.sub(r"<\s*template\s+name=['\"](.+?)['\"](.*?)>", self.addBlockTemplate, line, flags=re.S)
				line = self.STARTTEMPLATE_SUB.sub(self.addBlockTemplate, line)

			#if re.search(r"{{>(.+?)}}", line):
			if self.METEOR_TEMPLATE_CALL.search(line):
				#line = re.sub(r"{{>(.+?)}}", self.wrappeMeteorExpression, line, flags=re.S)
				line = self.METEOR_TEMPLATE_CALL.sub(self.wrappeMeteorExpression, line)

			#expression of meteor must be preceded with % or !
			#if re.search(r"{{%(.+?)}}", line):
			if self.METEOR_TEMPLATE_PERCENT_EXPR.search(line):
				#line = re.sub(r"{{%(.+?)}}", self.wrappeMeteorExpression, line, flags=re.S)
				line = self.METEOR_TEMPLATE_PERCENT_EXPR.sub(self.wrappeMeteorExpression, line)

			#expression of meteor must be preceded with % or !
			#if re.search(r"{{!(.+?)}}", line):
			if self.METEOR_TEMPLATE_BANG_EXPR.search(line):
				#line = re.sub(r"{{!(.+?)}}", self.wrappeMeteorExpression, line, flags=re.S)
				line = self.METEOR_TEMPLATE_BANG_EXPR.sub(self.wrappeMeteorExpression, line)

			#if re.search(r"{%\s+block(.+?)%}", line):
			if self.BLOCKBEGIN.search(line):
				#line = re.sub(r"{%\s+block(.+?)%}", self.process_jinja_blocks, line, flags=re.S)
				line = self.BLOCKBEGIN.sub(self.process_jinja_blocks, line)

			new_content.append(line)


		if not self.extends_found:
			includes = self.templates_to_include[:]
			del self.templates_to_include[:]
			for name in includes:
				tcontents = '<template name="%s">\n' % name + '</template>\n'
				#self.templates_to_include.remove(name)
				lines = self.replace_for_templates(tcontents)
				print "includes templates 2 {} lines {}".format(includes, lines)
				new_content.append(lines)

		content = "\n".join(new_content)
		if content.replace("\n","").replace(" ","") == "":
			content = content.replace("\n","").replace(" ","")

		return content

	def process_jinja_blocks(self, m):
		if m.group(1) in self.jinja_tag_blocks_list or self.check_in_tplt_remove_list(m.group(1)):
			self.remove_next_close_block = True
			return ""

		self.meteor_tag_templates_list.append(m.group(1))
		return m.group(0)

	def remove_template(self, name, content):
		re.sub("<template name=['\"]"+ name + "['\"](.*?)>(.*?)</template>", "", content, flags=re.S)

	def wrappeMeteorExpression(self, m):
		source = self.openRaw() + m.group(0).replace("{{%", "{{").replace("{{!", "{{") + self.closeRaw()
		return source

	def wrappeRaw(self, m):
		source = self.openRaw() + m.group(0) + self.closeRaw()
		return source

	def closeRaw(self):
		source = "\n{% endraw %}\n"
		return source

	def openRaw(self):
		source = '\n{% raw %}\n'
		return source

	def wrappeBlock(self, name=None):

		def _wrappeBlock(m):
			source = self.openBlock(m, name) + m.group(0) + self.closeBlock()
			return source

		return _wrappeBlock

	def closeBlock(self):
		source = "\n{% endblock %}\n"
		return source

	def openBlock(self, m, name=None):
		source = '\n{% block ' + '{}'.format(name or m.group(1)) + " %}"#+ ' %}\n{% raw %}\n'
		return source

	def addBlockTemplate(self, m):
		print "in block template template 5 {} remove? {}".format(m.group(1), m.group(3)=="remove")
		if m.group(3) == "remove":
			self.remove_next_close_template = True
			self.templates_to_remove.append(m.group(1))
			return ""
		elif m.group(3) == "include":
			self.templates_to_include.append(m.group(1))

		if m.group(1) in self.meteor_tag_templates_list or self.check_in_tplt_remove_list(m.group(1)) or m.group(1) in self.templates_to_remove:
			self.remove_next_close_template = True
			return ""
		#TODO
		if not self.extends_found:
			self.meteor_tag_templates_list.append(m.group(1))
		source = self.openBlock(m, name="spacebars_" + m.group(1)) + "<template name='{0}'{1}>".format(m.group(1), m.group(2))
		return source

	def get_meteor_template_list(self):
		return self.jinja_xhtml_template_list

	def check_in_tplt_remove_list(self, name):
		app = self.curr_app
		template = self.curr_template

		for obj in self.list_meteor_tplt_remove.get(app, []):
			if obj.get("name") == name and obj.get("file") == template:
				return True

		return False
"""

"""
The following list has this structure for remove and add:
{
	"appname1": [object or string],
	"appname2": [object or string]
}
"""

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


	#def process_from_files():

		from file import process_ignores_from_modules

		#list_ignores = frappe._dict({
		#	"remove":{
		#		"apps":tuple(list_meteor_tplt_remove)
		#	},
		#	"add":{
		#		"apps": tuple(list_meteor_tplt_add)
		#	}
		#})

		#new_list = process_ignores_from_files(apps, "get_meteor_apps", list_ignores=list_ignores)
		#first to be processed is last installed
		#for n in new_list:
		#	for k,v in n.items():
		#		remove = v.get("remove",[])
		#		process_remove(k, remove)
		#		add = v.get("add") or []
		#		process_add(k, add)

	map_hooks = frappe._dict({"fluorine_files_templates": "get_meteor_files_templates", "fluorine_meteor_templates": "get_meteor_templates",
							"fluorine_files_folders": "get_meteor_files_folders"})

	from file import process_ignores_from_modules

	modules_list = process_ignores_from_modules(apps, map_hooks.get(hook_name))
	n = -1
	list_max = len(modules_list) - 1

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
		n += 1
		if n <= list_max:
			hooks = modules_list[n]
			for k,v in hooks.items():
				remove = v.get("remove") or []
				#print "hooks meteor templates 4 {} remove {}".format(hooks, remove)
				process_remove(k, remove)
				add = v.get("add") or []
				process_add(k, add)


	#process_from_files()


	#print "meteor templates lists add {} remove {}".format(list_meteor_tplt_add, list_meteor_tplt_remove)
	return list_meteor_tplt_add, list_meteor_tplt_remove

def process_hooks_apps(apps):
	from file import process_ignores_from_modules

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
		#if hooks:
		process(hooks)
		n += 1
		#n=0 is the last installed app. Same order as the for cycle
		if n <= list_max:
			process(modules_list[n])

	#list_ignores = frappe._dict({
	#	"remove":{
	#		"apps":tuple(list_apps_remove)
	#	},
	#	"add":{
	#		"apps": tuple(list_apps_add)
	#	}
	#})

	#new_list = process_ignores_from_files(apps, "get_meteor_apps", list_ignores=list_ignores)
	#first to be processed is last installed
	#for n in new_list:
	#	process(n)

	return list_apps_remove

"""
class MyFileSystemLoader(FileSystemLoader):
	def __init__(self, apps, searchpath, encoding='utf-8'):
		super(MyFileSystemLoader, self).__init__(searchpath, encoding='utf-8')
		self.apps = apps

	def get_source(self, environment, template):
		found = False
		contents = filename = uptodate = None

		for app in self.apps:
			#temp = template.split("/")
			#temp.insert(0, app + "/" + app)
			#temp = "/".join(temp)
			app_path = frappe.get_app_path(app)#get_package_path(app, "", "")
			filepath = os.path.join(app_path, template)
			relpath = os.path.relpath(filepath, os.path.normpath(os.path.join(os.path.join(os.getcwd(), ".."), "apps")))
			#print "filepath {} {}".format(relpath, temp)#os.path.relpath("apps", app_path)
			try:
				contents, filename, uptodate = super(MyFileSystemLoader, self).get_source(environment, relpath)
				contents = re.sub("<template name=['\"](.+?)['\"](.*?)>(.*?)</template>", jinjarepl, contents, flags=re.S)
				#print "new Contents get_source {}".format(contents)
				found = True
				break
			except TemplateNotFound, e:
				#print "Not Found {}".format(e)
				continue

		if not found:
			raise TemplateNotFound(template)
		else:
			return contents, filename, uptodate
"""