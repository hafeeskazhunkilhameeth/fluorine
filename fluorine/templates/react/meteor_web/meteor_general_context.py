# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'

import os

def get_context(context, ctx, whatfor):
	highlight = None

	if not context.developer_mode:
		highlight = {"appname": "fluorine", "action": "remove", "pattern": "highlight/.*"}

	return highlight
