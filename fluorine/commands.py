from __future__ import unicode_literals, absolute_import
__author__ = 'luissaguas'


import frappe
import click
import os


class CommandFailedError(Exception):
	pass

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


def get_bench_module(module, bench=".."):
	import sys, importlib

	bench_path = os.path.abspath(bench)
	if bench_path not in sys.path:
		sys.path.append(bench_path)

	#print "cwd {} bench {} abs_bench {} bench_path in sys.path {}".format(os.getcwd(), bench, bench_path, bench_path in sys.path)
	m = importlib.import_module("bench." + module)

	return m


def get_doctype(name, site):

	if not frappe.db:
		frappe.init(site=site)
		frappe.connect()

	doc = frappe.get_doc(name)

	return doc

def get_default_site():

	try:
		with open("currentsite.txt") as f:
			site = f.read().strip()
			return site
	except IOError:
		click.echo("There is no default site. Check if sites/currentsite.txt exist or provide the site with --site option.")


def remove_public_link():
	from fluorine.utils.react_file_loader import remove_directory
	app_path = frappe.get_app_path("fluorine")
	public_folder = os.path.join(app_path, "public")

	for app in ("meteor_app", "meteor_web"):
		folder = os.path.join(public_folder, app)
		#if os.path.exists(folder):
		#	link_name = os.path.join(folder, "webbrowser")
		remove_directory(folder)


def make_public_link():
	#from fluorine.utils.file import get_path_reactivity

	#CONFIG FILE
	#path_reactivity = get_path_reactivity()

	app_path = frappe.get_app_path("fluorine")
	public_folder = os.path.join(app_path, "public")

	for app in ("meteor_app", "meteor_web"):
		folder = os.path.join(public_folder, app)
		if not os.path.exists(folder):
			frappe.create_folder(folder)
			#source = os.path.join(path_reactivity, app, ".meteor", "local", "build", "programs", "web.browser")
			#link_name = os.path.join(folder, "webbrowser")
			#os.symlink(source, link_name)

def remove_from_assets():
	from fluorine.utils.react_file_loader import remove_directory
	#app_path = frappe.get_app_path("fluorine")
	#meteor_web_path = os.path.join(os.path.abspath("."), "assets", "js", "meteor_web")

	#for app in ("meteor_app", "meteor_web"):
	try:
		#meteor_path = os.path.join(os.path.abspath("."), "assets", "js", "meteor_app")
		#remove_directory(meteor_path)
		meteor_path = os.path.join(os.path.abspath("."), "assets", "js", "meteor_web")
		#remove_directory(meteor_path)
		os.unlink(meteor_path)
		#remove_directory(os.path.join(os.path.abspath("."), "assets", "js", "packages"))
		#os.unlink(os.path.join(os.path.abspath("."), "assets", "js", "program.json"))
	except:
		pass

def copy_meteor_runtime_config():
	from shutil import copyfile

	app_path = frappe.get_app_path("fluorine")
	public_folder = os.path.join(app_path, "public")
	meteor_runtime_file = os.path.join(public_folder, "meteor_app", "meteor_runtime_config.js")
	copyfile(meteor_runtime_file, os.path.join(public_folder, "js", "meteor_runtime_config.js"))


def make_public_folders():

	for whatfor in ("meteor_app", "meteor_web"):
		app_path = frappe.get_app_path("fluorine")
		public_app_folder = os.path.join(app_path, "public", whatfor)
		frappe.create_folder(public_app_folder)


def check_prod_mode():
	from fluorine.utils.reactivity import meteor_config

	prod_mode = meteor_config.get("production_mode")

	return prod_mode


def make_start_meteor_script(doc):
	from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import get_mongo_exports, get_root_exports
	from fluorine.utils.file import get_path_reactivity, save_file
	import stat

	tostart = {"Both": ("meteor_app", "meteor_web"), "Reactive App": ("meteor_app", ), "Reactive Web": ("meteor_web", )}
	meteor_apps = tostart.get(doc.fluorine_reactivity)

	react_path = get_path_reactivity()

	for app in meteor_apps:
		meteor_final_path = os.path.join(react_path, app.replace("meteor", "final"), "bundle/exec_meteor")
		exp_mongo, mongo_default = get_mongo_exports(doc)
		mthost, mtport, forwarded_count = get_root_exports(doc, app)
		script =\
