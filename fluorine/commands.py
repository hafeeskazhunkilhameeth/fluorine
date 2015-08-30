from __future__ import unicode_literals, absolute_import
__author__ = 'luissaguas'


import click
from fluorine.commands_helpers import *

from fluorine.commands_helpers import services as sh
from fluorine.commands_helpers import meteor as mh
from fluorine.commands_helpers import config as ch
from fluorine.commands_helpers import hooks as hh
from fluorine.commands_helpers import mongo as mgh


def _reset_packages(app, file_add=None, file_remove=None):
	from fluorine.utils.install import meteor_reset_package

	for whatfor in ("meteor_app", "meteor_web"):
		meteor_reset_package(app, whatfor, file_add=file_add, file_remove=file_remove)


def _reset_packages_all(file_add=None, file_remove=None):
	from fluorine.commands_helpers.meteor import get_active_apps

	apps = get_active_apps()
	for app in apps:
		_reset_packages(app, file_add=file_add, file_remove=file_remove)


def _remove_meteor_packages(app, file_remove=None):
	from fluorine.utils.install import meteor_remove_package

	for whatfor in ("meteor_app", "meteor_web"):
		meteor_remove_package(app, whatfor, file_remove=file_remove)


def remove_meteor_packages(file_remove=None):
	from fluorine.commands_helpers.meteor import get_active_apps

	apps = get_active_apps()
	for app in apps:
		_remove_meteor_packages(app, file_remove=file_remove)

def _add_meteor_packages(app, file_add=None):
	from fluorine.utils.install import meteor_add_package

	for whatfor in ("meteor_app", "meteor_web"):
		meteor_add_package(app, whatfor, file_add=file_add)


def add_meteor_packages(file_add=None):
	from fluorine.commands_helpers.meteor import get_active_apps

	apps = get_active_apps()
	for app in apps:
		_add_meteor_packages(app, file_add=file_add)


def _cmd_create_meteor_apps(doc):
	from fluorine.utils.install import create_meteor_apps
	from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import check_meteor_apps_created

	if not check_meteor_apps_created(doc, with_error=False):
		create_meteor_apps()
		add_meteor_packages()


@click.command('check-updates')
@click.option('--site', default=None, help='The site to work with. If not provided it will use the currentsite')
def cmd_check_updates(site=None):
	"""Check for update in versions of fluorine apps."""
	from fluorine.commands_helpers.meteor import check_updates

	if site == None:
		site = get_default_site()

	bench = "../../bench-repo/"
	start_frappe_db(site)

	if check_updates(bench=bench):
		click.echo("fluorine apps are not updated.")
	else:
		click.echo("fluorine apps are updated.")


@click.command('update-version')
@click.option('--site', default=None, help='The site to work with. If not provided it will use the currentsite')
def cmd_update_version(site=None):
	"""Update version of fluorine apps."""
	from fluorine.commands_helpers.meteor import update_versions

	if site == None:
		site = get_default_site()

	bench = "../../bench-repo/"
	start_frappe_db(site)

	update_versions(bench=bench)
	click.echo("fluorine apps were updated.")


@click.command('remove-meteor-packages')
@click.option('--app', default=None, help='The name of the fluorine app to reset packages.')
@click.option('--site', default=None, help='The site to work with. If not provided it will use the currentsite')
def cmd_remove_meteor_packages(app, site=None):
	"""Add meteor packages from an app."""
	from fluorine.commands_helpers.meteor import is_valid_fluorine_app
	from fluorine.commands_helpers.config import get_custom_packages_files

	if site == None:
		site = get_default_site()

	start_frappe_db(site)

	if app and not is_valid_fluorine_app(app):
		click.echo("Sorry. App %s does not exist as meteor app." % app)
		return

	file_add, file_remove = get_custom_packages_files()

	if app:
		_remove_meteor_packages(app, file_remove=file_remove)
	else:
		remove_meteor_packages(file_remove=file_remove)


@click.command('add-meteor-packages')
@click.option('--app', default=None, help='The name of the fluorine app to reset packages.')
@click.option('--site', default=None, help='The site to work with. If not provided it will use the currentsite')
def cmd_add_meteor_packages(app=None, site=None):
	"""Add meteor packages from an app."""
	from fluorine.commands_helpers.meteor import is_valid_fluorine_app
	from fluorine.commands_helpers.config import get_custom_packages_files

	if site == None:
		site = get_default_site()

	start_frappe_db(site)

	if app and not is_valid_fluorine_app(app):
		click.echo("Sorry. App %s does not exist as meteor app." % app)
		return

	file_add, file_remove = get_custom_packages_files()

	if app:
		_add_meteor_packages(app, file_add=file_add)
	else:
		add_meteor_packages(file_add=file_add)


