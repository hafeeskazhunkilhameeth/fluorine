# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'saguas'

import re, frappe,os, fnmatch


c = lambda t:re.compile(t, re.S|re.M)
ENDTEMPLATE = c(r"</\s*template\s*>")
ENDBLOCK = c(r"{%\s+endblock\s+%}")
STARTTEMPLATE = c(r"<\s*template\s+")
METEOR_TEMPLATE_CALL = c(r"({{>)(.+?)}}")
METEOR_TEMPLATE_PERCENT_EXPR = c(r"({{%)(.+?)}}")
METEOR_TEMPLATE_BANG_EXPR = c(r"({{!)(.+?)}}")
BLOCKBEGIN = c(r"{%\s+block(.+?)%}")

#STARTTEMPLATE_SUB = c(r"<\s*template\s+name=['\"](.+?)['\"](.*?)(remove|include)?\s*>")
#STARTTEMPLATE_SUB = c(r"<\s*template\s+name=(['\"])(.+?)\1(.*?)(remove|include)?\s*>")
STARTTEMPLATE_SUB = c(r"<\s*template\s+name\s*=\s*(['\"])(.+?)\1(.*?)\s*>")
STARTTEMPLATE_SUB_ALL = c(r"<\s*template\s+name\s*=\s*(['\"])(.+?)\1(.*?)\s*>(.*?)<\s*/\s*template\s*>")
#STARTTEMPLATE_REMOVE=c(r"remove(?!\s*=)(?=\b)")
STARTTEMPLATE_REMOVE=c(r"((?<=\s)|(?<=^))remove(?!\s*=)(?=\b)")
#STARTTEMPLATE_INCLUDE=c(r"include(?!\s*=)(?=\b)")
STARTTEMPLATE_INCLUDE=c(r"((?<=\s)|(?<=^))include(?!\s*=)(?=\b)")
STARTTEMPLATE_KEEP=c(r"((?<=\s)|(?<=^))keep\s*=\s*(['\"])(.+?)\2")

EXTENDS = c(r"{%\s*extends(.+?) (.*?)%}")
INCLUDE = c(r"{%\s*include(.+?) (.*?)%}")

MSUPER = c(r"{{\s*msuper\((.*?)\)\s*}}")
MSUPERNAME=c(r"name\s*=\s*(['\"])(.+?)\1")
MSUPERFROM=c(r"from\s*=\s*(['\"])(.+?)\1")
MSUPERDEEP=c(r"deep\s*=\s*(.+?)")


COMMENTS = c(r"(?:{#)+(.*)?(?:#})*|{#*(.*)?(?:#})+")
STARTCOMMENTS = c(r"(?:{#)+(.*)")
ENDCOMMENTS = c(r"(.*)(?:#})+")
#PATHTAG = c(r"<\s*paths\s+path=(['\"])([^\1]+?)\1\s*((?:remove|add)=(['\"])([^\4]*?)\4)\s*(template=(['\"])([^\7]*?)\7)?\s*(appname=(['\"])([^\10]*?)\10)?/>")

PATHSTAG = c(r"<\s*paths\s+(.+)/>")
PATHTAG=c(r"path\s*=\s*(['\"])(.*?)\1")
PATHTAGADD=c(r"add\s*=\s*(['\"])(.*?)\1")
PATHTAGREMOVE=c(r"remove\s*=\s*(['\"])(.*?)\1")
PATHTAGAPPNAME=c(r"appname\s*=\s*(['\"])(.+?)\1")
PATHTAGTEMPLATE=c(r"template\s*=\s*(['\"])(.*?)\1")


map_path_to_compile_templates = {}


class Template(object):

	def __init__(self, name):
		self.name = name
		self.path = None
		self.realpath = None
		self.relpath = None
		self.content = None
		self.extends = False
		self.include = False
		self.extends_path  = None
		self.include_path = None
		self.remove = None
		self.startline = -1
		self.endline = -1
		self.templates_keep = []
		self.appname = None
		self.type = ""
		self.template = None
		self.parent = None
		self.addedafter = False




