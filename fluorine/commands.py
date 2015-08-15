from __future__ import unicode_literals, absolute_import
__author__ = 'luissaguas'


import frappe
import click


@click.command('setState')
@click.argument('site')
@click.option('--state', default="start", help='Use start|stop|production to start, stop or set meteor in production mode.')
def setState(site, state=None):
	"""Prepare Frappe for meteor."""
	if not frappe.db:
		frappe.init(site=site)
		frappe.connect()

	doc = frappe.get_doc("Fluorine Reactivity")
	devmode = doc.fluor_dev_mode
	fluor_state = doc.fluorine_state
	print "state {} fluor_state {}".format(state, fluor_state)
	what = state.lower()
	if what == "start":
		start_meteor(doc, devmode, fluor_state)
	elif what == "stop":
		stop_meteor(doc, devmode, fluor_state)
	elif what == "production":
		start_meteor_production_mode(doc, devmode, fluor_state)


def start_meteor(doc, devmode, state):
	from fluorine.utils.fhooks import change_base_template

	if devmode and state == "on":
		if doc.fluorine_base_template and doc.fluorine_base_template.lower() != "default":
			pass

		change_base_template(page_default=False)

def stop_meteor(doc, devmode, state):
	from fluorine.utils.fhooks import change_base_template

	if state == "off":
		change_base_template(page_default=True)

def start_meteor_production_mode(doc, devmode, state):
	from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import make_meteor_file

	if state == "off":
		make_meteor_file(doc.fluor_meteor_host, doc.fluor_meteor_port, doc.ddpurl, doc.meteor_target_arch, doc.fluorine_reactivity)
		#Patch: run twice for fix nemo64:bootstrap less problem
		print "Run twice to patch nemo64:bootstrap less problem"
		make_meteor_file(doc.fluor_meteor_host, doc.fluor_meteor_port, doc.ddpurl, doc.meteor_target_arch, doc.fluorine_reactivity)
		stop_meteor(doc, devmode, state)


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
@click.option('--hosts_web', default=["127.0.0.1:3000"], help='Hosts name or ip with port.')
@click.option('--hosts_app', default=["127.0.0.1:3080"], help='Hosts name or ip with port.')
@click.option('--meteor_port', default=3000, help='Port where meteor is listen.')
@click.option('--production', default=False, help='production True or False.')
def nginx_conf(hosts_web=None, hosts_app=None, meteor_port=None, production=None):
	"""make config file for meteor.
		Make config file for nginx with meteor support.
	"""
	from fluorine.utils.file import save_file, readlines
	import os, subprocess, re

	config_path = os.path.join(os.path.abspath(".."), "config")
	config_file = os.path.join(config_path, "nginx.conf")
	if not os.path.exists(config_file):
		p = subprocess.Popen(["bench", "setup", "nginx"], cwd=os.path.abspath(".."))
		p.wait()

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
	save_file(os.path.join(config_path, "meteor_nginx.conf"), "\n".join(ll))


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



commands = [
	mongodb_conf,
	nginx_conf,
	setState
]