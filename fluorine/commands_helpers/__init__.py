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

	#CONFIG FILE
	path_reactivity = get_path_reactivity()
	meteor_config = frappe.get_file_json(os.path.join(path_reactivity, "common_site_config.json"))

	meteor_config.get("")

	meteor_dns = meteor_config.get("meteor_dns")
	hosts_web = []
	hosts_app = []

	use_web_in_production = get_attr_from_json(["meteor_dev", meteor_web_app, "production"], meteor_config)

	use_desk_in_production = get_attr_from_json(["meteor_dev", meteor_desk_app, "production"], meteor_config)
	#remove :port only have meanning in ROOT_URL environment variable
	mthost = get_host_address(doc).replace("http://", "").replace("https://", "")

	port = doc.fluor_meteor_port or PORT.get(meteor_web_app)

	if use_web_in_production or not production:
		hosts_web.append("%s:%s" % (mthost, port))
	if use_desk_in_production or not production:
		hosts_app.append("%s:%s" % (mthost, PORT.get(meteor_desk_app)))

	#add others meteors
	if meteor_dns and production:
		meteor_web = meteor_dns.get(meteor_web_app)
		for obj in meteor_web:
			hosts_web.append("%s:%s" % (obj.get("host").replace("http://", "").replace("https://", ""), obj.get("port")))

		meteor_app = meteor_dns.get(meteor_desk_app)
		for obj in meteor_app:
			hosts_app.append("%s:%s" % (obj.get("host").replace("http://", "").replace("https://", ""), obj.get("port")))

	return hosts_web, hosts_app


def get_address(url, default="http://127.0.0.1"):
	import re

	if len(re.findall(":", url)) > 1:
		url = url.rsplit(":",1)[0]
	addr = url or default

	return addr

def get_host_address(doc):

	meteor_root_url = doc.fluor_meteor_host.strip()

	mthost = get_address(meteor_root_url)

	return mthost

def get_ddp_address(doc):

	meteor_ddp_url = doc.ddpurl.strip()

	mtddp = get_address(meteor_ddp_url)

	return mtddp

def stop_frappe_db():
	if frappe.db:
		frappe.db.commit()
		frappe.destroy()


def start_frappe_db(site):
	if not frappe.db:
		frappe.init(site=site)
		frappe.connect()


def change_frappe_db(site):
	stop_frappe_db()
	start_frappe_db(site)


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


def get_app_installed_site(app="fluorine"):
	from fluorine.utils import get_list_sites
	fluorine_site = None

	sites = get_list_sites()

	for site in sites:
		change_frappe_db(site)
		if app in frappe.get_installed_apps():
			fluorine_site = site
			break

	return fluorine_site


def get_current_dev_app():
	from fluorine.utils.reactivity import meteor_config
	import click

	current_dev_app = meteor_config.get("current_dev_app", None)
	if not current_dev_app:
		from fluorine.commands_helpers.meteor import get_active_apps
		apps = get_active_apps()
		if len(apps) > 1:
			click.echo("Please you must set the current_dev_app in reactivity/common_site_config.json to continue.")
			return
		else:
			current_dev_app = apps[0]

	return current_dev_app
