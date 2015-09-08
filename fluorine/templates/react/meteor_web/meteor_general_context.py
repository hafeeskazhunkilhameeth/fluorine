# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'


def get_context(context, ctx):
	highlight = []

	#if not context.developer_mode:
	#	highlight.append({"appname": "fluorine", "action": "remove", "pattern": "highlight/.*"})

	#highlight.append({"appname":"fluorine", "action":"add", "pattern":"login/.*"})

	return highlight


def get_files_folders(context):

	remove = []

	if not context.developer_mode:
		pattern = "highlight.xhtml"
		remove.append({"file":pattern})

	return {
		"IN":{
			"files_folders":{
				"fluorine":{
					"remove":remove
				}
			}
		}
	}

def get_apps(context):
	return {
		"IN":{
		  "apps": {
			"ekaiser":{
			  "remove": 0
			}
		  }
		}
	}

