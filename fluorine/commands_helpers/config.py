__author__ = 'luissaguas'


from fluorine.commands_helpers import *


def get_custom_packages_files():
	from fluorine.utils.reactivity import meteor_config

	custom_packages = meteor_config.get("custom_pakages") or {}
	file_add = custom_packages.get("add") or None
	file_remove = custom_packages.get("remove") or None

	return (file_add, file_remove)


def get_frappe_config(bench='..'):
	import json

	config_path = os.path.join(bench, 'config.json')
	if not os.path.exists(config_path):
		return {}
	with open(config_path) as f:
		return json.load(f)


def _generate_fluorine_nginx_conf(hosts_web=None, hosts_app=None, production=None, site=None):
	from fluorine.utils.file import save_file, readlines
	import re

	if not hosts_web or not hosts_app:
		site = site or get_default_site()
		doc = get_doctype("Fluorine Reactivity", site)

		if not hosts_web and not hosts_app:
			hosts_web, hosts_app = get_hosts(doc, production=production)
		elif not hosts_web:
			hosts_web = get_hosts(doc, production=production)
		else:
			hosts_app = get_hosts(doc, production=production)

	config_path = os.path.join("..", "config")
	config_file = os.path.join(config_path, "nginx.conf")


	serve_default_site = get_frappe_config().get('serve_default_site')

	if serve_default_site:
		try:
			with open("currentsite.txt") as f:
				default_site_name = f.read().strip()
		except IOError:
			default_site_name = None
	else:
		default_site_name = None

	frappe_nginx_file = readlines(config_file)
	inside_server = False
	inside_location = False
	inside_location_magic = False
	named_location = ""
	open_brace = 0
	new_frappe_nginx_file = []
	is_default_site = False
	server_name = ""

	for line in frappe_nginx_file:
		if re.search(r"{", line):
			open_brace += 1

		if re.search(r"}", line):
			open_brace -= 1

		if re.match(r"server\s*\{", line.strip()):
			inside_server = True
			inside_location = False
		elif re.match(r"listen\s+", line.strip()):
			m = re.match(r"listen\s+([0-9]+)\s+(.*);", line.strip())
			is_default_site = m.group(2).strip() == "default"
		elif re.match(r"server_name\s+", line.strip()):
			m = re.match(r"server_name\s+(.*);", line.strip())
			server_name = m.group(1).strip().split()
		elif re.match(r"location\s*/\s*{", line.strip()):
			inside_location = True
		elif inside_server and re.match(r"root", line.strip()):
			line = [line, "\n"]
			line.extend(production_if_redirect.split("\n"))

		elif inside_location and line.strip().startswith("try_files"):
			named_location_group = re.search(r"@(.*);$", line)
			named_location = named_location_group.group(1)
			line = re.sub(r"@(.*);$", "/assets/js/meteor_web/$uri $uri @meteor;", line)

			inside_location = False
		elif re.match(r"location\s*@%s\s*{" % (named_location or "magic"), line.strip()):
			inside_location_magic = True
		elif inside_location_magic and open_brace == 1 and re.search(r"}$", line):
			inside_location_magic = False
			line = [line, "\n"]
			nlocation_api = location_api % (named_location or "magic", "meteor")
			lapi = nlocation_api.split("\n")
			loc_redirect = production_location_redirect.split("\n")
			line.extend(loc_redirect)
			line.extend(lapi)
			if is_default_site:
				line.extend((location_meteordesk % ("proxy_set_header X-Frappe-Site-Name %s;" % default_site_name, )).split("\n"))
				line.extend((location_meteor % ("proxy_set_header X-Frappe-Site-Name %s;" % default_site_name, )).split("\n"))
			elif len(server_name) == 1:
				line.extend((location_meteordesk % ("proxy_set_header X-Frappe-Site-Name %s;" % server_name[0], )).split("\n"))
				line.extend((location_meteor % ("proxy_set_header X-Frappe-Site-Name %s;" % server_name[0], )).split("\n"))
			else:
				line.extend((location_meteordesk % "").split("\n"))
				line.extend((location_meteor % "").split("\n"))

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

	l = nginx_conf_top % (host_app, host_web)
	ll = l.split("\n")

	ll.extend(new_frappe_nginx_file)
	save_file(config_file, "\n".join(ll))



def get_mac_supervisor_confdir(path=""):

	if path.endswith("/"):
		path = path.rsplit("/",1)[0]

	possiblities = ('%s/etc/supervisor/conf.d' % path, '%s/etc/conf.d' % path, '%s/etc/supervisor.d/' % path, '%s/etc/supervisord/conf.d' % path, '%s/etc/supervisord.d' % path)
	for possiblity in possiblities:
		if os.path.exists(possiblity):
			return possiblity

	raise Exception, 'No supervisor conf dir found.'