"""#!/usr/bin/env bash
export ROOT_URL=%s
export PORT=%s
%s
%s
node main.js""" % (mthost, mtport, forwarded_count, exp_mongo)
		save_file(meteor_final_path, script)

		st = os.stat(meteor_final_path)
		os.chmod(meteor_final_path, st.st_mode | stat.S_IEXEC)


def exec_cmd(cmd, cwd=".", with_password=False):
	import subprocess, getpass

	stdout=subprocess.PIPE
	echo = None

	if with_password:
		password = getpass.getpass("Please enter root password.\n")
		echo = subprocess.Popen(['echo', password], stdout=stdout,)

	p = subprocess.Popen(cmd, cwd=cwd, shell=True, stdin=echo.stdout if echo else None)

	return_code = p.wait()
	if return_code > 0:
		raise CommandFailedError("restarting nginx...")

def is_running_systemd(module, bench=".."):
	m = get_bench_module(module, bench=bench)
	res = run_bench_module(m, "is_running_systemd")
	return res

def get_program(module, p, bench=".."):
	m = get_bench_module(module, bench=bench)
	res = run_bench_module(m, "get_program", p)
	return res

def fix_prod_setup_perms(frappe_user=None, bench="."):
	m = get_bench_module("utils", bench=bench)
	run_bench_module(m, "fix_prod_setup_perms", frappe_user=frappe_user)


def linux_system_service(service, bench=".."):
	if os.path.basename(get_program("utils", ['systemctl'], bench=bench) or '') == 'systemctl' and is_running_systemd("production_setup", bench=bench):
		exec_cmd = "{prog} restart {service}".format(prog='systemctl', service=service)
	elif os.path.basename(get_program("utils", ['service'], bench=bench) or '') == 'service':
		exec_cmd = "{prog} {service} restart ".format(prog='service', service=service)
	else:
		raise Exception, 'No service manager found'

	return exec_cmd


def get_supervisor_confdir(path=""):

	if path.endswith("/"):
		path = path.rsplit("/",1)[0]

	possiblities = ('%s/etc/supervisor/conf.d' % path, '%s/etc/conf.d' % path, '%s/etc/supervisor.d/' % path, '%s/etc/supervisord/conf.d' % path, '%s/etc/supervisord.d' % path)
	for possiblity in possiblities:
		if os.path.exists(possiblity):
			return possiblity

	raise Exception, 'No supervisor conf dir found.'

def generate_nginx_supervisor_conf(doc, user=None, debug=None, bench="..", mac_sup_prefix_path="/usr/local"):
	import platform

	supervisor_conf_filename = "frappe.conf"

	if platform.system() == "Darwin" and not debug:
		m = get_bench_module("config", bench=bench)
		run_bench_module(m, "generate_nginx_config")
		m = get_bench_module("config", bench=bench)
		run_bench_module(m, "generate_supervisor_config", user=user)
		fix_prod_setup_perms(frappe_user=user, bench=bench)

		sup_conf_dir = get_supervisor_confdir(path=mac_sup_prefix_path)
		final_path = os.path.join(sup_conf_dir, supervisor_conf_filename)
		if not os.path.exists(final_path):
			os.symlink(os.path.abspath(os.path.join(bench, 'config', 'supervisor.conf')), final_path)
		make_supervisor(doc)
	elif platform.system() != "Darwin" and not debug:
		nginx_link = '/etc/nginx/conf.d/frappe.conf'
		if os.path.exists(nginx_link):
			os.unlink(nginx_link)
		bench_setup_production(user=user, bench=bench)
		make_supervisor(doc)
	else:
		m = get_bench_module("config", bench=bench)
		run_bench_module(m, "generate_nginx_config")
		fix_prod_setup_perms(frappe_user=user, bench=bench)


def start_nginx_services(debug=False):
	import platform

	if platform.system() == 'Darwin':
		try:
			click.echo("restarting nginx...")
			exec_cmd("sudo -S nginx -s reload", with_password=True)
			click.echo("nginx restarted.")
		except:
			click.echo("nginx not running. Starting nginx...")
			exec_cmd("sudo -S nginx", with_password=True)
			click.echo("nginx started.")
			#os.popen("sudo -S %s"%("sudo -S nginx"), 'w').write(password)

	else:
		click.echo("restarting nginx...")
		cmd = "sudo -S " + linux_system_service('nginx')
		exec_cmd(cmd, with_password=True)
		click.echo("nginx restarted.")

	if not debug:
		click.echo("restarting supervisor...")
		exec_cmd("sudo -S supervisorctl reload", with_password=True)
		click.echo("supervisor restarted.")