class DocumentTemplate(object):

	def __init__(self, list_meteor_tplt_remove, apps=None, appname=None, template=None, relpath_temp=None, realpath=None, relpath=None, file_temp_path=None, encoding="utf-8"):

		self.encoding = encoding
		self.apps = apps
		self.appname = appname
		self.template = template
		self.jinja_xhtml_template_list = []
		self.templates_to_remove = []
		self.templates_to_include = []
		self.remove_next_close_template = False
		self.remove_next_close_block = False
		self.remove_curr_template = False
		self.extends_found = False
		self.found_super = frappe._dict({})
		self.curr_meteor_template_name = None
		self.include_template_found = False
		#self.include_found = 0
		#register the name of templates tags founded
		#self.meteor_tag_templates_list = []
		self.meteor_tag_templates_list = frappe._dict({})
		self.extends_path = []
		self.includes_path = []
		#register the name of jinja2 blocks tags founded
		#self.jinja_tag_blocks_list = []
		self.list_meteor_tplt_remove = list_meteor_tplt_remove
		self._make_template = False
		self.docs = []
		self._content = None
		self._save_to_temp = True
		self.in_comments = False
		self._save = True
		self._relpath_temp = relpath_temp
		self._file_temp_path = file_temp_path
		self._realpath = realpath
		self.relpath = relpath
		self.template_keep_name = []
		self.pathtag_remove = []
		self.pathtag_add = []

		self.parent = self
		self.origin = "self"
		#self.templates_found_add = frappe.local("templates_found_add")
		#self.templates_found_remove = frappe.local("templates_found_remove")


	def replace_for_templates(self, contents):
		new_content = []
		super_templates_remove = []
		self.remove_curr_template = False
		self.remove_next_close_template = False
		self.remove_next_close_block = False
		self.include_template_found = False
		start_line_template = 0
		count_line = 0
		#self.extends_found = False
		#self.include_found = False
		#print "start replace templ list is 5 {} content {}".format(self.meteor_tag_templates_list, contents)
		def close_template(line):
			if self.remove_next_close_template:
				#line = re.sub(r"</\s*template\s*>", '', line, 1, flags=re.S)
				line = ENDTEMPLATE.sub('', line, 1)
				self.remove_next_close_template = False
			else:
				#line = re.sub(r"</\s*template\s*>", '\n</template>\n{% endblock %}\n', line, flags=re.S)
				line = ENDTEMPLATE.sub('\n</template>\n{% endblock %}\n', line)

			return line

		def close_jinja_block(line):
			if self.remove_next_close_block:
				self.remove_next_close_block = False
				#line = re.sub(r"{%\s+endblock\s+%}", '', line, 1, flags=re.S)
				line = ENDBLOCK.sub('', line, 1)

			return line

		for line in contents.splitlines():
			#if re.search(r"</\s*template\s*>", line):
			#if re.match("^\s+$", line.strip(" ")):
			#	continue

			if STARTCOMMENTS.search(line) and not ENDCOMMENTS.search(line):
				self.in_comments = True
				continue
			elif ENDCOMMENTS.search(line):
				self.in_comments = False
				continue

			if self.in_comments:
				continue

			if ENDTEMPLATE.search(line):
				line = close_template(line)

				#self.make_template_list(new_content, start_line_template, len(new_content), line)
				self.make_template_list(new_content, start_line_template, count_line, line)

				template_with_super = self.found_super.get(self.curr_meteor_template_name, None)
				content = None
				end_line_template = None
				if template_with_super:
					#end_line_template = len(new_content)
					end_line_template = count_line
					#start_line_template + 1 to skip block and template
					content = "\n".join(new_content[start_line_template + 1:end_line_template])#"\n</template>\n{% endblock %}\n"
					if content.replace("\n","").strip() == "":#.replace(" ","") == "":
						content = content.replace("\n","").strip()#.replace(" ","")
					content = MSUPER.sub(content, template_with_super)
					if not self.extends_found:
						del new_content[start_line_template + 1:end_line_template]
						#insert the new content after tag template
						new_content[start_line_template + 1:start_line_template + 1] = [content]
						start_line_template = 0
					#else:
						#update the new content
					#	self.found_super[self.curr_meteor_template_name] = content
				#has and extends and super in template so remove the child template
				if self.remove_curr_template:
					#end_line_template = end_line_template or len(new_content)
					end_line_template = end_line_template or count_line
					if not content:
						content = "\n".join(new_content[start_line_template + 1:end_line_template])#"\n</template>\n{% endblock %}\n"
						if content.replace("\n","").strip() == "":#.replace(" ","") == "":
							content = content.replace("\n","").strip()#.replace(" ","")
					self.found_super[self.curr_meteor_template_name] = content
					#super_templates_remove.append({"start":start_line_template, "end": end_line_template + 1})
					start_line_template = 0
					self.remove_curr_template = False
					self.curr_meteor_template_name = None
					del new_content[start_line_template:end_line_template]
					continue

				self.curr_meteor_template_name = None

			elif ENDBLOCK.search(line):
				line = close_jinja_block(line)
				self.make_template_list(new_content, start_line_template, count_line, line, type="block")
				start_line_template = 0
				self.curr_meteor_template_name = None

			if self.remove_next_close_template or self.remove_next_close_block:
				continue

			#count_line += 1

			include = INCLUDE.search(line)
			if include:
				#ipathname = include.group(1).replace(" ","").replace("\'","")
				ipathname = include.group(1).strip().replace("\'","")
				"""
				self.include_found += 1
				for n in self.jinja_xhtml_template_list:
					if n.get("name") == include.group(1).replace(" ","").replace("\'",""):
						#print "removing from list jinja templates 5 {} jinja {}".format(include.group(1), self.jinja_xhtml_template_list)
						self.includs_path.append(n.get("name"))
						self.jinja_xhtml_template_list.remove(n)
						self.include_found -= 1
						break
				"""
				self.includes_path.append(ipathname)
				#self.includs_path.append(include.group(1).replace(" ","").replace("\'",""))

			extends = EXTENDS.search(line)
			if extends:
				#import ast
				self.extends_found = True
				#print "extends group 2 {}".format(ast.literal_eval(extends.group(1).replace(" ","")))
				#self.extends_path.append(ast.literal_eval(extends.group(1).replace(" ","")))
				#self.extends_path.append(extends.group(1).replace(" ","").replace("\'",""))
				#print "in extends extends.group(1) 1 {}".format(extends.group(1).strip())
				self.extends_path.append(extends.group(1).strip().replace("\'",""))

			#if re.search(r"<\s*template\s+", line):
			if STARTTEMPLATE.search(line):
				#line = re.sub(r"<\s*template\s+name=['\"](.+?)['\"](.*?)>", self.addBlockTemplate, line, flags=re.S)
				line = STARTTEMPLATE_SUB.sub(self.addBlockTemplate, line)
				#start_line_template = len(new_content)
				start_line_template = count_line

			#if re.search(r"{{>(.+?)}}", line):
			if METEOR_TEMPLATE_CALL.search(line):
				#line = re.sub(r"{{>(.+?)}}", self.wrappeMeteorExpression, line, flags=re.S)
				line = METEOR_TEMPLATE_CALL.sub(self.wrappeMeteorExpression, line)

			#expression of meteor must be preceded with % or !
			#if re.search(r"{{%(.+?)}}", line):
			if METEOR_TEMPLATE_PERCENT_EXPR.search(line):
				#line = re.sub(r"{{%(.+?)}}", self.wrappeMeteorExpression, line, flags=re.S)
				line = METEOR_TEMPLATE_PERCENT_EXPR.sub(self.wrappeMeteorExpression, line)

			#expression of meteor must be preceded with % or !
			#if re.search(r"{{!(.+?)}}", line):
			if METEOR_TEMPLATE_BANG_EXPR.search(line):
				#line = re.sub(r"{{!(.+?)}}", self.wrappeMeteorExpression, line, flags=re.S)
				line = METEOR_TEMPLATE_BANG_EXPR.sub(self.wrappeMeteorExpression, line)

			#if re.search(r"{%\s+block(.+?)%}", line):
			if BLOCKBEGIN.search(line) and not self.curr_meteor_template_name:
				#line = re.sub(r"{%\s+block(.+?)%}", self.process_jinja_blocks, line, flags=re.S)
				line = BLOCKBEGIN.sub(self.process_jinja_blocks, line)
				start_line_template = count_line

			if MSUPER.search(line):
				#line = re.sub(r"{%\s+block(.+?)%}", self.process_jinja_blocks, line, flags=re.S)
				line = MSUPER.sub(self.process_super, line)

			#if PATHTAG.search(line):
			line = PATHSTAG.sub(self.process_pathtag, line)

			#if not re.match("^\\n$", line.strip(" ")):
			#if not re.match("^\s+$", line):
			new_content.append(line)
			count_line += 1

		#for t in super_templates_remove:
			#remove the templates that has super in it
		#	del new_content[t.get("start"):t.get("end")]
		"""
		if not self.extends_found:
			includes = self.templates_to_include[:]
			del self.templates_to_include[:]
			for name in includes:
				tcontents = '<template name="%s">\n' % name + '</template>\n'
				#self.templates_to_include.remove(name)
				lines = self.replace_for_templates(tcontents)
				print "includes templates 2 {} lines {}".format(includes, lines)
				new_content.append(lines)
		"""
		#content = "\n\n".join(new_content)
		#print "content in replace method template {} content {}".format(self.template, content)
		#if content.replace("\n","").replace(" ","") == "":
		#	content = content.replace("\n","").replace(" ","")

		content = "\n\n".join([s for s in new_content if s])
		#list of doc that extends and are includeds
		docs = self.process_references(content, force=True)
		self.docs.extend(docs)

		"""
		meteor_tag_templates_list = list(self.meteor_tag_templates_list.keys())

		for doc in docs:
			if doc.template in self.includes_path:
				#don't save because may change content with remove of templates
				doc._save_to_temp = False
				meteor_tag_templates_list.extend(doc.meteor_tag_templates_list.keys())

		self.process_docs_references(self.docs, meteor_tag_templates_list)
		"""

		#this template is for get_template function
		self._make_template = True

		#adoc = self.flat_and_remove_docs(self)
		#ldoc = adoc[0] if adoc else self
		#for d in self.docs:
		#	if not d.extends_found:
		#		d._content = self.change_doc_content_remove(d)

		#we are in last doc. If not extend and was not include it is the last doc
		#ldoc = self.lastDoc(self)
		#if self.templates_to_include:
		#	ldoc._content = self.change_doc_content_include(ldoc)
			#print "templates to include 2 {} and last doc is {} from {} lista {} content {}".format(self.templates_to_include, ldoc.template, self.template, ldoc.meteor_tag_templates_list, ldoc.content)

		#self.make_final_list_of_templates()

		#self.make_template_remove_regexp()
		#if not self.extends_found:
		#	self.make_path_add(self)

		return content

	def lastDoc(self, doc):
		if doc.extends_found:
			ext = doc.extends_path[0]
			for d in doc.docs:
				if d.template == ext:
					return self.lastDoc(d)
		return doc

	def make_final_list_of_templates(self):

		#remove self templates
		#for tname in self.templates_to_remove:
		#	if tname in self.meteor_tag_templates_list:
		#		self.insere_template_to_remove_path(tname, self.appname, self.appname, self.realpath)
		#flat = self.flat_and_remove_docs(self)
		self.flat_and_remove_docs(self)

		#if self.extends_found:
		#	doc = flat[0]
			#if self.templates_to_remove:
				#for d in doc.docs:#if last doc has include process
				#	from file import read
				#	content = read(doc.file_temp_path)
				#only remove from the last one in each chain of extends. Jinja will after that remove every template that not exist in the last one.
				#d._content = self.change_doc_content_remove(d)
			#	doc._content = self.change_doc_content_remove(doc)
				#print "flat doc 0 is 4 {} self is {} content {}".format(doc.template, self.template, doc.content)

			#if self.templates_to_include: #and doc.template not in self.includes_path:
			#	doc._content = self.change_doc_content_include(doc)

		#from is inputs remove any template in the list of templates to remove
		#for i in self.includes_path:
		#	for d in self.docs:
				#print "include_path i 3 {} d.template {} is equal {}".format(i, d.template, i == d.template)
		#		if i == d.template:
		#			d._content = self.change_doc_content_remove(d)

		"""
		def make_template(doc, tname, ttype):
			tt = Template(tname)
			tt.appname = doc.appname
			tt.templates_keep.extend(doc.template_keep_name)
			tt.realpath = doc.realpath
			tt.type = ttype
			tt.relpath = doc.relpath
			tt.template = doc.template
			tt.extends = doc.extends_found
			tt.parent = doc
			return tt
		"""
		"""
		def check_lastdoc_includes(doc, tname):
			includes = []
			for d in doc.docs:
				if tname in d.meteor_tag_templates_list:
					includes.append(d)
			return includes
		"""
		def is_in_extend_path(doc, template):
			for d in doc.docs:
				if d.template == template:
					#return True
					return d
				found = is_in_extend_path(d, template)
				if found:
					#return True
					return found
			#return False
			return None

		#ldoc = lastDoc(self)
		#put here to let extends and include same meteor template name from different sources
		for tname in self.meteor_tag_templates_list.keys():
			#print "tname in meteor tag templates list 3 {} keys {}".format(tname, frappe.local.meteor_Templates.keys())
			#the template must exist in the last template in case of extends to be valid template
			if tname in frappe.local.meteor_Templates.keys():
				#inc = check_lastdoc_includes(ldoc, tname)
				#if tname in ldoc.meteor_tag_templates_list or len(inc) > 0:
				t = frappe.local.meteor_Templates.get(tname)
				self.insere_template_to_remove_path(tname, self.appname, t.appname, t.realpath)
				#if remove a template and not extend anything then that template must be removed
				if not self.extends_found:
					if self.template not in self.parent.includes_path and t.template not in self.includes_path: #and not self.parent:
						frappe.msgprint("Duplicated Template {} in app {} file {} from app {} in file {}. \nTIP: There is another template with the same name in another extend path. If you want to replace him then extend {}.".format(tname, t.appname, t.template, self.appname, self.template, self.template), raise_exception=1)
					"""
					doc = self.lastDoc(t.parent)
					if tname in doc.meteor_tag_templates_list:
						tt = make_template(doc, t.name, t.type)
						frappe.local.meteor_dynamic_templates_remove[t.template] = tt
						doc.insere_template_to_remove_path(tname, doc.appname, tt.appname, tt.realpath)

					inc = check_lastdoc_includes(doc, tname)
					for d in inc:
						if tname in d.meteor_tag_templates_list:
							tt = make_template(d, t.name, t.type)
							frappe.local.meteor_dynamic_templates_remove[t.template] = tt
							d.insere_template_to_remove_path(tname, d.appname, tt.appname, tt.realpath)
					"""

				else:
					#found = False
					#for d in self.docs:
					#	if d.template == t.template:
					#		found = True
					#		break

					#if not found:
					#Here we are in the case where a template does not exist in the extend path but exist in another extend path
					if not is_in_extend_path(self, t.template):
						frappe.msgprint("Duplicated Template {} in app {} file {} from app {} in file {}. \nTIP: There is another template with the same name in another extend path. If you want to replace him then extend {}.".format(tname, t.appname, t.template, self.appname, self.template, self.template), raise_exception=1)
						#self.insere_template_to_remove_path(tname, self.appname, self.appname, self.realpath)

				#	inc = check_lastdoc_includes(ldoc, tname)
				#	if tname in ldoc.meteor_tag_templates_list or len(inc) > 0:
				#		continue
					#in this case we extend but there is no template from the doc (or the includes) we extend so exclude him
					#self.insere_template_to_remove_path(tname, self.appname, self.appname, self.realpath)
				#print "found tname in meteor tag templates list will remove 4 {} who_appname {} where_appname {} realpath {}".format(tname, self.appname, t.appname, t.template)
			elif self.extends_found and tname not in self.templates_to_include:
				#if name of template not in any template yet then as we are extending the template will be removed by jinja so remove is folder
				#last = flat[0]
				#if tname in last.meteor_tag_templates_list:
				self.insere_template_to_remove_path(tname, self.appname, self.appname, self.realpath)
				continue

			#if self.template == "templates/includes/teste2.xhtml":
			#	print "lastdoc list tname 2 {} list {}".format(tname, self.meteor_tag_templates_list)
			frappe.local.meteor_Templates[tname] = self.meteor_tag_templates_list.get(tname)

	def flat_and_remove_docs(self, doc):

		flat = []

		for tname in self.templates_to_remove:
			if tname in doc.meteor_tag_templates_list:
				self.insere_template_to_remove_path(tname, self.appname, doc.appname, doc.realpath)
				try:
					del frappe.local.meteor_Templates[tname]
				except:
					pass

		for d in doc.docs:
			d._save = False
			self.make_path_remove(d)
			# from his include tags remove any template in the list of templates to remove. If include has extends then remove only in the last one.
			# or is the last document and remove from there
			#if (d.template in doc.includes_path and not d.extends_found) or (d.template not in doc.includes_path and not d.extends_found):
			#we have to remove the includes too or else it will include the removed templates
			if not d.extends_found:# and d.template not in doc.includes_path:
				d._content = self.change_doc_content_remove(d)
				#print "last doc template name {} and content {}".format(d.template, d.content)
				#we are in last doc. If not extend and was not include it is the last doc
				if self.templates_to_include and d.template not in doc.includes_path:
					d._content = self.change_doc_content_include(d)
			#if the templates to remove is in the list of doc templates then remove is path
			#for tname in self.templates_to_remove:
			#	if tname in d.meteor_tag_templates_list:
			#		self.insere_template_to_remove_path(tname, self.appname, d.appname, d.realpath)
					#try:
						##del d.meteor_tag_templates_list[tname]
					#	del frappe.local.meteor_Templates[tname]
					#except:
					#	pass
			#for tname in self.templates_to_remove:
			#	if tname in d.meteor_tag_templates_list:
					#self.insere_template_to_remove_path(d.appname, tname)
			#d._content = self.change_doc_content_remove(d)
			#if d.docs:
			flat.extend(self.flat_and_remove_docs(d))

			flat.append(d)

		return flat

	#not used
	def process_tag_path(self, doc):
		self.make_path_remove(doc)

	def make_template_remove_regexp(self):
		basename = os.path.basename(self.template)[:-6]
		dirname = os.path.dirname(self.template)
		idx = self.apps.index(self.appname) + 1
		apps = self.apps[idx:]
		order = self.apps.index(self.appname)
		for app in apps:
			app_path = frappe.get_app_path(app)
			pattern = fnmatch.translate(os.path.join(app_path, dirname, basename + "*"))
			#frappe.local.templates_found_remove.add(c(pattern))
			if not frappe.local.templates_found_remove.get(app, None):
				frappe.local.templates_found_remove[app] = frappe._dict({})
			frappe.local.templates_found_remove.get(app)[pattern] = frappe._dict({"compiled": c(pattern), "order": order})

		if not frappe.local.templates_found_remove.get(app, None):
			frappe.local.templates_found_remove[app] = frappe._dict({})
		frappe.local.templates_found_remove.get(app)[pattern] = frappe._dict({"compiled": c(pattern), "order": order})

	#not used
	def make_template_add_regexp(self):
		basename = os.path.basename(self.template)[:-6]
		dirname = os.path.dirname(self.template)
		app_path = frappe.get_app_path(self.appname)
		pattern = fnmatch.translate(os.path.join(app_path, dirname, basename, "*"))
		#frappe.local.templates_found_add.add(c(pattern))
		order = self.apps.index(self.appname)
		if not frappe.local.templates_found_remove.get(self.appname, None):
			frappe.local.templates_found_remove[self.appname] = frappe._dict({})
		frappe.local.templates_found_add.get(self.appname)[pattern] = frappe._dict({"compiled": c(pattern), "order": order})

	def make_path_remove(self, doc):
		order = self.apps.index(self.appname)
		for r in self.pathtag_remove:
			if r.template == doc.template:
				#basename = os.path.basename(r.template)[:-6]
				path = r.path.strip()
				if path.startswith("/"):
					path = path.replace("/", "", 1)
				dirname = os.path.dirname(r.template)
				app_path = frappe.get_app_path(doc.appname)
				rmpath = os.path.join(app_path, dirname, path, r.pattern)
				pattern = fnmatch.translate(rmpath)
				#frappe.local.templates_found_remove.add(c(pattern))
				if not frappe.local.templates_found_remove.get(doc.appname, None):
					frappe.local.templates_found_remove[doc.appname] = frappe._dict({})
				frappe.local.templates_found_remove.get(doc.appname)[pattern] = frappe._dict({"compiled": c(pattern), "order": order})

	#not used
	def make_path_add(self, doc):
		order = self.apps.index(self.appname)
		for a in self.pathtag_add:
			if a.template == doc.template:
				#basename = os.path.basename(r.template)[:-6]
				path = a.path.strip()
				if path.startswith("/"):
					path = path.replace("/", "", 1)
				dirname = os.path.dirname(a.template)
				app_path = frappe.get_app_path(a.appname)
				adpath = os.path.join(app_path, dirname, path, a.pattern)
				pattern = fnmatch.translate(adpath)
				#frappe.local.templates_found_remove.add(c(pattern))
				if not frappe.local.templates_found_remove.get(doc.appname, None):
					frappe.local.templates_found_remove[doc.appname] = frappe._dict({})
				frappe.local.templates_found_add.get(doc.appname)[pattern] = frappe._dict({"compiled": c(pattern), "order": order})

	#not used
	def make_template_remove_path(self, doc, name):

		def check_others(doc, name):
			for d in doc.docs:
				if d.template not in doc.includes_path:
					if not d.extends_found:
						if name in d.meteor_tag_templates_list.keys():
							return True
						else:
							return False
					return check_others(d, name)
			return False

		if name in doc.meteor_tag_templates_list.keys():
			self.add_template_to_remove_path(doc, name)
			#for d in doc.docs:
			#	res = doc.make_template_remove(d, name)
		elif not doc.extends_found:
			self.add_template_to_remove_path(self, name)
		else:
			res = check_others(doc, name)
			if not res:
				self.add_template_to_remove_path(self, name)

	def insere_template_to_remove_path(self, name, appname_who, appname_where, realpath):

		#app_path = frappe.get_app_path(appname)
		#path = os.path.join(app_path, name)
		basename = os.path.basename(realpath)
		dirpath = os.path.dirname(realpath)
		#path = os.path.join(dirpath, basename[:-6], "*", name, "*")
		path = os.path.join(dirpath, basename[:-6])
		#pattern = path + r"/(?:[^\s]+/)?(?:(?:%s)/.*|(?:%s$))" % (name, name)
		pattern = path + r"/(?:[^\s]+/)?(?:(?:%s)/[^\s/]+|(?:%s/?$))" % (name, name)
		if not frappe.local.templates_found_remove.get(appname_where, None):
			frappe.local.templates_found_remove[appname_where] = frappe._dict({})

		# less order bigger priority
		order = self.apps.index(appname_who)
		frappe.local.templates_found_remove.get(appname_where)[pattern] = frappe._dict({"compiled": c(pattern), "order":order})
		#pattern = fnmatch.translate(path)
		print "listing templates to remove path 8 {} pattern {}".format(path, pattern)
		#self.templates_found_remove.add(c(pattern))
		#frappe.local.templates_found_remove.add(c(pattern))

	#not used
	def add_template_to_remove_path(self, doc, name):
		appname = None
		realpath = None
		if name.startswith("/"):
			name = name.replace("/", "", 1)
		#tdirname = os.path.dirname(name)
		if name in doc.meteor_tag_templates_list:
			appname = doc.appname
			realpath = doc.realpath
		else:
			for d in doc.docs:
				if d.template in doc.includes_path:
					if name in d.meteor_tag_templates_list:
						appname = d.appname
						realpath = d.realpath

		self.insere_template_to_remove_path(name, doc.appname, appname, realpath)

	"""
	def process_docs_references(self, docs, meteor_tag_templates_list):
		#only the first extends will be save

		for doc in docs:
			#print "referenced docs for template name {} docs {} name {}".format(self.template, self.docs, self.docs)
			#if doc.extends_found:

			#if doc.template in self.includes_path:
				#don't save because may change content with remove of templates
			#	doc.save_to_temp = False
			#	meteor_tag_templates_list.extend(doc.meteor_tag_templates_list.keys())

			doc._save = False
			self.make_path_remove(doc)

			if doc.template not in self.includes_path:
				for name in meteor_tag_templates_list:
					self.make_template_remove_path(doc, name)
					#if not res:
					#	self.add_template_to_remove_path(doc, name)
			#if self.extends_found: #and (self.include_template_found or self.templates_to_remove):
				#we are in extends so keep the content in memory
				#print "for doc in docs template 4 {} remove {} doc {} extends_found {}".format(self.template, self.templates_to_remove, doc.template, doc.extends_found)
			#if doc.extends_found:
			#TODO ver se qual coloco a lista toda ou a parcial
			self.process_docs_references(doc.docs, doc.meteor_tag_templates_list)

			#maybe an include or the end of extends (last file that does not extend anything)
			if not doc.extends_found:
				#from file import read
				#content = read(doc.file_temp_path)
				doc._content = self.change_doc_content_remove(doc)
				if doc.template not in self.includes_path:
					doc._content = self.change_doc_content_include(doc, doc._content)
					doc._save_to_temp = False
					#doc._save = True
				#if doc.extends_found and (doc.include_template_found or doc.templates_to_remove):
				#	doc._content = new_content
	"""

	def change_doc_content_remove(self, doc):
		from file import read

		content = doc.content

		if self.templates_to_remove:
			if not content:
				content = read(doc.file_temp_path).decode(self.encoding)
			for tname in self.templates_to_remove:
				if tname in doc.meteor_tag_templates_list:
					#block = c(r"{%\s+block\s+(%s)s\s+%}" % tname)
					block_txt = r"{%\s+block\s+spacebars_" + tname + r"\s+%}(.*?){%\s*endblock\s*%}"
					block = c(block_txt)
					#print "content before remove in template 3 {} template {} content {}".format(doc.template, tname, content)
					content = block.sub("", content)

					#self.insere_template_to_remove_path(tname, self.appname, doc.appname, doc.realpath)
					#try:
					#	del frappe.local.meteor_Templates[tname]
					#except:
					#	pass
				#for d in doc.docs:#if last doc has include process
				#	d._content = self.change_doc_content_remove(d)
					#print "\n\n\nself template name 6 {} doc template name {} templates to remove {} doc.meteor_tag_templates_list {} block to remove {} \n\ncontent after remove {}\n\n\n".format(self.template, doc.template, self.templates_to_remove, doc.meteor_tag_templates_list, block_txt, content)
					#self.add_template_to_remove_path(doc, tname)

					#self.insere_template_to_remove_path(doc.appname, tname)
					#try:
					#	del frappe.local.meteor_Templates[tname]
					#except:
					#	pass
					#self.add_template_to_remove_path(doc, tname)
					#print "content after remove in template 3 {} template {} content {}".format(doc.template, tname, content)

		return content

	def change_doc_content_include(self, doc):
		from file import read

		content = doc._content
		#if doc.template not in self.includes_path:
		if self.templates_to_include:
			if not content:
				content = read(doc.file_temp_path).decode(self.encoding)

			for name in self.templates_to_include:
				t = self.meteor_tag_templates_list.get(name)

				#tt = frappe.local.meteor_Templates.get(name)
				#if tt:
				#	self.insere_template_to_remove_path(name, self.appname, tt.appname, tt.realpath)

				template = r"<\s*template\s+name\s*=\s*(['\"])"+ name + r"\1(.*?)\s*>"
				if re.search(template, content, re.S|re.I|re.M):
					continue

				"""
				ttt = Template(name)
				ttt.appname = doc.appname
				ttt.templates_keep.extend(doc.template_keep_name)
				ttt.realpath = doc.realpath
				ttt.relpath = doc.relpath
				ttt.parent = doc
				ttt.type = t.type
				ttt.extends = doc.extends_found
				ttt.template = doc.template
				ttt.addedafter = True

				#frappe.local.meteor_Templates[name] = ttt
				doc.meteor_tag_templates_list[name] = ttt
				"""
				#Only change content if not there yet. No need to replace if it already there one template
				content = content + '\n' + t.content
				#doc._save_to_temp = False

		print "docs to include 4 {} content {}".format(doc.template, content)
		return content

	def make_template_list(self, contents, startline, endline, lastline, type="template"):

		if self.remove_next_close_template:
			##self.add_template_to_remove_path(self, self.curr_meteor_template_name)
		#	self.insere_template_to_remove_path(self.curr_meteor_template_name, self.appname, self.appname, self.realpath)
			return
		t = Template(self.curr_meteor_template_name)
		t.appname = self.appname
		t.templates_keep.extend(self.template_keep_name)
		#t.extends = self.extends_found
		#t.extends_path = self.extends_path[0] if self.extends_found else None
		#t.include = self.include_found
		#t.include_path = self.includes_path[0] if self.include_found else None
		#t.remove = self.remove_next_close_template
		t.startline = startline
		t.endline = endline
		t.realpath = self.realpath
		t.type = type
		t.relpath = self.relpath
		t.template = self.template
		t.extends = self.extends_found
		t.parent = self

		if self.include_template_found:
			t.include = True
			t.content = contents[startline] + "\n" + lastline
			self.include_template_found = False

		self.meteor_tag_templates_list[self.curr_meteor_template_name] = t

	def process_pathtag(self, m):

		pattern = ""
		remove = ""

		p = PATHTAG.search(m)
		if p:
			path = p.group(2)
		else:
			path = "*"

		add = PATHTAGADD.search(m)
		if add and not self.extends_found:
			pattern = add.group(2)
			obj = frappe._dict({"path": path, "pattern": pattern})
			obj["template"] = self.template
			self.pathtag_add.append(obj)
		else:
			remove = PATHTAGREMOVE.search(m)
			if remove:
				pattern = remove.group(2)

			obj = frappe._dict({"path": path, "pattern": pattern})
			t = PATHTAGTEMPLATE.search(m)
			if t:
				template = t.group(2)
			else:
				template = self.extends_path[0] if self.extends_path else ""

			obj["template"] = template
			self.pathtag_remove.append(obj)

		return ""

	#TODO to remove and pass inside the search above
	def process_super(self, m):
		#if self.extends_found and self.curr_meteor_template_name:
		#	self.remove_curr_template = True
		#probably should rise an error if has super but not extends!
		args = m.group(1)
		if args:
			n = MSUPERNAME.search(args)
			if n:
				name = n.group(2).strip()
			else:
				name = self.curr_meteor_template_name
			f = MSUPERFROM.search(args)
			if f:
				ffrom = f.group(2).strip()
			else:
				ffrom = ""
			d = MSUPERDEEP.search(args)
			if d:
				deep = d.group(1)
			else:
				deep = 1
		else:
			ffrom = ""
			name = self.curr_meteor_template_name
			deep = 1

		return "{{ msuper(curr_tplt='%s', deep=%s, name='%s', ffrom='%s') }}" % (self.template, deep, name, ffrom)

	def process_jinja_blocks(self, m):
		name = m.group(1).strip()
		self.curr_meteor_template_name = name
		#if name in frappe.local.jinja_blocks or self.check_in_tplt_remove_list(name):
		if self.check_in_tplt_remove_list(name):
			self.remove_next_close_block = True
			return ""

		#self.meteor_tag_templates_list.append(m.group(1))
		return m.group(0)

	def remove_template(self, name, content):
		re.sub("<template name=['\"]"+ name + "['\"](.*?)>(.*?)</template>", "", content, flags=re.S)

	def wrappeMeteorRawExpression(self, m):
		source = self.openRaw() + m.group(0).replace("{{%", "{{").replace("{{!", "{{") + self.closeRaw()
		return source

	def wrappeMeteorExpression(self, m):
		#source = m.group(0).replace("{{%", "{{ '{{' }}").replace("{{!", "{{ '{{' }}").replace("{{>", "{{ '{{>' }}").replace("}}", "{{ '}}' }}")
		source = "{{ '%s%s' }} {{ '}}' }}" % (m.group(1).replace("{{%","{{").replace("{{!","{{"), m.group(2))
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
		source = '\n{% block ' + '{}'.format(name or m.group(2)) + " %}\n"#+ ' %}\n{% raw %}\n'
		return source

	def addBlockTemplate(self, m):
		template_name = m.group(2).strip()
		self.curr_meteor_template_name = template_name
		#print "in block template template 5 {} remove? {}".format(m.group(2), m.group(4)=="remove")
		tail = m.group(3)

		if tail:
			tk = STARTTEMPLATE_KEEP.search(tail)
			if tk:
				self.template_keep_name.append(tk.group(3).strip())
				tail = STARTTEMPLATE_KEEP.sub("", tail)

			if STARTTEMPLATE_REMOVE.search(tail):
				tail = STARTTEMPLATE_REMOVE.sub("", tail)
				self.remove_next_close_template = True
				self.templates_to_remove.append(template_name)
				return ""
			#TODO give error if include and remove
			else:
				if STARTTEMPLATE_INCLUDE.search(tail):
					tail = STARTTEMPLATE_INCLUDE.sub("", tail)
					self.include_template_found = True
					self.templates_to_include.append(template_name)

		#if template_name in frappe.local.meteor_Templates.keys() or self.check_in_tplt_remove_list(template_name) or template_name in self.templates_to_remove:
		if self.check_in_tplt_remove_list(template_name) or template_name in self.templates_to_remove:
			self.remove_next_close_template = True
			self.include_template_found = False
			try:
				self.templates_to_include.remove(template_name)
			except:
				pass
			return ""
		#TODO give error if inside a block tag
		#if not self.extends_found:
		#	t = Template(m.group(1))
		#	self.meteor_tag_templates_list[m.group(1)] = t
			#self.meteor_tag_templates_list.append(m.group(1))

		source = self.openBlock(m, name="spacebars_" + template_name) + "<template name='{0}'{1}>".format(template_name, tail)
		return source

	def check_in_tplt_remove_list(self, name):
		app = self.appname
		template = self.template

		for obj in self.list_meteor_tplt_remove.get(app, []):
			if obj.get("name") == name and obj.get("file") == template:
				print "in teplate remove list is: {}".format(name)
				return True

		return False

	#Process dependencies in template.
	#Finds all the referenced templates from the AST. This will return an iterator over all
	#the hardcoded template extensions, inclusions and imports. If dynamic inheritance
	#or inclusion is used, None will be yielded.
	def process_references(self, source, force=False):
		from jinja2 import meta
		from fluorine.utils.spacebars_template import fluorine_get_fenv

		docs = []
		env = fluorine_get_fenv()
		for referenced_template_path in meta.find_referenced_templates(env.parse(source)):
			if referenced_template_path:
				#self.load(referenced_template_path)
				doc = fluorine_get_fenv().addto_meteor_templates_list(referenced_template_path, force=force)
				if doc:
					print "referenced docs for template name 6 {} reference template path {} doc {}".format(self.template, referenced_template_path, doc.template)
					doc.parent = self
					if doc.template in self.includes_path:
						doc.origin = "include"
					elif doc.template in self.extends_path:
						doc.origin = "extend"
					doc._make_template = False
					docs.append(doc)

		return docs

	def __eq__(self, obj):
		return self.__dict__ == obj.__dict__

	@property
	def make_template(self):
		return self._make_template

	@property
	def save(self):
		return self._save

	@property
	def save_to_temp(self):
		return self._save_to_temp

	@property
	def realpath(self):
		return self._realpath

	@property
	def file_temp_path(self):
		return self._file_temp_path

	@property
	def relpath_temp(self):
		return self._relpath_temp

	@property
	def content(self):
		return self._content

