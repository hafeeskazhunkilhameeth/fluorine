from __future__ import unicode_literals, absolute_import
__author__ = 'luissaguas'


import frappe
import click
import os


class FluorineError(Exception):
	def __init__(self, message):
		super(FluorineError, self).__init__(message)


def run_bench_module(module, func, *args, **kwargs):
	cwd = os.getcwd()
	os.chdir("../")
	f = getattr(module, func)
	res = f(*args, **kwargs)
	os.chdir(cwd)

	return res


def get_bench_module(module):
	import sys, importlib
	bench_path = os.path.abspath("../../bench-repo/")
	sys.path.append(bench_path)
	m = importlib.import_module("bench." + module)

	return m


@click.command('setState')
@click.option('--site', default=None, help='The site to work with. If not provided it will use the currentsite')
@click.option('--state', default="start", help='Use start|stop|production to start, stop or set meteor in production mode.')
@click.option('--debug', is_flag=True)
def setState(site=None, state=None, debug=None):
	"""Prepare Frappe for meteor."""
	_setState(site=site, state=state, debug=debug)

def _setState(site=None, state=None, debug=False):

	if site == None:
		try:
			with open("currentsite.txt") as f:
				site = f.read().strip()
		except IOError:
			click.echo("There is no default site. Check if sites/currentsite.txt exist or provide the site with --site option.")

	if not frappe.db:
		frappe.init(site=site)
		frappe.connect()

	doc = frappe.get_doc("Fluorine Reactivity")
	devmode = doc.fluor_dev_mode
	fluor_state = doc.fluorine_state
	what = state.lower()
	if what == "start":
		start_meteor(doc, devmode, fluor_state)
	elif what == "stop":
		stop_meteor(doc, devmode, fluor_state)
	elif what == "production":
		import sys
		start_meteor_production_mode(doc, devmode, fluor_state, debug=debug)
		m = get_bench_module("config")
		run_bench_module(m, "generate_nginx_config")


def start_meteor(doc, devmode, state):
	from fluorine.utils.fhooks import change_base_template, remove_hook_app_include
	from fluorine.utils.file import save_custom_template
	from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import save_to_procfile

	if devmode and state == "on":
		save_to_procfile(doc)
		if doc.fluorine_base_template and doc.fluorine_base_template.lower() != "default":
			save_custom_template(doc.fluorine_base_template)

		change_base_template(page_default=False)
		remove_hook_app_include()
	else:
		click.echo("You must set state to on and activate developer mode in fluorine doctype.")


def stop_meteor(doc, devmode, state):
	from fluorine.utils.fhooks import change_base_template, remove_hook_app_include
	from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import remove_from_procfile

	if state == "off":
		remove_from_procfile()
		change_base_template(page_default=True)
		remove_hook_app_include()
	else:
		click.echo("You must set state to off in fluorine doctype.")


def start_meteor_production_mode(doc, devmode, state, debug=False):
	from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import make_meteor_file
	from fluorine.utils.fhooks import hook_app_include

	if state == "off":
		#If debug then do not run frappe setup production and test only meteor in production mode.
		click.echo("Make meteor bundle for Desk APP")
		#make_meteor_file(doc.fluor_meteor_host, doc.fluor_meteor_port, doc.ddpurl, doc.meteor_target_arch, doc.fluorine_reactivity)
		#Patch: run twice for fix nemo64:bootstrap less problem
		print "Run twice to patch nemo64:bootstrap less problem"
		click.echo("Make meteor bundle for WEB")
		#make_meteor_file(doc.fluor_meteor_host, doc.fluor_meteor_port, doc.ddpurl, doc.meteor_target_arch, doc.fluorine_reactivity)
		click.echo("Run npm install for meteor server:")
		run_npm()
		stop_meteor(doc, devmode, state)
		click.echo("Make production links.")
		make_production_link()
		click.echo("Make js and css hooks.")
		app_include_js, app_include_css = get_meteor_app_files()
		hook_app_include(app_include_js, app_include_css)

		#common_site_config.json must have meteor_dns for production mode or use default
		make_nginx_conf_file(doc)

		if not debug:
			click.echo("Run frappe setup production.")
			make_supervisor(doc)


	else:
		click.echo("You must set state to off in fluorine doctype.")


