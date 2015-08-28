__author__ = 'luissaguas'

import frappe
from bench_helpers import *


class FluorineError(Exception):
	def __init__(self, message):
		super(FluorineError, self).__init__(message)


def check_prod_mode():
	from fluorine.utils.reactivity import meteor_config

	prod_mode = meteor_config.get("production_mode")

	return prod_mode


def get_hosts(doc, production=False):
	from fluorine.utils.meteor.utils import default_path_prefix, PORT
	from fluorine.utils.file import get_path_reactivity

	#CONFIG FILE
	path_reactivity = get_path_reactivity()
	meteor_config = frappe.get_file_json(os.path.join(path_reactivity, "common_site_config.json"))

	meteor_dns = meteor_config.get("meteor_dns")
	hosts_web = []
	hosts_app = []
	if meteor_dns and production==True:
		meteor_web = meteor_dns.get("meteor_web")
		for obj in meteor_web:
			hosts_web.append("%s:%s" % (obj.get("host").replace("http://", ""), obj.get("port")))

		meteor_app = meteor_dns.get("meteor_app")
		for obj in meteor_app:
			hosts_app.append("%s:%s" % (obj.get("host").replace("http://", ""), obj.get("port")))
	else:
		mthost = doc.fluor_meteor_host.strip().replace("http://", "") or "127.0.0.1"
		port = doc.fluor_meteor_port or PORT.meteor_web
		hosts_web.append("%s:%s" % (mthost, port))
		hosts_app.append("%s:%s" % (mthost, PORT.meteor_app))

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

"""
def get_default_site():
	import click

	try:
		with open("currentsite.txt") as f:
			site = f.read().strip()
			return site
	except IOError:
		click.echo("There is no default site. Check if sites/currentsite.txt exist or provide the site with --site option.")
"""