def bench_setup_production(user=None, bench=".."):
	import getpass

	if not user:
		user = getpass.getuser()

	cwd = os.getcwd()
	os.chdir("../")
	exec_cmd("sudo -S bench setup production %s" % user, with_password=True)
	os.chdir(cwd)


#TODO PARA REMOVER
@click.command('mproduction')
@click.option('--site', default=None, help='The site to work with. If not provided it will use the currentsite')
@click.option('--debug', is_flag=True)
@click.option('--force', is_flag=True)
def setup_production(site=None, debug=None, force=False):
	"""Prepare Frappe for meteor."""
	from fluorine.utils.fcache import clear_frappe_caches

	bench = "../../bench-repo/"
	#_setup_production()
	#return
	if site == None:
		site = get_default_site()

	doc = get_doctype("Fluorine Reactivity", site)

	devmode = doc.fluor_dev_mode
	fluor_state = doc.fluorine_state

	start_meteor_production_mode(doc, devmode, fluor_state, site=site, debug=debug, force=force, bench=bench)

	#start_nginx_services(debug=debug)

	clear_frappe_caches()

	if frappe.db:
		frappe.db.commit()
		frappe.destroy()


@click.command('setState')
@click.option('--site', default=None, help='The site to work with. If not provided it will use the currentsite')
@click.option('--state', default="start", help='Use start|stop|production to start, stop or set meteor in production mode.')
@click.option('--mongo-custom', help='Set False to use custom mongo. Set mongo custom options in folder reactivity/common_site_config.json. By default is True.', is_flag=True)
@click.option('--user', default=None, help='Name of the user to use to start production mode. Default to the current user.')
@click.option('--mac_sup_prefix_path', default="/usr/local", help='Name of the user to use to start production mode. Default to the current user.')
@click.option('--debug', is_flag=True)
@click.option('--force', is_flag=True)
def setState(site=None, state=None, mongo_custom=None, user=None, debug=None, force=None, mac_sup_prefix_path=None):
	"""Prepare Frappe for meteor."""
	import getpass

	if site == None:
		site = get_default_site()

	if not user:
		user = getpass.getuser()

	bench = "../../bench-repo/"

	_setState(site=site, state=state, debug=debug, force=force, mongo_custom=mongo_custom, user=user, bench=bench, mac_sup_prefix_path=mac_sup_prefix_path)


def _setState(site=None, state=None, debug=False, force=False, mongo_custom=False, user=None, bench="..", mac_sup_prefix_path="/usr/local"):
	from fluorine.utils.fcache import clear_frappe_caches

	doc = get_doctype("Fluorine Reactivity", site)

	devmode = doc.fluor_dev_mode
	fluor_state = doc.fluorine_state
	what = state.lower()
	if what == "start":
		start_meteor(doc, devmode, fluor_state, site=site, mongo_custom=mongo_custom, bench=bench)
	elif what == "stop":
		stop_meteor(doc, devmode, fluor_state, force=force, site=site, bench=bench)
	elif what == "production":
		#import sys
		start_meteor_production_mode(doc, devmode, fluor_state, site=site, debug=debug, force=force, user=user, bench=bench, mac_sup_prefix_path=mac_sup_prefix_path)
		#m = get_bench_module("config")
		#run_bench_module(m, "generate_nginx_config")

	clear_frappe_caches()

	if frappe.db:
		frappe.db.commit()
		frappe.destroy()