def make_nginx_conf_file(doc):
	from fluorine.utils.meteor.utils import default_path_prefix, PORT
	from fluorine.utils.file import get_path_reactivity

	#CONFIG FILE
	path_reactivity = get_path_reactivity()
	meteor_config = frappe.get_file_json(os.path.join(path_reactivity, "common_site_config.json"))

	meteor_dns = meteor_config.get("meteor_dns")
	hosts_web = []
	hosts_app = []
	if meteor_dns:
		meteor_web = meteor_dns.get("meteor_web")
		for obj in meteor_web:
			hosts_web.append(["%s:%s" % (obj.get("host"), obj.get("port"))])

		meteor_app = meteor_dns.get("meteor_app")
		for obj in meteor_app:
			hosts_app.append(["%s:%s" % (obj.get("host"), obj.get("port"))])
	else:
		mthost = doc.fluor_meteor_host.strip() or "http://127.0.0.1"
		port = doc.fluor_meteor_port or PORT.meteor_web
		hosts_web.append(["%s:%s" % (mthost, port)])
		hosts_app.append(["%s:%s" % (mthost, PORT.meteor_app)])

	_generate_nginx_conf(hosts_web=hosts_web, hosts_app=hosts_app, production=True)

def make_supervisor(doc):
	import getpass
	from fluorine.utils.file import writelines, readlines, get_path_reactivity

	#m = get_bench_module("production_setup")
	#run_bench_module(m, "setup_production")

	#TODO REMOVE
	m = get_bench_module("config")
	run_bench_module(m, "generate_supervisor_config")

	conf = frappe._dict()
	conf.user = getpass.getuser()
	conf.bench_dir = os.path.abspath("..")
	#sites_dir = os.path.abspath(".")
	config_path = os.path.join(conf.bench_dir, "config")
	config_file = os.path.join(config_path, 'supervisor.conf')
	content = readlines(config_file)
	content.append("\n")
	path_reactivity = get_path_reactivity()

	for final in ("final_app", "final_web"):
		conf.meteorenv = get_meteor_environment(doc, final.replace("final", "meteor"))
		conf.progname = "meteor_" + final
		conf.final_server_path = os.path.join(path_reactivity, final, "bundle")
		content.extend(supervisor_meteor_conf.format(**conf))
		#final_web_path = os.path.join(path_reactivity, "final_web", "bundle")
		#conf.final_server_path = final_app_path

	writelines(config_file, content)


def get_meteor_environment(doc, whatfor):
	from fluorine.utils.meteor.utils import default_path_prefix, PORT
	from fluorine.utils.file import get_path_reactivity

	conf = frappe._dict()

	#CONFIG FILE
	path_reactivity = get_path_reactivity()
	meteor_config = frappe.get_file_json(os.path.join(path_reactivity, "common_site_config.json"))

	#METEOR MAIL
	if hasattr(doc, "mailurl"):
		conf.mail_url = ", MAIL_URL='{mail_url}'".format(doc.mailurl)
	else:
		conf.mail_url = ""

	#MONGODB
	mongodb_conf = meteor_config.get("meteor_mongo")
	if mongodb_conf and mongodb_conf.get("type") != "default":
		user_pass = "%s:%s@" % (doc.mongo_user, doc.mongo_pass) if doc.mongo_user and doc.mongo_pass else ''
		mghost = doc.fluor_mongo_host.replace("http://","").replace("mongodb://","").strip(' \t\n\r')
		mgport = doc.fluor_mongo_port
		dbname = doc.fluor_mongo_database
	else:
		user_pass = ''
		mghost = "127.0.0.1"
		mgport = 27017
		dbname = "fluorine"

	conf.mongo_url = "mongodb://{user_pass}{host}:{port}/{databasename}".format(user_pass=user_pass, host=mghost, port=mgport, databasename=dbname)

	#METEOR
	mthost = doc.fluor_meteor_host.strip() or "http://127.0.0.1"
	port = doc.fluor_meteor_port or PORT.meteor_web
	conf.port = port if whatfor == "meteor_web" else PORT.meteor_app
	default_prefix = default_path_prefix if whatfor=="meteor_app" else ""
	meteor_dev = meteor_config.get("meteor_dev", None)
	meteor = meteor_dev.get(whatfor)
	prefix = meteor.get("ROOT_URL_PATH_PREFIX") or ""
	conf.root_url = mthost + (prefix if prefix else default_prefix)

	#NGINX
	count = meteor_config.get("meteor_http_forwarded_count") or "1"
	conf.forwarded_count = ", HTTP_FORWARDED_COUNT='" + str(count) + "'"

	#SUPERVISOR
	env = "PORT={port}, ROOT_URL='{root_url}', MONGO_URL='{mongo_url}'{mail_url}{forwarded_count}".format(**conf)

	return env

