__author__ = 'luissaguas'

import frappe
from bench_helpers import *
from fluorine.utils import meteor_desk_app, meteor_web_app

class FluorineError(Exception):
	def __init__(self, message):
		super(FluorineError, self).__init__(message)


def check_prod_mode():
	from fluorine.utils.reactivity import meteor_config

	prod_mode = meteor_config.get("production_mode")

	return prod_mode


def get_hosts(doc, production=False):
	from fluorine.utils import get_attr_from_json
	from fluorine.utils.meteor.utils import PORT
	from fluorine.utils.file import get_path_reactivity
	import re

	#CONFIG FILE
	path_reactivity = get_path_reactivity()
	meteor_config = frappe.get_file_json(os.path.join(path_reactivity, "common_site_config.json"))

	meteor_config.get("")

	meteor_dns = meteor_config.get("meteor_dns")
	hosts_web = []
	hosts_app = []

	#meteor_dev = meteor_config.get("meteor_dev") or {}
	#meteor_web = meteor_dev.get(meteor_web_app) or {}
	#meteor_web = get_attr_from_json(["meteor_dev", meteor_web_app], meteor_config)
	use_web_in_production = get_attr_from_json(["meteor_dev", meteor_web_app, "production"], meteor_config)#meteor_web.get("production")

	#meteor_desk = meteor_dev.get(meteor_desk_app) or {}
	#meteor_desk = get_attr_from_json(["meteor_dev", meteor_desk_app], meteor_config)
	use_desk_in_production = get_attr_from_json(["meteor_dev", meteor_desk_app, "production"], meteor_config)#meteor_desk.get("production")
	#remove :port only have meanning in ROOT_URL environment variable
	meteor_root_url = doc.fluor_meteor_host.strip()
	if len(re.findall(":", meteor_root_url)) > 1:
		meteor_root_url = meteor_root_url.rsplit(":",1)[0]
	mthost = meteor_root_url.replace("http://", "") or "127.0.0.1"
	port = doc.fluor_meteor_port or PORT.meteor_web

	if use_web_in_production or not production:
		hosts_web.append("%s:%s" % (mthost, port))
	if use_desk_in_production or not production:
		hosts_app.append("%s:%s" % (mthost, PORT.meteor_app))

	#add others meteors
	if meteor_dns and production:
		meteor_web = meteor_dns.get(meteor_web_app)
		for obj in meteor_web:
			hosts_web.append("%s:%s" % (obj.get("host").replace("http://", ""), obj.get("port")))

		meteor_app = meteor_dns.get(meteor_desk_app)
		for obj in meteor_app:
			hosts_app.append("%s:%s" % (obj.get("host").replace("http://", ""), obj.get("port")))

	return hosts_web, hosts_app


def start_frappe_db(site):
	if not frappe.db:
		frappe.init(site=site)
		frappe.connect()


def get_doctype(name, site):

	start_frappe_db(site)
	doc = frappe.get_doc(name)

	return doc


def get_default_site():
	from fluorine.utils import meteor_config

	site = meteor_config.get("site")
	if not site:
		try:
			with open("currentsite.txt") as f:
				site = f.read().strip()
		except IOError:
			frappe.throw("There is no default site. Check if reactivity/common_site_config.json for site option or if sites/currentsite.txt exist or provide the site with --site option.")

	return site
