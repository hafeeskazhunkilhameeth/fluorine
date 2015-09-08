# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'


def get_context(context, ctx, whatfor):
	return


def get_files_folders(context, whatfor):

	folder = "%s/common" % whatfor

	return {
		"OUT":{
			"files_folders":{
				"all":{
					"add":[{"folder":folder}]
				}
			}
		}
	}

def get_apps(context, whatfor):
	return

