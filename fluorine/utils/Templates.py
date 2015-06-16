__author__ = 'saguas'

import re


class DocumentTemplate(object):

	def __init__(self, list_meteor_tplt_remove):

		self.curr_app = ""
		self.curr_template = ""
		self.jinja_xhtml_template_list = []
		self.templates_to_remove = []
		self.templates_to_include = []
		self.remove_next_close_template = False
		self.remove_next_close_block = False
		self.remove_curr_template = False
		self.extends_found = False
		self.found_super = {}
		self.curr_meteor_template_name = None
		self.include_found = 0
		#register the name of templates tags founded
		self.meteor_tag_templates_list = []
		self.extends_path = []
		self.includs_path = []
		#register the name of jinja2 blocks tags founded
		self.jinja_tag_blocks_list = []
		#register the founded templates
		self.templates_found = []
		self.list_meteor_tplt_remove = list_meteor_tplt_remove
		self.c = c = lambda t:re.compile(t, re.S)
		#TODO add to cache? or add to initialization in develop mode
		self.ENDTEMPLATE = c(r"</\s*template\s*>")
		self.ENDBLOCK = c(r"{%\s+endblock\s+%}")
		self.STARTTEMPLATE = c(r"<\s*template\s+")
		self.METEOR_TEMPLATE_CALL = c(r"({{>)(.+?)}}")
		self.METEOR_TEMPLATE_PERCENT_EXPR = c(r"({{%)(.+?)}}")
		self.METEOR_TEMPLATE_BANG_EXPR = c(r"({{!)(.+?)}}")
		self.BLOCKBEGIN = c(r"{%\s+block(.+?)%}")
		self.STARTTEMPLATE_SUB = c(r"<\s*template\s+name=['\"](.+?)['\"](.*?)(remove|include)?\s*>")
		self.EXTENDS = c(r"{%\s*extends(.+?) (.*?)%}")
		self.INCLUDE = c(r"{%\s*include(.+?) (.*?)%}")
		self.SUPER = c(r"{%\s*super\((.*?)\)\s*%}")


	def replace_for_templates(self, contents):
		new_content = []
		super_templates_remove = []
		self.remove_curr_template = False
		self.remove_next_close_template = False
		self.remove_next_close_block = False
		start_line_template = 0
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
				template_with_super = self.found_super.get(self.curr_meteor_template_name, None)
				content = None
				end_line_template = None
				if template_with_super:
					end_line_template = len(new_content)
					#start_line_template + 1 to skip block and template
					content = "\n".join(new_content[start_line_template + 1:end_line_template])#"\n</template>\n{% endblock %}\n"
					if content.replace("\n","").replace(" ","") == "":
						content = content.replace("\n","").replace(" ","")
					content = self.SUPER.sub(content, template_with_super)
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
					end_line_template = end_line_template or len(new_content)
					if not content:
						content = "\n".join(new_content[start_line_template + 1:end_line_template])#"\n</template>\n{% endblock %}\n"
						if content.replace("\n","").replace(" ","") == "":
							content = content.replace("\n","").replace(" ","")
					self.found_super[self.curr_meteor_template_name] = content
					#super_templates_remove.append({"start":start_line_template, "end": end_line_template + 1})
					start_line_template = 0
					self.remove_curr_template = False
					del new_content[start_line_template:end_line_template]
					continue

			elif self.ENDBLOCK.search(line):
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
				start_line_template = len(new_content)

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

			if self.SUPER.search(line):
				#line = re.sub(r"{%\s+block(.+?)%}", self.process_jinja_blocks, line, flags=re.S)
				line = self.SUPER.sub(self.process_super, line)

			new_content.append(line)

		#for t in super_templates_remove:
			#remove the templates that has super in it
		#	del new_content[t.get("start"):t.get("end")]

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

	#TODO to remove and pass inside the search above
	def process_super(self, m):
		if self.extends_found and self.curr_meteor_template_name:
			self.remove_curr_template = True
		#probably should rise an error if has super but not extends!
		return m.group(0)

	def process_jinja_blocks(self, m):
		if m.group(1) in self.jinja_tag_blocks_list or self.check_in_tplt_remove_list(m.group(1)):
			self.remove_next_close_block = True
			return ""

		self.meteor_tag_templates_list.append(m.group(1))
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
		source = '\n{% block ' + '{}'.format(name or m.group(1)) + " %}\n"#+ ' %}\n{% raw %}\n'
		return source

	def addBlockTemplate(self, m):
		self.curr_meteor_template_name = m.group(1)
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

	def check_in_tplt_remove_list(self, name):
		app = self.curr_app
		template = self.curr_template

		for obj in self.list_meteor_tplt_remove.get(app, []):
			if obj.get("name") == name and obj.get("file") == template:
				print "in teplate remove list is: {}".format(name)
				return True

		return False

class Templates(DocumentTemplate):

	def __init__(self, list_meteor_tplt_remove):
		super(Templates, self).__init__(list_meteor_tplt_remove)

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

	def make_template(self, contents, template):
		c = self.replace_for_templates(contents)
		self.templates_found.append(template)
		return c

	def check_include(self, template):
		if self.include_found and template not in self.extends_path:
			self.includs_path.append(template)
			self.include_found -= 1
			print "included found {}".format(template)
			return True

		return False

	def get_meteor_template_list(self):
		return self.jinja_xhtml_template_list

	def setCurrApp(self,app):
		self.curr_app = app

	def setCurrTemplate(self, template):
		self.curr_template = template