#Run npm install for meteor server
def run_npm():
	from fluorine.utils.file import get_path_reactivity
	import subprocess

	path_reactivity = get_path_reactivity()
	final_app_path = os.path.join(path_reactivity, "final_app", "bundle", "programs", "server")
	final_web_path = os.path.join(path_reactivity, "final_web", "bundle", "programs", "server")
	click.echo("npm install meteor server Desk APP")
	subprocess.call(["npm", "install"], cwd=final_app_path)
	click.echo("npm install meteor server WEB")
	subprocess.call(["npm", "install"], cwd=final_web_path)


def make_production_link():
	from fluorine.utils.file import get_path_reactivity

	path_reactivity = get_path_reactivity()
	final_app_path = os.path.join(path_reactivity, "final_app", "bundle", "programs", "web.browser")
	meteordesk_path = os.path.join(os.path.abspath("."), "assets", "js", "meteor_app", "meteordesk")
	if os.path.exists(final_app_path) and not os.path.exists(meteordesk_path):
		frappe.create_folder(os.path.join(os.path.abspath("."), "assets", "js", "meteor_app"))
		os.symlink(final_app_path, meteordesk_path)


def get_meteor_app_files():
	from shutil import copyfile

	meteor_app_path = os.path.join(os.path.abspath("."), "assets", "js", "meteor_app")
	meteordesk_path = os.path.join(meteor_app_path, "meteordesk")
	app_include_js = []
	app_include_css = []

	if os.path.exists(meteordesk_path):
		app_include_js.append("assets/js/meteor_app/meteor_runtime_config.js")
		progfile = frappe.get_file_json(os.path.join(meteordesk_path, "program.json"))
		manifest = progfile.get("manifest")
		for obj in manifest:
			if obj.get("type") == "js" and obj.get("where") == "client":
				app_include_js.append("assets/js/meteor_app/meteordesk" + obj.get("url"))
			elif obj.get("type") == "css" and obj.get("where") == "client":
				app_include_css.append("assets/js/meteor_app/meteordesk" + obj.get("url"))

		fluorine_path = frappe.get_app_path("fluorine")
		src = os.path.join(fluorine_path, "public", "meteor_app", "meteor_runtime_config.js")
		dst = os.path.join(meteor_app_path, "meteor_runtime_config.js")
		copyfile(src, dst)

	return app_include_js, app_include_css



@click.command('mongodb-conf')
@click.argument('site')
@click.argument('db-name')
@click.argument('username')
@click.argument('password')
@click.option('--host', default='localhost', help='MongoDB Host default to localhost')
@click.option('--port', default=27017, help='MongoDB Port default to 27017')
def mongodb_conf(site, db_name, username, password, host=None, port=None):
	"""prepare Fluorine for mongodb.
		Make reset to mongodb collection fUsers and set the frappe current users.
	"""
	from fluorine.utils.mongodb.utils import set_frappe_users

	if not frappe.db:
		frappe.init(site=site)
		frappe.connect()

	set_frappe_users(host, port, db_name)


@click.command('nginx-conf')
@click.option('--hosts_web', default=["127.0.0.1:3070"], help='Hosts name or ip with port.')
@click.option('--hosts_app', default=["127.0.0.1:3080"], help='Hosts name or ip with port.')
@click.option('--production', default=False, help='production True or False.')
def nginx_conf(hosts_web=None, hosts_app=None, production=None):
	"""make config file for meteor.
		Make config file for nginx with meteor support.
	"""
	_generate_nginx_conf(hosts_web=hosts_web, hosts_app=hosts_app, production=production)