@click.command('reset-meteor-packages')
@click.option('--app', default=None, help='The name of the fluorine app to reset packages.')
@click.option('--site', default=None, help='The site to work with. If not provided it will use the currentsite')
def cmd_reset_meteor_packages(app=None, site=None):
	"""Reset meteor packages."""
	from fluorine.commands_helpers.meteor import is_valid_fluorine_app
	from fluorine.commands_helpers.config import get_custom_packages_files


	if site == None:
		site = get_default_site()

	start_frappe_db(site)

	file_add, file_remove = get_custom_packages_files()

	if app:
		if not is_valid_fluorine_app(app):
			click.echo("Sorry. App %s does not exist as meteor app." % app)
			return
		_reset_packages(app, file_add=file_add, file_remove=file_remove)
	else:
		_reset_packages_all(file_add=file_add, file_remove=file_remove)


@click.command('create-meteor-apps')
@click.option('--site', default=None, help='The site to work with. If not provided it will use the currentsite')
def cmd_create_meteor_apps(site=None):
	"""Create meteor apps."""

	if site == None:
		site = get_default_site()

	doc = get_doctype("Fluorine Reactivity", site)

	_cmd_create_meteor_apps(doc)


@click.command('current-dev-app')
@click.argument('app')
def set_current_app(app):
	"""Set the current app."""
	from fluorine.utils.reactivity import meteor_config
	from fluorine.utils.meteor.utils import update_common_config

	meteor_config["current_dev_app"] = app
	update_common_config(meteor_config)


@click.command('restore-common-config')
@click.option('--site', default=None, help='The site to work with. If not provided it will use the currentsite.')
def cmd_restore_common_config(site=None):
	"""Restore the common site config file in reactivity folder."""
	from fluorine.utils.reactivity import meteor_config
	from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import save_to_common_site_config

	if site == None:
		site = get_default_site()

	doc = get_doctype("Fluorine Reactivity", site)

	if not meteor_config:
		meteor_config = {}

	if doc.current_dev_app and doc.current_dev_app.strip() != "":
		meteor_config["current_dev_app"] = doc.current_dev_app

	meteor_config["production_mode"] = meteor_config.get("production_mode") or 0
	meteor_config["developer_mode"] = doc.fluor_dev_mode
	save_to_common_site_config(doc, meteor_config)

	click.echo("Common config restored.")


#TODO PARA REMOVER
@click.command('mproduction')
@click.option('--site', default=None, help='The site to work with. If not provided it will use the currentsite.')
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


@click.command('set-state')
@click.argument('state')
@click.option('--site', default=None, help='The site to work with. If not provided it will use the currentsite')
@click.option('--custom-mongo', help='Set False to use custom mongo. Set mongo custom options in folder reactivity/common_site_config.json. By default is True.', is_flag=True)
@click.option('--user', default=None, help='Name of the user to use to start production mode. Default to the current user.')
@click.option('--server-port', default=None, help='Nginx listen port. Supply the port number if it is different then 80. Used only in production mode.')
@click.option('--mac_sup_prefix_path', default="/usr/local", help='Name of the user to use to start production mode. Default to the current user.')
@click.option('--debug', is_flag=True)
@click.option('--update', is_flag=True)
@click.option('--force', is_flag=True)
def setState(state, site=None, custom_mongo=None, user=None, server_port=None, mac_sup_prefix_path=None, debug=None, update=None, force=None):
	"""Prepare Frappe for meteor.\n
		STATE: \n
		`develop` to enter in developer mode;\n
		`production` to enter in production mode;\n
		`stop` to enter in original frappe web.
	"""
	import getpass

	if site == None:
		site = get_default_site()

	if not user:
		user = getpass.getuser()

	bench = "../../bench-repo/"

	_setState(site=site, state=state, debug=debug, update= update, force=force, mongo_custom=custom_mongo, user=user, bench=bench, server_port=server_port, mac_sup_prefix_path=mac_sup_prefix_path)


