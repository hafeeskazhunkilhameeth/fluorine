# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'


import frappe, os
from pymongo import MongoClient

def set_frappe_users(host, port, db_name):

	host = host.replace("http://", "")
	client = MongoClient(host, port)
	db = client[db_name]
	db.drop_collection("fUsers")

	frappe_users = []
	users = frappe.db.sql("""select `user`, `password` from __Auth""", debug=0)
	for user in users:
		frappe_users.append({"username": user[0],
		"password": user[1]
		})
		print "call of mongodb_conf username {} password {}".format(user[0], user[1])

	fUsers = db.fUsers
	fUsers.insert_many(frappe_users)


def is_mongodb_ready(common_file):

	mongodb_users = common_file.get("mongodb_users_ready", 0)
	return mongodb_users


def save_mongodb_config(common_config):
	from fluorine.utils.file import get_path_reactivity, save_js_file

	path_reactivity = get_path_reactivity()
	common_config_file = os.path.join(path_reactivity, "common_site_config.json")
	save_js_file(common_config_file, common_config)