def _generate_nginx_conf(hosts_web=None, hosts_app=None, production=None):
	from fluorine.utils.file import save_file, readlines, get_path_reactivity
	import re


	#config_path = os.path.join(os.path.abspath(".."), "config")
	config_path = os.path.join(os.path.abspath(".."), "config")
	config_file = os.path.join(config_path, "nginx.conf")
	#if not os.path.exists(config_file):
	#p = subprocess.Popen(["bench", "setup", "nginx"], cwd=os.path.abspath(".."))
	#p.wait()
	m = get_bench_module("config")
	#m.generate_nginx_config()
	run_bench_module(m, "generate_nginx_config")

	frappe_nginx_file = readlines(config_file)
	inside_server = False
	inside_location = False
	inside_location_magic = False
	named_location = ""
	open_brace = 0
	new_frappe_nginx_file = []
	for line in frappe_nginx_file:
		if re.search(r"{", line):
			open_brace += 1

		if re.search(r"}", line):
			open_brace -= 1

		if re.match(r"server\s*\{", line.strip()):
			inside_server = True
			inside_location = False
		elif re.match(r"location\s*/\s*{", line.strip()):
			inside_location = True
		elif inside_server and production == False and re.match(r"root", line.strip()):
			line = [line, "\n"]
			line.extend(rewrite_for_bread)
		elif inside_location and line.strip().startswith("try_files"):
			named_location_group = re.search(r"@(.*);$", line)
			named_location = named_location_group.group(1)
			line = re.sub(r"@(.*);$", "/assets/js/meteor_web/$uri $uri @meteor;", line)
			inside_location = False
		elif re.match(r"location\s*@%s\s*{" % (named_location or "magic"), line.strip()):
			inside_location_magic = True
			if not production:
				oline = line
				location_root = new_location_root % (named_location or "magic")
				line = location_root.split("\n")
				line.append(oline)
		elif inside_location_magic and open_brace == 1 and re.search(r"}$", line):
			inside_location_magic = False
			line = [line, "\n"]
			nlocation_api = location_api % (named_location or "magic")
			lapi = nlocation_api.split("\n")
			if production:
				lapi[1] = lapi[1].replace("|^/mdesk", "")
				lapi.pop(2)
				lapi.pop(2)
			else:
				lapi.pop(4)
			line.extend(lapi)
			line.extend(location_meteordesk)
			line.extend(location_meteor)

		if open_brace == 0:
			inside_server = False
			inside_location = False


		if not isinstance(line, list):
			line = [line]
		new_frappe_nginx_file.extend(line)

	host_web = ""
	host_app = ""

	for hostw in hosts_web:
		host_web = host_web + "server " + hostw + " fail_timeout=0;\n\t"
	for hosta in hosts_app:
		host_app = host_app + "server " + hosta + " fail_timeout=0;\n\t"

	l = nginx_conf_top % (host_web, host_app)
	ll = l.split("\n")

	ll.extend(new_frappe_nginx_file)
	save_file(os.path.join(config_path, "nginx.conf"), "\n".join(ll))


def make_nginx_replace(m):
	content = m.group(1)
	print "m.group 1 {}".format(m.group(1))
	return content + "\nteste123"


nginx_conf_top = """

map $http_upgrade $connection_upgrade {
  default upgrade;
  ''      close;
}

#Load Balancing desk
upstream meteor_frappe_desk {
  ip_hash;               # this directive ensures that each unique visiting IP will always be routed to the same server.
  %s
}

#Load Balancing web
upstream meteor_frappe_web {
  ip_hash;               # this directive ensures that each unique visiting IP will always be routed to the same server.
  %s
}

"""

new_location_root = """
		#only in developer mode
		location =/ {
			try_files $uri @%s;
		}
"""

rewrite_for_bread = """
		#because we use mdesk intead of desk brand icon start with /m/assets; Only in developer mode
		rewrite ^/m/(.*)$ http://$remote_addr/$1 last;""".split("\n")

location_api = """
		location ~* "^/api|^/desk|^/mdesk|^/index$" {
			#to support flowrouter while in development
			rewrite ^/mdesk/(.*)$ http://$remote_addr/mdesk?page=$1 last;
			rewrite ^/desk/(.*)$ http://$remote_addr/desk?page=$1 last;
			try_files $uri @%s;
		}
"""


location_meteordesk = """
		location ~* "^/meteordesk" {
			proxy_pass http://meteor_frappe_desk;
			proxy_set_header X-Real-IP $remote_addr;
			proxy_set_header Host $host;
			proxy_http_version 1.1;
			# WebSocket proxying - from http://nginx.org/en/docs/http/websocket.html
			proxy_set_header Upgrade $http_upgrade;
			proxy_set_header Connection $connection_upgrade;
			proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
			proxy_redirect off;
		}
""".split("\n")


location_meteor = """
		location @meteor {
			proxy_pass http://meteor_frappe_web;
			proxy_set_header X-Real-IP $remote_addr;
			proxy_set_header Host $host;
			proxy_http_version 1.1;
			# WebSocket proxying - from http://nginx.org/en/docs/http/websocket.html
			proxy_set_header Upgrade $http_upgrade;
			proxy_set_header Connection $connection_upgrade;
			proxy_redirect off;
		}
""".split("\n")



supervisor_meteor_conf = """
[program: {progname}]
command=node main.js
autostart=true
autorestart=true
stopsignal=QUIT
stdout_logfile={bench_dir}/logs/%s.log
stderr_logfile={bench_dir}/logs/%s.error.log
user={user}
directory={final_server_path}
environment={meteorenv}
"""


commands = [
	mongodb_conf,
	nginx_conf,
	setState
]