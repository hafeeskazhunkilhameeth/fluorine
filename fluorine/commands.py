from __future__ import unicode_literals, absolute_import
__author__ = 'luissaguas'


import click
from fluorine.commands_helpers import *

from fluorine.commands_helpers import services as sh
from fluorine.commands_helpers import meteor as mh
from fluorine.commands_helpers import config as ch
from fluorine.commands_helpers import hooks as hh
from fluorine.commands_helpers import mongo as mgh


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
@click.option('--update', is_flag=True)
@click.option('--force', is_flag=True)
def setState(site=None, state=None, mongo_custom=None, user=None, mac_sup_prefix_path=None, debug=None, update=None, force=None):
	"""Prepare Frappe for meteor."""
	import getpass

	if site == None:
		site = get_default_site()

	if not user:
		user = getpass.getuser()

	bench = "../../bench-repo/"

	_setState(site=site, state=state, debug=debug, update= update, force=force, mongo_custom=mongo_custom, user=user, bench=bench, mac_sup_prefix_path=mac_sup_prefix_path)


def _setState(site=None, state=None, debug=False, update=False, force=False, mongo_custom=False, user=None, bench="..", mac_sup_prefix_path="/usr/local"):
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
		from fluorine.utils.reactivity import meteor_config

		if not update and not debug:
			if meteor_config.get("on_update", None):
				update = True
		in_production = start_meteor_production_mode(doc, devmode, fluor_state, site=site, debug=debug, update=update, force=force, user=user, bench=bench, mac_sup_prefix_path=mac_sup_prefix_path)
		if in_production and update:
			#from fluorine.commands_helpers.meteor import update_common_config
			from fluorine.utils.meteor.utils import update_common_config
			#from fluorine.utils.file import get_path_reactivity, save_js_file

			meteor_config["on_update"] = False
			update_common_config(meteor_config)
			#path_reactivity = get_path_reactivity()
			#config_file_path = os.path.join(path_reactivity, "common_site_config.json")
			#save_js_file(config_file_path, meteor_config)
		#m = get_bench_module("config")
		#run_bench_module(m, "generate_nginx_config")

	clear_frappe_caches()

	if frappe.db:
		frappe.db.commit()
		frappe.destroy()


def start_meteor(doc, devmode, state, site=None, mongo_custom=False, bench=".."):
	from fluorine.utils.file import get_path_reactivity, save_js_file
	from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import save_to_procfile, make_mongodb_default
	from fluorine.utils.meteor.utils import PORT, update_common_config
	from fluorine.utils.reactivity import meteor_config
	import platform

	#path_reactivity = get_path_reactivity()
	#config_file_path = os.path.join(path_reactivity, "common_site_config.json")
	#meteor_config = frappe.get_file_json(config_file_path)

	if not devmode or state != "on":
		doc.fluor_dev_mode = 1
		doc.fluorine_state = "on"

	hh._change_hook(state="start", site=site)

	if not mongo_custom:
		meteor_config.pop("meteor_mongo", None)
		make_mongodb_default(meteor_config, doc.fluor_meteor_port or PORT.meteor_web)
		#save_js_file(config_file_path, meteor_config)
		update_common_config(meteor_config)
		mongo_default = 0
	else:
		mongo_conf = meteor_config.get("meteor_mongo", None)
		if not mongo_conf or mongo_conf.get("type", None) == "default":
			click.echo("You must set mongo custom in reactivity/common_site_config.json or remove --mongo-custom option to use the mongo default.")
			hh._change_hook(state="stop", site=site)
			return
		mongo_default = 1

	doc.check_mongodb = mongo_default
	doc.save()

	mh.make_public_link()
	mh.remove_from_assets()
	save_to_procfile(doc)

	ch._generate_nginx_conf(production=False)
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
	hh._change_hook(state="stop", site=site)
	#else:
	#	prepare_make_meteor_file(doc.fluor_meteor_port, doc.fluorine_reactivity)


def start_meteor_production_mode(doc, devmode, state, site=None, debug=False, update=False, force=False, user=None, bench="..", mac_sup_prefix_path="/usr/local"):
	from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import make_meteor_file, prepare_client_files, remove_from_procfile, make_final_app_client, save_to_procfile
	from fluorine.utils.meteor.utils import build_meteor_context, make_meteor_props


	if state == "off" and devmode == 0 and check_prod_mode() or force==True:

		if _check_updates(bench=bench):
			click.echo("There are updates in your apps. To update production you must press button 'run_updates' in fluorine app.")
			return

		if force==True:
			mh.make_public_folders()

		mgh._check_custom_mongodb(doc)
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

		mh.copy_meteor_runtime_config()
		click.echo("Make build.json for meteor_app")
		make_final_app_client()
		click.echo("Run npm install for meteor server:")
		mh.run_npm()
		click.echo("Make production links.")
		mh.make_production_link()
		click.echo("Make js and css hooks.")
		hh._change_hook(state="production", site=site)
		#common_site_config.json must have meteor_dns for production mode or use default
		ch.generate_nginx_supervisor_conf(doc, user=user, debug=debug, update=update, bench=bench, mac_sup_prefix_path=mac_sup_prefix_path)

		hosts_web, hosts_app = get_hosts(doc, production=True)
		ch._generate_nginx_conf(hosts_web=hosts_web, hosts_app=hosts_app, production=True)
		mh.remove_public_link()

		#if not debug:
		#	click.echo("Run frappe setup production.")
		#	make_supervisor(doc)
			#click.echo("Please restart nginx and supervisor.")
		if debug:
			mh.make_start_meteor_script(doc)
			save_to_procfile(doc, production_debug=True)
			#click.echo("Please restart nginx.")

		sh.build_assets(bench_path=bench)

		sh.start_nginx_supervisor_services(debug=debug)

		return True

	else:
		click.echo("You must set state to off in fluorine doctype and remove developer mode.")
		return False

def _check_updates(bench="."):
	from fluorine.commands_helpers.meteor import get_active_apps, check_updates

	click.echo("Checking for updates...")
	apps = get_active_apps()
	return check_updates(apps, bench=bench)

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
	ch._generate_nginx_conf(hosts_web=hosts_web, hosts_app=hosts_app, production=production)


#def make_nginx_replace(m):
#	content = m.group(1)
#	print "m.group 1 {}".format(m.group(1))
#	return content + "\nteste123"


commands = [
	mongodb_conf,
	nginx_conf,
	setup_production,
	setState
]