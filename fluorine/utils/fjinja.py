__author__ = 'luissaguas'



#from fluorine.utils.packages_path import get_package_path
from jinja2 import FileSystemLoader, TemplateNotFound, ChoiceLoader
from jinja2.utils import internalcode
from jinja2.environment import Environment

import re, os, frappe


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
		super(MyEnvironment, self).__init__(**vars)
	"""
	def __init__(self,
			block_start_string=BLOCK_START_STRING,
			block_end_string=BLOCK_END_STRING,
			variable_start_string=VARIABLE_START_STRING,
			variable_end_string=VARIABLE_END_STRING,
			comment_start_string=COMMENT_START_STRING,
			comment_end_string=COMMENT_END_STRING,
			line_statement_prefix=LINE_STATEMENT_PREFIX,
			line_comment_prefix=LINE_COMMENT_PREFIX,
			trim_blocks=TRIM_BLOCKS,
			lstrip_blocks=LSTRIP_BLOCKS,
			newline_sequence=NEWLINE_SEQUENCE,
			keep_trailing_newline=KEEP_TRAILING_NEWLINE,
			extensions=(),
			optimized=True,
			undefined=Undefined,
			finalize=None,
			autoescape=False,
			loader=None,
			cache_size=50,
			auto_reload=True,
			bytecode_cache=None):

		super(MyEnvironment, self).__init__(
			block_start_string=block_start_string,
			block_end_string=block_end_string,
			variable_start_string=variable_start_string,
			variable_end_string=variable_end_string,
			comment_start_string=comment_start_string,
			comment_end_string=comment_end_string,
			line_statement_prefix=line_statement_prefix,
			line_comment_prefix=line_comment_prefix,
			trim_blocks=trim_blocks,
			lstrip_blocks=lstrip_blocks,
			newline_sequence=newline_sequence,
			keep_trailing_newline=keep_trailing_newline,
			extensions=extensions,
			optimized=optimized,
			undefined=undefined,
			finalize=finalize,
			autoescape=autoescape,
			loader=loader,
			cache_size=cache_size,
			auto_reload=auto_reload,
			bytecode_cache=bytecode_cache
		)
	"""
	def addto_meteor_templates_list(self, path):
		return self.get_template(path)

	def get_meteor_template_list(self):
		floader = self.loader.get_curr_loader()
		return floader.get_meteor_template_list()

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

