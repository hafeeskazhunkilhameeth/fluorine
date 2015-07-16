# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'


from jinja2 import nodes
from jinja2.ext import Extension, TemplateAssertionError


class MeteorElseExpression(Extension):
	# a set of names that trigger the extension.
	tags = set(['melse'])

	def __init__(self, environment):
		super(MeteorElseExpression, self).__init__(environment)

	def parse(self, parser):
		# the first token is the token that started the tag.  In our case
		# we only listen to ``'cache'`` so this will be a name token with
		# `cache` as value.  We get the line number so that we can give
		# that line number to the nodes we create by hand.
		stream = parser.stream
		tag = stream.next()

		name_tag = nodes.Const(tag.value)

		def make_call_node(*kw):
			return self.call_method('_cache_support', args=[
				name_tag,
			], kwargs=kw)

		return nodes.Output([make_call_node()]).set_lineno(tag.lineno)

	def _cache_support(self, tag):
		"""Helper callback."""
		mexpr = "{{%s}}" % tag[1:]

		print "helper function args 8 {} args {}".format(mexpr, tag)

		return mexpr


class MeteorEndExpression(Extension):
	# a set of names that trigger the extension.
	tags = set(['endmif', 'endmeach', 'endmunless', 'endmwith'])

	def __init__(self, environment):
		super(MeteorEndExpression, self).__init__(environment)

	def parse(self, parser):
		# the first token is the token that started the tag.  In our case
		# we only listen to ``'cache'`` so this will be a name token with
		# `cache` as value.  We get the line number so that we can give
		# that line number to the nodes we create by hand.
		stream = parser.stream
		tag = stream.next()

		name_tag = nodes.Const(tag.value)

		def make_call_node(*kw):
			return self.call_method('_cache_support', args=[
				name_tag,
			], kwargs=kw)

		return nodes.Output([make_call_node()]).set_lineno(tag.lineno)

	def _cache_support(self, tag):
		"""Helper callback."""
		if tag == "endtemplate":
			mexpr = "</%s>" % tag[3:]
		else:
			mexpr = "{{/%s}}" % tag[4:]

		print "helper function args 8 {} args {}".format(mexpr, tag)

		return mexpr


def process_args(parser, blocktype):
	expression = []
	stream = parser.stream

	#while not stream.current.test('block_end'):
	token = stream.current

	while not token.type == blocktype:#"variable_end" or not token.type == 'block_end':
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


	print "token current stream 21 {}".format(stream.current.type)
	"""
	elif stream.current.test('lbracket'):
		stream.skip()
		expression.append("[")
	elif stream.current.test('rbracket'):
		stream.skip()
		expression.append("]")
	elif stream.current.test('lbrace'):
		stream.skip()
		expression.append("{")
	elif stream.current.test('rbrace'):
		stream.skip()
		expression.append("}")
	"""

	return expression


class MeteorTemplate(Extension):
	# a set of names that trigger the extension.
	tags = set(['template'])

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
		expression = process_args(parser, 'block_end')

		print "args of template {}".format(expression)

		expressions = nodes.Const(" ".join(expression))
		#name_tag = nodes.Const(tag.value)

		stream.skip_if('colon')
		stream.expect('block_end')
		body = self._subparse(parser, ["gt"], ['name:endtemplate'])
		next(parser.stream)

		return nodes.CallBlock(
			self.call_method('_cache_support', args=[expressions]), [], [], body).\
				set_lineno(tag.lineno)


	def _subparse(self, parser, expr_tokens, end_tokens=None):
		body = []
		data_buffer = []
		add_data = data_buffer.append

		expr_tokens_str = ",".join(expr_tokens)
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
					if token.test_any(expr_tokens_str):
						add_data(nodes.TemplateData("{{" + token.value,
													lineno=token.lineno))
						next(parser.stream)
						token = parser.stream.current
						#while not token.type == "variable_end":
						expression = process_args(parser, 'variable_end')
						#if expression:
						token = parser.stream.current
						add_data(nodes.TemplateData(" ".join(expression),
								lineno=token.lineno))
						#else:
						#	add_data(nodes.TemplateData(token.value,
						#			lineno=token.lineno))
						#next(parser.stream)
						#token = parser.stream.current

						print "token current stream 19 {}".format(token.type)
						add_data(nodes.TemplateData("}}",
									lineno=token.lineno))

						#token = parser.stream.current
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

	def _cache_support(self, expressions, caller=None):
		"""Helper callback."""

		template = """<template %s>
				%s
			</template>""" % (expressions, caller())
		return template


class MeteorStartExpression(Extension):
	# a set of names that trigger the extension.
	tags = set(['mif', 'meach', 'munless', 'mwith'])

	def __init__(self, environment):
		super(MeteorStartExpression, self).__init__(environment)

	def parse(self, parser):
		# the first token is the token that started the tag.  In our case
		# we only listen to ``'cache'`` so this will be a name token with
		# `cache` as value.  We get the line number so that we can give
		# that line number to the nodes we create by hand.
		stream = parser.stream
		tag = stream.next()

		# now we parse a single expression that is used as cache key.

		expression = process_args(parser)

		expressions = nodes.Const(" ".join(expression))
		name_tag = nodes.Const(tag.value)

		def make_call_node(*kw):
			return self.call_method('_cache_support', args=[
				name_tag,
				expressions,
			], kwargs=kw)

		return nodes.Output([make_call_node()]).set_lineno(tag.lineno)

	def _cache_support(self, tag, expressions):
		"""Helper callback."""
		if tag == "template":
			mexpr = "<%s %s>" % (tag, expressions)
		else:
			mexpr = "{{#%s %s}}" % (tag[1:], expressions)

		return mexpr


"""
def _subparse(self, parser, expr_tokens, end_tokens=None):
		body = []
		data_buffer = []
		add_data = data_buffer.append

		expr_tokens_str = ",".join(expr_tokens)
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
					if token.test_any(expr_tokens_str):
						add_data(nodes.TemplateData("{{" + token.value,
													lineno=token.lineno))
						next(parser.stream)
						token = parser.stream.current
						while not token.type == "variable_end":
							expression = process_args(parser)
							if expression:
								add_data(nodes.TemplateData(" ".join(expression),
										lineno=token.lineno))
							else:
								add_data(nodes.TemplateData(token.value,
										lineno=token.lineno))
							next(parser.stream)
							#if token.type == 'name':
							#	name = parser.stream.expect('name')
							#	add_data(nodes.TemplateData(name.value,
							#			lineno=token.lineno))
							#else:
							#	add_data(nodes.TemplateData(token.value,
							#			lineno=token.lineno))
							#	next(parser.stream)
							token = parser.stream.current


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
