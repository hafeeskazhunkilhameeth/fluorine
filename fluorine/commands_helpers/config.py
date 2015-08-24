__author__ = 'luissaguas'


from fluorine.commands_helpers import *



def _generate_nginx_conf(hosts_web=None, hosts_app=None, production=None):
	from fluorine.utils.file import save_file, readlines
	import re

	if not hosts_web or not hosts_app:
		site = get_default_site()
		doc = get_doctype("Fluorine Reactivity", site)

		if not hosts_web and not hosts_app:
			hosts_web, hosts_app = get_hosts(doc, production=production)
		elif not hosts_web:
			hosts_web= get_hosts(doc, production=production)
		else:
			hosts_app = get_hosts(doc, production=production)

	#config_path = os.path.join(os.path.abspath(".."), "config")
	config_path = os.path.join("..", "config")
	config_file = os.path.join(config_path, "nginx.conf")

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
			if production:
				line = re.sub(r"@(.*);$", "/assets/js/meteor_web/$uri $uri @meteor;", line)
			else:
				line = re.sub(r"@(.*);$", "$uri @meteor;", line)

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


def make_supervisor(doc):
	import getpass
	from fluorine.utils.file import writelines, readlines, get_path_reactivity
	from meteor import get_meteor_environment

	#TODO REMOVE
	#m = get_bench_module("config")
	#run_bench_module(m, "generate_supervisor_config")

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


def generate_nginx_supervisor_conf(doc, user=None, debug=None, update=False, bench="..", mac_sup_prefix_path="/usr/local"):
	from bench_helpers import bench_generate_nginx_config, bench_generate_supervisor_config, fix_prod_setup_perms,\
						bench_setup_production
	import platform, errno

	supervisor_conf_filename = "frappe.conf"

	if platform.system() == "Darwin" and not debug:
		#m = get_bench_module("config", bench=bench)
		#run_bench_module(m, "generate_nginx_config")
		bench_generate_nginx_config(bench=bench)
		#m = get_bench_module("config", bench=bench)
		#run_bench_module(m, "generate_supervisor_config", user=user)
		bench_generate_supervisor_config(bench=bench, user=user)

		sup_conf_dir = get_mac_supervisor_confdir(path=mac_sup_prefix_path)
		final_path = os.path.join(sup_conf_dir, supervisor_conf_filename)
		if not os.path.exists(final_path):
			os.symlink(os.path.abspath(os.path.join("..", 'config', 'supervisor.conf')), final_path)
		make_supervisor(doc)
	elif platform.system() != "Darwin" and not debug:
		if not update:
			try:
				bench_setup_production(user=user, bench=bench)
			except OSError as e:
				if e.errno != errno.EEXIST:
					raise
		else:
			bench_generate_supervisor_config(bench=bench, user=user)
			bench_generate_nginx_config(bench=bench)

		make_supervisor(doc)
	else:
		#m = bh.get_bench_module("config", bench=bench)
		#bh.run_bench_module(m, "generate_nginx_config")
		bench_generate_nginx_config(bench=bench)


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
		location ~* "^/api|^/desk|^/mdesk|^/index.html$" {
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
