# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'


from jinja2 import nodes, Markup
from jinja2.ext import Extension
import re, os
import frappe

c = lambda t:re.compile(t, re.S|re.M)
STARTTEMPLATE_SUB_ALL = c(r"<\s*template\s+name\s*=\s*(['\"])(\w+)\1(.*?)\s*>(.*?)<\s*/\s*template\s*>")

op_values = ["and", "or", "band"]

def process_args(parser, blocktype, meteor_token):
	expression = []
	stream = parser.stream

	token = stream.current
	last_token = token

	mtoken = meteor_token
	#print "meteor token {}".format(meteor_token)
	def is_special_token(token):
		return token.value in (".", "[", "]", "{", "}", "(", ")")

	def is_meteor_token(mtoken):
		return mtoken in ("#", "/", ">", "{")

	while not token.type == blocktype:
		if stream.current.test('string'):
			special = is_special_token(last_token)
			last_token = stream.next()
			expression.append(("'%s'" if special else " '%s'") % last_token.value)
			token = stream.current
		elif stream.current.test('name') and stream.current.value not in op_values:
			special = is_meteor_token(mtoken)
			if special:
				mtoken = ""
			else:
				special = is_special_token(last_token)

			last_token = stream.next()
			expression.append(("%s" if special else " %s") % last_token.value)
			token = stream.current
		elif stream.current.value == 'and':
			expression.append(" && ")
			last_token = stream.next()
			token = stream.current
		elif stream.current.value == 'band':
			expression.append(" & ")
			last_token = stream.next()
			token = stream.current
		elif stream.current.value == 'or':
			expression.append(" || ")
			last_token = stream.next()
			token = stream.current
		elif stream.current.value == '|':
			nt = stream.look()
			if nt.value == "|":
				stream.skip()
				expression.append(" || ")
			else:
				expression.append(" | ")
			last_token = stream.next()
			token = stream.current
		else:
			special = is_special_token(last_token)
			last_token = stream.next()
			curr_special = is_special_token(last_token)
			expression.append(("" if special or curr_special else " ") + unicode(last_token.value))
			token = stream.current

	return expression