class MyFileSystemLoader(FileSystemLoader):
	def __init__(self, apps, searchpath, encoding='utf-8'):
		super(MyFileSystemLoader, self).__init__(searchpath, encoding=encoding)
		self.apps = apps
		#register the name of the jinja (xhtml files) templates founded
		self.jinja_xhtml_template_list = []
		self.remove_next_close = False
		#register the name of templates tags founded
		self.meteor_tag_templates_list = []
		#register the founded templates
		self.templates_found = []
		self.list_apps_remove = []
		self.list_meteor_tplt_remove = frappe._dict({})
		self.list_meteor_tplt_add = frappe._dict({})
		self.curr_app = ""
		self.curr_template = ""
		self.start_hook_lists()

	#TODO make cache
	def start_hook_lists(self):
		self.list_apps_remove.extend(process_hooks_apps(self.apps))
		list_meteor_tplt_add, list_meteor_tplt_remove = process_hooks_meteor_templates(self.apps)
		self.list_meteor_tplt_add.update(list_meteor_tplt_add)
		self.list_meteor_tplt_remove.update(list_meteor_tplt_remove)


	@internalcode
	def load(self, environment, name, globals=None):
		#A template with the same name was already found in a more recent installed app... ignore
		if name in self.templates_found:
			return
		template = super(MyFileSystemLoader, self).load(environment, name, globals=globals)
		self.jinja_xhtml_template_list.append({"name": name, "template": template})
		return template

	def get_source(self, environment, template):
		#find the first template in revers order of installed apps and return

		for app in self.apps:
			if app in self.list_apps_remove:
				continue
			app_path = frappe.get_app_path(app)#get_package_path(app, "", "")
			filepath = os.path.join(app_path, template)
			relpath = os.path.relpath(filepath, os.path.normpath(os.path.join(os.path.join(os.getcwd(), ".."), "apps")))
			#print "filepath in get_source {} template {}".format(relpath, template)#os.path.relpath("apps", app_path)
			try:
				contents, filename, uptodate = super(MyFileSystemLoader, self).get_source(environment, relpath)
				#contents = re.sub("<template name=['\"](.+?)['\"](.*?)>(.*?)</template>", jinjarepl, contents, flags=re.S)

				#used in check_in_remove_list to know which template tag to remove
				self.curr_app = app
				#used in check_in_remove_list to know which template file to remove the tag template name
				self.curr_template = template
				contents = self.replace_for_templates(contents)
				self.templates_found.append(template)
				self.process_references(contents)
				return contents, filename, uptodate
			except TemplateNotFound, e:
				#print "Not Found {}".format(e)
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
		#print "start replace templ list is 5 {} content {}".format(self.meteor_tag_templates_list, contents)
		def close_template(line):
			if self.remove_next_close:
				line = re.sub(r"</\s*template\s*>", '', line, 1, flags=re.S)
				self.remove_next_close = False
			else:
				line = re.sub(r"</\s*template\s*>", '\n</template>\n{% endblock %}\n', line, flags=re.S)

			return line

		for line in contents.splitlines():
			if re.search(r"</\s*template\s*>", line):
				line = close_template(line)

			if self.remove_next_close:
				continue

			if re.search(r"<\s*template\s+", line):
				line = re.sub(r"<\s*template\s+name=['\"](.+?)['\"](.*?)>", self.addBlockTemplate, line, flags=re.S)

			if re.search(r"{{%(.+?)}}", line):
				line = re.sub(r"{{%(.+?)}}", self.wrappeMeteorExpression, line, flags=re.S)

			if re.search(r"{{!(.+?)}}", line):
				line = re.sub(r"{{!(.+?)}}", self.wrappeMeteorExpression, line, flags=re.S)

			new_content.append(line)

		content = "\n".join(new_content)
		if content.replace("\n","").replace(" ","") == "":
			content = content.replace("\n","").replace(" ","")

		return content

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
		if m.group(1) in self.meteor_tag_templates_list or self.check_in_remove_list(m.group(1)):
			print "in_template_list {} tmpl_list {}".format(m.group(1), self.meteor_tag_templates_list)
			self.remove_next_close = True
			return ""
		self.meteor_tag_templates_list.append(m.group(1))
		source = self.openBlock(m, name="spacebars_" + m.group(1)) + "<template name='{0}'{1}>".format(m.group(1), m.group(2))
		return source

	def get_meteor_template_list(self):
		return self.jinja_xhtml_template_list

	def check_in_remove_list(self, name):
		app = self.curr_app
		template = self.curr_template

		for obj in self.list_meteor_tplt_remove.get(app, []):
			if obj.get("name") == name and obj.get("file") == template:
				return True

		return False

def process_hooks_meteor_templates(apps):
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
					break
				elif not check_in_remove_list(k, r):
					lrm.append(r)

	def process_add(k, add):
		ladd = list_meteor_tplt_add.get(k)
		for a in add:
			if not check_in_remove_list(k, a):
				if not ladd:
					list_meteor_tplt_add[k] = add
					break
				elif not check_in_add_list(k, a):
					ladd.append(a)

	for app in apps:
		hooks = frappe.get_hooks(hook="fluorine_meteor_templates", app_name=app)
		if hooks:
			for k,v in hooks.items():
				remove = v.get("remove") or []
				print "hooks meteor templates 4 {} remove {}".format(hooks, remove)
				process_remove(k, remove)
				add = v.get("add") or []
				process_add(k, add)

	print "meteor templates lists add {} remove {}".format(list_meteor_tplt_add, list_meteor_tplt_remove)
	return list_meteor_tplt_add, list_meteor_tplt_remove

def process_hooks_apps(apps):
	list_apps_add = []
	list_apps_remove = []
	for app in apps:
		hooks = frappe.get_hooks(hook="fluorine_apps", app_name=app)
		print "hooks apps {}".format(hooks)
		if hooks:
			for k,v in hooks.items():
				if v.get("remove")[0]:
					if k not in list_apps_add:
						list_apps_remove.append(k)
				elif v.get("add")[0]:
					if k not in list_apps_remove:
						list_apps_add.append(k)

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