# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'


from jinja2 import nodes, Markup
from jinja2.ext import Extension
import re, os
import frappe

c = lambda t:re.compile(t, re.S|re.M)
STARTTEMPLATE_SUB_ALL = c(r"<\s*template\s+name\s*=\s*(['\"])(\w+)\1(.*?)\s*>(.*?)<\s*/\s*template\s*>")


def process_args(parser, blocktype):
	expression = []
	stream = parser.stream

	token = stream.current
	last_token = token

	def is_special_token(token):
		return token.value in (".", "[", "]", "{", "}", "(", ")")


	while not token.type == blocktype:

		if stream.current.test('string'):
			special = is_special_token(last_token)
			last_token = stream.next()
			expression.append(("'%s'" if special else " '%s'") % last_token.value)
			token = stream.current
		elif stream.current.test('name'):
			special = is_special_token(last_token)
			last_token = stream.next()
			expression.append(("" if special else " ") + last_token.value)
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


	"""
	elif stream.current.test('name') and stream.look().test('dot'):
	token = stream.next()
	name = " %s" % token.value
	name = name + "."
	stream.skip()
	vv = stream.next().value
	name = name + "%s" % vv
	expression.append(name)
	token = stream.current

	"""

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
		stream = parser.stream
		tag = stream.next()

		# now we parse a single expression that is used as cache key.

		#expression = process_args(parser, 'block_end')
		#expressions = nodes.Const(" ".join([unicode(expr) for expr in expression]))
		#name_tag = nodes.Const(tag.value)

		tname = stream.expect('name')
		if tname:
			tname = nodes.Const(tname.value)
		else:
			parser.fail("You must provide a name")

		app_path = os.path.normpath(os.path.join(frappe.get_app_path("fluorine"), "..", ".."))

		filename = parser.filename

		if filename:
			filepath = os.path.relpath(parser.filename, app_path)
			filepath = nodes.Const(filepath.split("/",1)[1])
		else:
			filepath = nodes.Const(None)

		stream.skip_if('colon')
		stream.expect('block_end')
		body = self._subparse(parser, ("gt", "dot", "mod", "div", "else", "lbrace"), end_tokens=['name:endmeteor'])
		next(parser.stream)

		ctx_ref = nodes.ContextReference()

		return nodes.CallBlock(
			self.call_method('_template', args=[ctx_ref, tname, filepath]), [], [], body).\
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
							value = ""
						elif token.value == ".":
							value = "#"
						else:
							value = token.value

						add_data(nodes.TemplateData("{{" + value,
													lineno=token.lineno))
						next(parser.stream)
						expression = process_args(parser, 'variable_end')
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

	def _template(self, ctx, tname, filepath, caller=None):
		"""Helper callback."""

		devmod = ctx.get("developer_mode")
		source = caller()
		if devmod:
			template = STARTTEMPLATE_SUB_ALL.sub(self.highlight(filepath), source)
		else:
			template = """%s""" % (source)

		return Markup(template.strip())

	def highlight(self, filepath):
		print "parser calls 4 {}".format(filepath)
		filepath = filepath or ""
		def _highlight(m):
			name = m.group(2)
			content = m.group(4)
			attrs = m.group(3)
			template =\
			"""<template name='%s'%s>\n\t<div class="{{ highlight '%s' }}" path='%s'>\n\t%s\n\t</div>\n</template>
			""" % (name, attrs, name, filepath, content)
			return template
		return _highlight

"""
def _subparse(self, parser, expr_tokens, end_tokens=None):
		body = []
		data_buffer = []
		add_data = data_buffer.append

		#expr_tokens_str = ",".join(expr_tokens)
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
				elif token.type == 'variable_begin':# or token.type == 'comment_begin':
					next(parser.stream)
					token = parser.stream.current
					if token.test_any(*expr_tokens):# or token.value in ("else",):
						if token.value == "%":
							value = ""
						elif token.value == ".":
							value = "#"
						else:
							value = token.value

						add_data(nodes.TemplateData("{{" + value,
													lineno=token.lineno))
						next(parser.stream)
						expression = process_args(parser, 'variable_end')
						token = parser.stream.current
						add_data(nodes.TemplateData(" ".join([unicode(expr) for expr in expression]),
								lineno=token.lineno))

						print "token current stream 19 {}".format(token.type)
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


"""

"""
def process_args_old(parser, blocktype):
	expression = []
	stream = parser.stream

	token = stream.current

	while not token.type == blocktype:
		if stream.current.test('string'):
			t = stream.next()
			expression.append("'%s'" % t.value)
			token = stream.current
		elif stream.current.test('name') and stream.look().test('assign'):
			token = stream.next()
			name = "%s" % token.value
			stream.skip()
			name = name + "="
			if stream.current.test('string'):
				value = parser.parse_expression()
				name = name + "'%s'" % value.value
			else:
				value = parser.parse_expression()
				name = name + "%s" % value.value

			expression.append(name)
			token = stream.current

		elif stream.current.test('name') and stream.look().test('dot'):
			token = stream.next()
			name = "%s" % token.value
			name = name + "."
			stream.skip()
			vv = stream.next().value
			name = name + "%s" % vv
			expression.append(name)
			token = stream.current

		elif stream.current.test('name'):
			t = stream.next()
			expression.append("%s" % t.value)
			token = stream.current
		else:
			t = stream.next()
			expression.append(t.value)
			token = stream.current

	return expression
"""


"""
class MeteorTemplate_old(Extension):
	# a set of names that trigger the extension.
	tags = set(['template'])

	def __init__(self, environment):
		super(MeteorTemplate_old, self).__init__(environment)

	def parse(self, parser):
		# the first token is the token that started the tag.  In our case
		# we only listen to ``'cache'`` so this will be a name token with
		# `cache` as value.  We get the line number so that we can give
		# that line number to the nodes we create by hand.
		lineno = parser.stream.next().lineno

		# now we parse a single expression that is used as cache key.

		if not parser.stream.current.test('block_end'):
			if parser.stream.current.type == 'name':
				name = parser.stream.expect('name')
				if name.value != 'name':
					parser.fail('found %r, "name" expected' %
								name.value, name.lineno,
								exc=TemplateAssertionError)

				if parser.stream.current.type == 'assign':
						parser.stream.next()
						args = [parser.parse_expression()]
				else:
					var = parser.stream.current
					parser.fail('assignment expected after the name' %
								var.value, var.lineno,
								exc=TemplateAssertionError)
			else:
				args = [nodes.Const(None)]
		else:
			args = [nodes.Const(None)]

		body = parser.parse_statements(['name:endtemplate'], drop_needle=True)

		return nodes.CallBlock(self.call_method('_cache_support', args),
							[], [], body).set_lineno(lineno)
"""

	#def _cache_support(self, name, caller=None):
	#	"""Helper callback."""
	#	template = """{%% block %s %%}
	#		<template name='%s'>
	#			%s
	#		</template>
	#	{%% endblock %%}""" % (name, name, caller())
	#	return template