class Templates(object):

	def __init__(self, list_meteor_tplt_remove, apps=None):
		self.list_meteor_tplt_remove = list_meteor_tplt_remove
		self.apps = apps
		#self.templates_found = []
		frappe.local.meteor_Templates = frappe._dict({})
		frappe.local.jinja_blocks = frappe._dict({})
		#super(Templates, self).__init__(list_meteor_tplt_remove)

	"""
	def process_include_excludes(self, name, template):

		if name in self.extends_path or name in self.includs_path:
			print "load func name 3 {} extends_path {} include_path {} jinja template list {}".format(name, self.extends_path, self.includs_path, self.jinja_xhtml_template_list)
			#for n in self.jinja_xhtml_template_list:
			#	print "load func before save removing from list jinja templates 7 {} jinja {} extends {} found {} jinja template list {}".format(name, n.get("name"), self.extends_path, self.include_found, self.jinja_xhtml_template_list)
			#	if n.get("name") == name:
			#		self.jinja_xhtml_template_list.remove(n)
			#		break
			#save_to_file = False
			return template

		self.jinja_xhtml_template_list.append({"name": name, "template": template})

	def check_found_include(self, name):
		#A template with the same name was already found in a more recent installed app... ignore
		print "inload func name 5 {} includs_path {}".format(name, self.includs_path)
		if name in self.templates_found or name in self.includs_path:
			print "load func name 6 {} include_path {} templTES FOUND {}".format(name, self.includs_path, self.templates_found)
			for n in self.jinja_xhtml_template_list:
				if n.get("name") == name:
					self.jinja_xhtml_template_list.remove(n)
					break
			return False

		return True
	"""

	def make_template(self, contents, appname=None, template=None, relpath_temp=None, realpath=None, relpath=None, file_temp_path=None, encoding="utf-8"):
		doc = DocumentTemplate(self.list_meteor_tplt_remove, apps=self.apps, appname=appname, template=template, relpath_temp=relpath_temp, realpath=realpath, relpath=relpath, file_temp_path=file_temp_path, encoding=encoding)
		contents = doc.replace_for_templates(contents)
		#self.process_references(contents)
		#self.check_include(template)

		return doc, contents

	def check_include(self, template):
		if self.include_found and template not in self.extends_path:
			self.includs_path.append(template)
			self.include_found -= 1
			print "included found {}".format(template)
			return True

		return False

	#def get_meteor_template_list(self):
	#	return self.jinja_xhtml_template_list

	def setCurrApp(self,app):
		self.curr_app = app

	def setCurrTemplate(self, template):
		self.curr_template = template