def make_supervisor(doc, site):
	import getpass
	from fluorine.utils.file import writelines, readlines, get_path_reactivity
	from meteor import get_meteor_environment
	from fluorine.utils.reactivity import meteor_config
	from fluorine.utils import get_meteor_final_name
	from distutils.spawn import find_executable

	nodepath = find_executable('node') or find_executable('nodejs')
	#sitename = site.replace(".","_")
	conf = frappe._dict()
	conf.user = getpass.getuser()
	conf.bench_dir = os.path.abspath("..")
	config_path = os.path.join(conf.bench_dir, "config")
	config_file = os.path.join(config_path, 'supervisor.conf')
	content = readlines(config_file)
	content.append("\n")
	path_reactivity = get_path_reactivity()

	meteor_dev = meteor_config.get("meteor_dev") or {}

	final_desk = meteor_desk_app.replace("meteor", "final")
	final_web = meteor_web_app.replace("meteor", "final")

	for final in (final_desk, final_web):
		app_name = final.replace("final", "meteor")
		meteor = meteor_dev.get(app_name) or {}
		#force meteor desk. Meteor desk must be local where frappe is installed
		if meteor.get("production") or final == final_desk:
			final_app_name = get_meteor_final_name(site, final)
			conf.meteorenv = get_meteor_environment(doc, app_name)
			conf.progname = "meteor_%s" % final_app_name
			conf.final_server_path = os.path.join(path_reactivity, final_app_name, "bundle")
			conf.nodepath = nodepath
			content.extend(supervisor_meteor_conf.format(**conf))

	writelines(config_file, content)


def generate_nginx_supervisor_conf(doc, site, user=None, debug=None, update=False, bench="..", mac_sup_prefix_path="/usr/local"):
	from bench_helpers import bench_generate_nginx_config, bench_generate_supervisor_config,\
						bench_setup_production

	import platform, errno

	supervisor_conf_filename = "frappe.conf"

	if platform.system() == "Darwin" and not debug:
		bench_generate_nginx_config(bench=bench)
		bench_generate_supervisor_config(bench=bench, user=user)

		sup_conf_dir = get_mac_supervisor_confdir(path=mac_sup_prefix_path)
		final_path = os.path.join(sup_conf_dir, supervisor_conf_filename)
		if not os.path.exists(final_path):
			os.symlink(os.path.abspath(os.path.join("..", 'config', 'supervisor.conf')), final_path)
		make_supervisor(doc, site)
	elif platform.system() != "Darwin" and not debug:

		if not update:
			#import frappe
			try:
				sup_conf_dir = get_supervisor_confdir(bench=bench)
				final_path = os.path.join(sup_conf_dir, get_supervisor_conf_filename(bench=bench))
				if not (os.path.exists(final_path) and os.path.exists('/etc/nginx/conf.d/frappe.conf')):
					#frappe.throw("Can't continue: the symlink to supervisor config file %s exist and must be remove it.\nCheck also nginx conf file /etc/nginx/conf.d/frappe.conf" % final_path)
					bench_setup_production(user=user, bench=bench)
				else:
					bench_generate_supervisor_config(bench=bench, user=user)
					bench_generate_nginx_config(bench=bench)

			except OSError as e:
				if e.errno != errno.EEXIST:
					raise
		else:
			bench_generate_supervisor_config(bench=bench, user=user)
			bench_generate_nginx_config(bench=bench)

		make_supervisor(doc, site)
	else:
		bench_generate_nginx_config(bench=bench)


supervisor_meteor_conf = """
[program: {progname}]
command={nodepath} {final_server_path}/main.js
autostart=true
autorestart=true
stopsignal=QUIT
stdout_logfile={bench_dir}/logs/{progname}.log
stderr_logfile={bench_dir}/logs/{progname}.error.log
user={user}
directory={final_server_path}
environment={meteorenv}
"""

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


log_format mainlog '$http_x_forwarded_for - $remote_user [$time_local] "$host" "$request" '
            '$status $body_bytes_sent "$http_referer" '
            '"$http_user_agent" $request_time';

"""

new_location_root = """
		#only in developer mode
		location =/ {
			try_files $uri @%s;
		}
"""

location_api = """
		location ~* "^/api|^/desk|^/index.html$" {
			#to support flowrouter while in development
			#rewrite ^/mdesk/(.*)$ http://$remote_addr/mdesk?page=$1 last;
			rewrite "^/desk/(.*)$" "http://$remote_addr/desk#$1" last;#a usar
			#rewrite ^/desk/(.*)$ "http://$remote_addr/desk#$1" last;
			try_files $uri @%s;
		}

		location /login {

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
			%s
		}
"""


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
			%s
		}
"""

production_if_redirect = """
		#fix the frappe POST to root url '/'
		set $referer 0;
		if ($request_method = POST){
			set $post 1;
		}

		if ($http_referer ~* [http://|https://](.*)/desk){
			set $referer "${post}1";
		}

		if ($referer = 11){
			rewrite ^/$ /tmp last;
		}
"""

production_location_redirect = """
		location =/tmp {
			internal;
			rewrite $uri / break;
			try_files $uri @magic;
		}
"""

#access_log /Users/saguas/erpnext4/erpnext/frappe_v5/frappe-bench/logs/nginx-access.log mainlog;