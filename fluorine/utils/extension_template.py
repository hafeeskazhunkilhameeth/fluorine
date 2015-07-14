# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'


from jinja2 import nodes
from jinja2.ext import Extension, TemplateAssertionError


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

	def _cache_support(self, name, caller=None):
		"""Helper callback."""
		template = """{%% block %s %%}
			<template name='%s'>
				%s
			</template>
		{%% endblock %%}""" % (name, name, caller())
		return template