def start_meteor(doc, devmode, state, site=None, mongo_custom=False, bench=".."):
	from fluorine.utils.file import get_path_reactivity, save_js_file
	from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import save_to_procfile, make_mongodb_default
	from fluorine.utils.meteor.utils import PORT
	from fluorine.utils.reactivity import meteor_config
	import platform

	path_reactivity = get_path_reactivity()
	config_file_path = os.path.join(path_reactivity, "common_site_config.json")
	#meteor_config = frappe.get_file_json(config_file_path)

	if not devmode or state != "on":
		doc.fluor_dev_mode = 1
		doc.fluorine_state = "on"

	_change_hook(state="start", site=site)

	if not mongo_custom:
		meteor_config.pop("meteor_mongo", None)
		make_mongodb_default(meteor_config, doc.fluor_meteor_port or PORT.meteor_web)
		save_js_file(config_file_path, meteor_config)
		mongo_default = 0
	else:
		mongo_conf = meteor_config.get("meteor_mongo", None)
		if not mongo_conf or mongo_conf.get("type", None) == "default":
			click.echo("You must set mongo custom in reactivity/common_site_config.json or remove --mongo-custom option to use the mongo default.")
			_change_hook(state="stop", site=site)
			return
		mongo_default = 1

	doc.check_mongodb = mongo_default
	doc.save()

	make_public_link()
	remove_from_assets()
	save_to_procfile(doc)

	_generate_nginx_conf(production=False)
	try:
		src = os.path.abspath(os.path.join("..", 'config', 'nginx.conf'))
		if platform.system() == 'Darwin':
			frappe.create_folder('/usr/local/etc/nginx/sites-enabled/')
			if not os.path.exists('/usr/local/etc/nginx/sites-enabled/frappe.conf'):
				os.symlink(src, '/usr/local/etc/nginx/sites-enabled/frappe.conf')
		else:
			if not os.path.exists('/etc/nginx/conf.d/frappe.conf'):
				os.symlink(src, '/etc/nginx/conf.d/frappe.conf')

	except:
		click.echo("nginx link not set. You must make a symlink to frappe-bench/config/nginx.conf from nginx conf folder.")
		return

	click.echo("Please restart nginx.")


def stop_meteor(doc, devmode, state, force=False, site=None, production=False, bench=".."):
	#from fluorine.utils.file import set_config
	from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import remove_from_procfile, prepare_make_meteor_file

	#if state != "off" or force:
	doc.fluorine_state = "off"
	doc.fluor_dev_mode = 1
	#if production:
		#doc.fluor_dev_mode = 0
		#doc.check_mongodb = 1
	#	set_config({
	#		"developer_mode": 0
	#	})

	doc.save()

	remove_from_procfile()
	#if not production:
	_change_hook(state="stop", site=site)
	#else:
	#	prepare_make_meteor_file(doc.fluor_meteor_port, doc.fluorine_reactivity)


def _change_hook(site=None, state="start"):
	from fluorine.utils.fhooks import FluorineHooks

	with FluorineHooks(site=site) as fh:
		if state == "start":
			fh.change_base_template(page_default=False)
			fh.remove_hook_app_include()
		elif state == "stop":
			fh.change_base_template(page_default=True)
			fh.remove_hook_app_include()
		elif state == "production":
			fh.change_base_template(page_default=True)
			#app_include_js, app_include_css = get_meteor_app_files()
			fh.hook_app_include(["/assets/js/meteor_app.min.js"], ["/assets/css/meteor_app.css"])


def _check_custom_mongodb(doc):
	from fluorine.utils.file import get_path_reactivity, save_js_file

	path_reactivity = get_path_reactivity()
	config_file_path = os.path.join(path_reactivity, "common_site_config.json")
	meteor_config = frappe.get_file_json(config_file_path)
	mongo_conf = meteor_config.get("meteor_mongo", None)
	if not mongo_conf or mongo_conf.get("type", None) == "default":
		#click.echo("You must set mongo custom in reactivity/common_site_config.json.")
		click.echo("Using mongodb with localhost, port 27017 and db fluorine.")
		mghost = doc.fluor_mongo_host.strip()
		mgport = doc.fluor_mongo_port or 27017
		mgdb = doc.fluor_mongo_database.strip() or "fluorine"
		meteor_config["meteor_mongo"] = {
			"host": mghost,
			"port": mgport,
			"db": mgdb,
		}
		save_js_file(config_file_path, meteor_config)
	else:
		click.echo("Using mongodb with host {}, port {} and db {}.".format(mongo_conf.get("host"), mongo_conf.get("port"), mongo_conf.get("db")))

	return True