class MeteorTemplate(Extension):
	# a set of names that trigger the extension.
	tags = set(['meteor'])

	def __init__(self, environment):
		super(MeteorTemplate, self).__init__(environment)

	def parse(self, parser):
		# the first token is the token that started the tag.  In our case
		# we only listen to ``'cache'`` so this will be a name token with
		# `cache` as value.  We get the line number so that we can give
		# that line number to the nodes we create by hand.

		filename = parser.filename

		stream = parser.stream
		tag = stream.next()

		tkeep = nodes.Const(0)
		hightlight = nodes.Const(0)
		tname = stream.expect('name')
		if tname:
			tname = nodes.Const(tname.value)
		else:
			parser.fail("You must provide a name.")

		if stream.skip_if("comma"):
			nameobj = stream.expect('name')
			name = nameobj.value
			if name == "highlight" or name == "hl":
				hightlight = nodes.Const(1)
			elif name == "tkeep":
				tkeep = nodes.Const(1)
			else:
				parser.fail("You must provide a highlight after comma.")

		if stream.skip_if("comma"):
			nameobj = stream.expect('name')
			name = nameobj.value
			if name == "highlight" or name == "hl":
				hightlight = nodes.Const(1)
			elif name == "tkeep":
				tkeep = nodes.Const(1)
			else:
				parser.fail("You must provide a highlight after comma.")


		if filename:
			template_real_path = nodes.Const(filename)
		else:
			template_real_path = nodes.Const(None)

		#frappe.local.context.current_xhtml_template = {"tname": tname.value, "template": filename}
		#print "current template {} template_path {}".format(tname.value, filename)

		lineno = nodes.Const(tag.lineno)
		stream.skip_if('colon')
		stream.expect('block_end')
		body = self._subparse(parser, ("gt", "dot", "mod", "div", "else", "lbrace", 'semicolon'), end_tokens=['name:endmeteor'])
		next(parser.stream)

		ctx_ref = nodes.ContextReference()

		return nodes.CallBlock(
			self.call_method('_template', args=[ctx_ref, tname, template_real_path, lineno, hightlight, tkeep]), [], [], body).\
				set_lineno(tag.lineno)


	def _subparse(self, parser, expr_tokens, end_tokens=None):
		body = []
		data_buffer = []
		add_data = data_buffer.append

		if end_tokens is not None:
			parser._end_token_stack.append(end_tokens)

		def flush_data():
			if data_buffer:
				lineno = data_buffer[0].lineno
				body.append(nodes.Output(data_buffer[:], lineno=lineno))
				del data_buffer[:]
		try:
			while parser.stream:
				token = parser.stream.current
				if token.type == 'data':
					if token.value:
						add_data(nodes.TemplateData(token.value,
										lineno=token.lineno))
					next(parser.stream)
				elif token.type == 'variable_begin':
					next(parser.stream)
					token = parser.stream.current
					if token.test_any(*expr_tokens):
						if token.value == "%":
							#value = ""
							next(parser.stream)
							token = parser.stream.current
							value = token.value
						elif token.value == ";":
							value = "!"
						elif token.value == ".":
							value = "#"
						else:
							value = token.value

						add_data(nodes.TemplateData("{{%s" % value,
													lineno=token.lineno))
						next(parser.stream)
						expression = process_args(parser, 'variable_end', value)
						token = parser.stream.current
						add_data(nodes.TemplateData("".join([unicode(expr) for expr in expression]),
								lineno=token.lineno))

						add_data(nodes.TemplateData("}}",
									lineno=token.lineno))

						parser.stream.expect('variable_end')
						continue

					add_data(parser.parse_tuple(with_condexpr=True))
					parser.stream.expect('variable_end')
				elif token.type == 'block_begin':
					flush_data()
					next(parser.stream)
					if end_tokens is not None and \
					   parser.stream.current.test_any(*end_tokens):
						return body
					rv = parser.parse_statement()
					if isinstance(rv, list):
						body.extend(rv)
					else:
						body.append(rv)
					parser.stream.expect('block_end')
				else:
					raise AssertionError('internal parsing error')

			flush_data()
		finally:
			if end_tokens is not None:
				parser._end_token_stack.pop()

		return body

	def _template(self, ctx, tname, template_real_path, lineno, hightlight, tkeep, caller=None):
		"""Helper callback."""
		from fluorine.utils.fjinja2.utils import export_meteor_template_out, get_meteor_template_parent_path
		from fluorine.utils import is_making_production

		app = get_appname(template_real_path)
		relpath = get_template_path(app, template_real_path)

		frappe.local.context.current_xhtml_template = {"tname": tname, "template": template_real_path, "relpath": relpath}

		if tkeep and relpath:
			ref = get_meteor_template_parent_path(tname, relpath)
			if not ref:
				frappe.throw("mtkeep command only can be used inside meteor templates and only with fluorine templates (Ex. xhtml files) that extends another fluorine template.")
			export_meteor_template_out(tname, ref)

		devmod = ctx.get("developer_mode")
		hightlight_all = ctx.get("highlight_all")
		source = caller()
		if not is_making_production() and (devmod and hightlight or devmod and hightlight_all):
			template = STARTTEMPLATE_SUB_ALL.sub(self.highlight(relpath, lineno, app), source)
		else:
			template = """%s""" % (source)

		return Markup(template.strip())

	def highlight(self, filepath, lineno, appname):

		filepath = filepath or ""
		def _highlight(m):
			import json
			name = m.group(2)
			content = m.group(4)
			attrs = m.group(3)
			debug = {"app":appname, "path": filepath, "lineno": lineno}
			template =\
			"""<template name='%s'%s>\n\t<div class="{{ highlight "%s" '%s' }}">\n\t%s\n\t</div>\n</template>
			""" % (name, attrs, name, json.dumps(debug), content)
			return template
		return _highlight



def get_template_path(app, template_real_path):

	app_path = frappe.get_app_path(app)
	relpath = os.path.relpath(template_real_path, app_path)

	return relpath

def get_appname(template_real_path):
	m = search_template(template_real_path)
	if m:
		app = m.group(1)
		return app

def search_template(template_real_path):
	from fluorine.utils import get_frappe_apps_path

	frappe_apps_path = get_frappe_apps_path()
	pattern = "%s/(.+?)/.+" % frappe_apps_path
	m = re.search(pattern, template_real_path, re.S)

	return m