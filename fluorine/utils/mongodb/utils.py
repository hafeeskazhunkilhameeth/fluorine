# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'

import frappe, os


def set_frappe_users(host, port, db_name):
	from pymongo import MongoClient

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


def make_mongodb_default(conf, port=3070):
	from fluorine.utils import meteor_web_app, is_open_port

	if is_open_port(port=port):
		frappe.throw("port {} is open, please close. If you change from production then stop supervisor (sudo supervisorctl stop all).".format(port))
		return
	if not conf.get("meteor_mongo"):
		import subprocess
		from fluorine.utils import file

		path_reactivity = file.get_path_reactivity()
		meteor_web = os.path.join(path_reactivity, meteor_web_app)
		print "getting mongo config please wait..."

		mongodb = None

		meteor = subprocess.Popen(["meteor", "--port", str(port)], cwd=meteor_web, shell=False, stdout=subprocess.PIPE)
		while True:
			line = meteor.stdout.readline()
			if "App running at" in line:
				mongodb = subprocess.check_output(["meteor", "mongo", "-U"], cwd=meteor_web, shell=False)
				meteor.terminate()
				break
			elif "Error" in line:
				mongodb = subprocess.check_output(["meteor", "mongo", "-U"], cwd=meteor_web, shell=False)
				meteor.terminate()
				break
				#print line

		print "meteor mongo -U {}".format(mongodb)
		if mongodb:
			fs = mongodb.rsplit("/",1)
			hp = fs[0].split("mongodb://")[1].split(":")
			db = fs[1].rstrip() or "fluorine"
			host = hp[0]
			port = hp[1]

			conf["meteor_mongo"] = {
				"host": host,
				"port": port,
				"db": db,
				"type": "default"
			}

def get_mongo_exports(doc):
	from fluorine.utils.reactivity import meteor_config

	mongo_default = False
	if doc.check_mongodb and doc.fluor_mongo_host.strip():
		user_pass = "%s:%s@" % (doc.mongo_user, doc.mongo_pass) if doc.mongo_user and doc.mongo_pass else ''
		mghost = doc.fluor_mongo_host.replace("http://","").replace("mongodb://","").strip(' \t\n\r')
		export_mongo = "export MONGO_URL=mongodb://%s%s:%s/%s " % (user_pass, mghost, doc.fluor_mongo_port, doc.fluor_mongo_database)
	else:
		mongo_conf = meteor_config.get("meteor_mongo")
		db = mongo_conf.get("db") or "fluorine"
		port = mongo_conf.get("port") or 27017
		host = mongo_conf.get("host") or "127.0.0.1"
		export_mongo = "export MONGO_URL=mongodb://%s:%s/%s " % (host.replace("http://","").replace("mongodb://","").strip(' \t\n\r'), port, db)
		mongo_default = True

	return export_mongo, mongo_default