def _setState(site=None, state=None, debug=False, update=False, force=False, mongo_custom=False, user=None, bench="..", server_port=None, mac_sup_prefix_path="/usr/local"):
	from fluorine.utils.fcache import clear_frappe_caches

	doc = get_doctype("Fluorine Reactivity", site)

	devmode = doc.fluor_dev_mode
	fluor_state = doc.fluorine_state
	what = state.lower()
	if what == "develop":
		start_meteor(doc, devmode, fluor_state, site=site, mongo_custom=mongo_custom, bench=bench)
	elif what == "stop":
		stop_meteor(doc, devmode, fluor_state, force=force, site=site, bench=bench)
	elif what == "production":
		from fluorine.utils.reactivity import meteor_config

		current_dev_app = meteor_config.get("current_dev_app", None)
		if not current_dev_app:
			from fluorine.commands_helpers.meteor import get_active_apps
			apps = get_active_apps()
			if len(apps) > 1:
				click.echo("Please you must set the current_dev_app in reactivity/common_site_config.json to continue.")
				return
			else:
				current_dev_app = apps[0]

		if not update and not debug:
			if meteor_config.get("on_update", 0):
				update = True
		in_production = start_meteor_production_mode(doc, devmode, fluor_state, current_dev_app, server_port=server_port, site=site, debug=debug, update=update, force=force, user=user, bench=bench, mac_sup_prefix_path=mac_sup_prefix_path)
		if in_production and update:
			#from fluorine.commands_helpers.meteor import update_common_config
			from fluorine.utils.meteor.utils import update_common_config
			#from fluorine.utils.file import get_path_reactivity, save_js_file

			meteor_config["on_update"] = 0
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
	#from fluorine.utils.file import get_path_reactivity, save_js_file
	from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import save_to_procfile, make_mongodb_default, check_meteor_apps_created
	from fluorine.utils.meteor.utils import PORT, update_common_config
	from fluorine.utils.reactivity import meteor_config
	import platform

	#path_reactivity = get_path_reactivity()
	#config_file_path = os.path.join(path_reactivity, "common_site_config.json")
	#meteor_config = frappe.get_file_json(config_file_path)
	click.echo("Checking for meteor apps folder. Please wait.")
	if not check_meteor_apps_created(doc):
		click.echo("Please install meteor app first. From command line issue 'bench fluorine create-meteor-apps.'")
		return

	if not devmode or state != "on":
		doc.fluor_dev_mode = 1
		doc.fluorine_state = "on"

	meteor_config["developer_mode"] = 1
	meteor_config["production_mode"] = 0
	#hh._change_hook(state="start", site=site)
	meteor_config["stop"] = 0
	#use mongo from meteor by default
	if not mongo_custom:
		meteor_config.pop("meteor_mongo", None)
		make_mongodb_default(meteor_config, doc.fluor_meteor_port or PORT.meteor_web)
		#save_js_file(config_file_path, meteor_config)
		mongo_default = 0
	else:
		mongo_conf = meteor_config.get("meteor_mongo", None)
		if not mongo_conf or mongo_conf.get("type", None) == "default":
			click.echo("You must set mongo custom in reactivity/common_site_config.json or remove --mongo-custom option to use the mongo default.")
			hh._change_hook(state="stop", site=site)
			return
		mongo_default = 1

	update_common_config(meteor_config)
	doc.check_mongodb = mongo_default
	doc.save()

	mh.make_public_link()
	mh.remove_from_assets()
	save_to_procfile(doc)
	bench_generate_nginx_config(bench=bench)
	ch._generate_fluorine_nginx_conf(production=False)
	try:
		src = os.path.abspath(os.path.join("..", 'config', 'nginx.conf'))
		if platform.system() == 'Darwin':
			frappe.create_folder('/usr/local/etc/nginx/sites-enabled/')
			if not os.path.exists('/usr/local/etc/nginx/sites-enabled/frappe.conf'):
				os.symlink(src, '/usr/local/etc/nginx/sites-enabled/frappe.conf')
		else:
			if not os.path.exists('/etc/nginx/conf.d/frappe.conf'):
				os.symlink(src, '/etc/nginx/conf.d/frappe.conf')

		click.echo("Please issue bench start and go to http://localhost or http://127.0.0.1.")
	except:
		click.echo("nginx link not set. You must make a symlink to frappe-bench/config/nginx.conf from nginx conf folder.")
		return

	#click.echo("Please restart nginx.")
	sh.start_nginx_supervisor_services(debug=True)


