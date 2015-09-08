# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'


def get_context(context, ctx, whatfor):
	highlight = []

	if not context.developer_mode:
		highlight.append({"appname": "fluorine", "action": "remove", "pattern": "highlight/.*"})

	highlight.append({"appname":"fluorine", "action":"add", "pattern":"login/.*"})

	return highlight


def get_files_folders(context, whatfor):

	return {
		"IN":{
		  "files_folders":{
			  "fluorine":{
				  "remove":[{"folder":"meteor_web/common"}]
			  }
		  }
		}
	}

def get_apps(context, whatfor):
	return {
		"IN":{
		  "apps": {
			"ekaiser":{
			  "remove": 0
			}
		  }
		}
	}