def start_meteor_production_mode(doc, devmode, state, site=None, debug=False, force=False, user=None, bench="..", mac_sup_prefix_path="/usr/local"):
	from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import make_meteor_file, prepare_client_files, remove_from_procfile, make_final_app_client, save_to_procfile
	from fluorine.utils.meteor.utils import build_meteor_context, make_meteor_props

	if doc.fluorine_state == "off" and doc.fluor_dev_mode == 0 and check_prod_mode() or force==True:

		if force==True:
			make_public_folders()

		_check_custom_mongodb(doc)
		#stop_meteor(doc, devmode, state, production=True)
		remove_from_procfile()
		prepare_client_files()
		#If debug then do not run frappe setup production and test only meteor in production mode.
		click.echo("Make meteor bundle for Desk APP")
		make_meteor_file(doc.fluor_meteor_host, doc.fluor_meteor_port, doc.ddpurl, doc.meteor_target_arch, doc.fluorine_reactivity)
		#Patch: run twice for fix nemo64:bootstrap less problem
		print "Run twice to patch nemo64:bootstrap less problem"
		click.echo("Make meteor bundle for WEB")
		make_meteor_file(doc.fluor_meteor_host, doc.fluor_meteor_port, doc.ddpurl, doc.meteor_target_arch, doc.fluorine_reactivity)

		context = frappe._dict()
		build_meteor_context(context, 0, "meteor_app")
		make_meteor_props(context, "meteor_app", production=1)

		copy_meteor_runtime_config()
		click.echo("Make build.json for meteor_app")
		make_final_app_client()
		click.echo("Run npm install for meteor server:")
		run_npm()
		click.echo("Make production links.")
		make_production_link()
		click.echo("Make js and css hooks.")
		_change_hook(state="production", site=site)
		#common_site_config.json must have meteor_dns for production mode or use default
		generate_nginx_supervisor_conf(doc, user=user, debug=debug, bench=bench, mac_sup_prefix_path=mac_sup_prefix_path)

		hosts_web, hosts_app = get_hosts(doc, production=True)
		_generate_nginx_conf(hosts_web=hosts_web, hosts_app=hosts_app, production=True)
		remove_public_link()

		#if not debug:
		#	click.echo("Run frappe setup production.")
		#	make_supervisor(doc)
			#click.echo("Please restart nginx and supervisor.")
		if debug:
			make_start_meteor_script(doc)
			save_to_procfile(doc, production_debug=True)
			#click.echo("Please restart nginx.")

		build()

		start_nginx_services(debug=debug)

	else:
		click.echo("You must set state to off in fluorine doctype and remove developer mode.")
		return


def build(make_copy=False, verbose=False):
	"Minify + concatenate JS and CSS files, build translations"
	import frappe.build
	frappe.build.bundle(False, make_copy=make_copy, verbose=verbose)


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

def make_supervisor(doc):
	import getpass
	from fluorine.utils.file import writelines, readlines, get_path_reactivity

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


def get_meteor_environment(doc, whatfor):
	from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import get_mongo_exports, get_root_exports
	#from fluorine.utils.meteor.utils import default_path_prefix, PORT
	#from fluorine.utils.file import get_path_reactivity


	conf = frappe._dict()

	#CONFIG FILE
	#path_reactivity = get_path_reactivity()
	#meteor_config = frappe.get_file_json(os.path.join(path_reactivity, "common_site_config.json"))

	#METEOR MAIL
	if hasattr(doc, "mailurl"):
		conf.mail_url = ", MAIL_URL='{mail_url}'".format(doc.mailurl)
	else:
		conf.mail_url = ""

	#MONGODB
	"""
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
	"""
	mongo_url, mongo_default = get_mongo_exports(doc)

	conf.mongo_url = mongo_url.replace("export MONGO_URL=", "").strip()
	#METEOR
	"""
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
	"""
	conf.root_url, conf.port, forwarded_count = get_root_exports(doc, whatfor)
	conf.forwarded_count = forwarded_count.replace("export", "").strip()
	#SUPERVISOR
	env = "PORT={port}, ROOT_URL='{root_url}', MONGO_URL='{mongo_url}'{mail_url}, {forwarded_count}".format(**conf)

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
	#final_app_path = os.path.join(path_reactivity, "final_app", "bundle", "programs", "web.browser")
	#meteordesk_path = os.path.join(os.path.abspath("."), "assets", "js", "meteor_app", "meteordesk")
	#if os.path.exists(final_app_path) and not os.path.exists(meteordesk_path):
	#	frappe.create_folder(os.path.join(os.path.abspath("."), "assets", "js", "meteor_app"))
	#	os.symlink(final_app_path, meteordesk_path)

	final_web_path = os.path.join(path_reactivity, "final_web", "bundle", "programs", "web.browser")
	meteor_web_path = os.path.join(os.path.abspath("."), "assets", "js", "meteor_web")
	if os.path.exists(final_web_path):
		try:
			os.symlink(final_web_path, meteor_web_path)
		except:
			pass


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

	config_path = os.path.join(os.path.abspath(".."), "config")
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
	setup_production,
	setState
]