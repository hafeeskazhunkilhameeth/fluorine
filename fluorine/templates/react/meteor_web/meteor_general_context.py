# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'

import os

def get_context(context, ctx, whatfor):
	highlight = []

	if not context.developer_mode:
		highlight.append({"appname": "fluorine", "action": "remove", "pattern": "highlight/.*"})

	highlight.append({"appname":"fluorine", "action":"add", "pattern":"login/.*"})

	return highlight