def stop_meteor(doc, devmode, state, force=False, site=None, production=False, bench=".."):
	#from fluorine.utils.file import set_config
	from fluorine.utils import meteor_config
	from fluorine.utils.meteor.utils import update_common_config
	from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import remove_from_procfile

	#if state != "off" or force:
	doc.fluorine_state = "off"
	doc.fluor_dev_mode = 1
	#if production:
		#doc.fluor_dev_mode = 0
		#doc.check_mongodb = 1
	#	set_config({
	#		"developer_mode": 0
	#	})
	meteor_config["stop"] = 1
	meteor_config["developer_mode"] = 1
	meteor_config["production_mode"] = 0
	update_common_config(meteor_config)
	doc.save()

	remove_from_procfile()
	click.echo("Please issue bench start go to http://localhost:8000 or http://127.0.0.1:8000.")
	#if not production:
	#hh._change_hook(state="stop", site=site)
	#else:
	#	prepare_make_meteor_file(doc.fluor_meteor_port, doc.fluorine_reactivity)


def start_meteor_production_mode(doc, devmode, state, current_dev_app, server_port=None, site=None, debug=False, update=False, force=False, user=None, bench="..", mac_sup_prefix_path="/usr/local"):
	from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import remove_from_procfile, make_final_app_client, save_to_procfile, check_meteor_apps_created
	from fluorine.utils.meteor.utils import build_meteor_context, make_meteor_props, make_meteor_files, prepare_client_files

	prodmode = check_prod_mode()
	if state == "off" and devmode == 0 and prodmode:# or prodmode:# and force==True:

		click.echo("Checking for meteor apps folder. Please wait.")
		if not check_meteor_apps_created(doc):
			click.echo("Please install meteor app first. From command line issue 'bench fluorine create-meteor-apps.'")
			return

		if _check_updates(bench=bench):
			click.echo("There are updates in your apps. To update production you must press button 'run_updates' in fluorine app.")
			return

		#if force==True:
		mh.make_public_folders()

		mgh._check_custom_mongodb(doc)
		#stop_meteor(doc, devmode, state, production=True)
		remove_from_procfile()
		#only save the meteor packages installed in fluorine if fluorine app is in development.
		if current_dev_app != "fluorine" or current_dev_app == "fluorine" and force:
			prepare_client_files(current_dev_app)
		#If debug then do not run frappe setup production and test only meteor in production mode.
		click.echo("Make meteor bundle for Desk APP")
		make_meteor_files(doc.fluor_meteor_host, doc.fluor_meteor_port, doc.ddpurl, doc.meteor_target_arch, doc.fluorine_reactivity)
		#Patch: run twice for fix nemo64:bootstrap less problem
		print "Run twice to patch nemo64:bootstrap less problem"
		click.echo("Make meteor bundle for WEB")
		make_meteor_files(doc.fluor_meteor_host, doc.fluor_meteor_port, doc.ddpurl, doc.meteor_target_arch, doc.fluorine_reactivity)

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

		#hh._change_hook(state="production", site=site)
		#common_site_config.json must have meteor_dns for production mode or use default
		ch.generate_nginx_supervisor_conf(doc, user=user, debug=debug, update=update, bench=bench, mac_sup_prefix_path=mac_sup_prefix_path)

		hosts_web, hosts_app = get_hosts(doc, production=True)
		ch._generate_fluorine_nginx_conf(hosts_web=hosts_web, hosts_app=hosts_app, production=True, server_port=server_port)
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

		click.echo("Please go to http://localhost or http://127.0.0.1.")

		return True

	else:
		click.echo("You must set state to off in fluorine doctype and remove developer mode.")
		return False

def _check_updates(bench="."):
	from fluorine.commands_helpers.meteor import check_updates

	click.echo("Checking for updates...")
	return check_updates(bench=bench)

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
	ch._generate_fluorine_nginx_conf(hosts_web=hosts_web, hosts_app=hosts_app, production=production)


#def make_nginx_replace(m):
#	content = m.group(1)
#	print "m.group 1 {}".format(m.group(1))
#	return content + "\nteste123"


commands = [
	mongodb_conf,
	nginx_conf,
	set_current_app,
	cmd_create_meteor_apps,
	cmd_reset_meteor_packages,
	cmd_add_meteor_packages,
	cmd_remove_meteor_packages,
	cmd_restore_common_config,
	setup_production,
	cmd_update_version,
	cmd_check_updates,
	setState
]