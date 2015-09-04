from __future__ import unicode_literals, absolute_import
__author__ = 'luissaguas'


import click
from fluorine.utils import whatfor_all
from fluorine.commands_helpers import *

from fluorine.commands_helpers import services as sh
from fluorine.commands_helpers import meteor as mh
from fluorine.commands_helpers import config as ch


COLORS = ("green", "blue", "yellow", "red", "black", "white", "magenta", "cyan")


def click_format(msg, color=None, new_line=True, end_line=True):
	from random import randint

	if not color:
		color = COLORS[randint(0,7)]

	if new_line:
		click.echo("\n" * 1)

	click.echo(click.style(msg, fg=color))

	if end_line:
		click.echo("\n" * 1)

	return color


def meteor_echo(msg, count=30, color=None, new_line=True, end_line=True):
	color = click_format("*" * count, color=color, new_line=new_line, end_line=end_line)
	click.echo(msg)
	click_format("*" * count, color=color, new_line=new_line, end_line=end_line)


def _reset_packages(app, file_add=None, file_remove=None):
	from fluorine.utils.meteor.packages import meteor_reset_package

	for whatfor in whatfor_all:#("meteor_app", "meteor_web"):
		meteor_reset_package(app, whatfor, file_add=file_add, file_remove=file_remove)


def _reset_packages_all(file_add=None, file_remove=None):
	from fluorine.commands_helpers.meteor import get_active_apps

	apps = get_active_apps()
	for app in apps:
		_reset_packages(app, file_add=file_add, file_remove=file_remove)


def _remove_meteor_packages(app, file_remove=None):
	from fluorine.utils.meteor.packages import meteor_remove_package

	for whatfor in whatfor_all:#("meteor_app", "meteor_web"):
		meteor_remove_package(app, whatfor, file_remove=file_remove)


def remove_meteor_packages(file_remove=None):
	from fluorine.commands_helpers.meteor import get_active_apps

	apps = get_active_apps()
	for app in apps:
		_remove_meteor_packages(app, file_remove=file_remove)

def _add_meteor_packages(app, file_add=None):
	from fluorine.utils.meteor.packages import meteor_add_package

	for whatfor in whatfor_all:#("meteor_app", "meteor_web"):
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


@click.command('get-apps-packages-list')
@click.option('--custom-file-to-add', default=None, help='Name of the custom file with packages to add.')
@click.option('--custom-file-to-remove', default=None, help='Name of the custom file with packages to remove.')
def cmd_get_apps_packages_list(custom_file_to_add=None, custom_file_to_remove=None):
	from fluorine.utils.meteor.packages import print_meteor_packages_list, get_package_list_updates

	curr_app = get_current_dev_app()
	for whatfor in whatfor_all:
		pckg_add, pckg_remove, i_pckgs = get_package_list_updates(curr_app, whatfor, file_add=custom_file_to_add, file_remove=custom_file_to_remove)
		print_meteor_packages_list(whatfor, pckg_add, pckg_remove, i_pckgs)

@click.command('get-current-state')
def cmd_get_state():
	"""Set the current app."""
	from fluorine.utils.reactivity import meteor_config

	production_mode = meteor_config.get("production_mode")
	developer_mode = meteor_config.get("developer_mode")
	stop = meteor_config.get("stop")

	color = click_format("*" * 35)
	if production_mode:
		click.echo("Current State: %s" % "Production mode.")

	elif developer_mode:
		click.echo("Current State: %s" % "Developer mode.")
	elif stop:
		click.echo("Current State: %s" % "Stop. Default frappe mode.")
	else:
		click.echo("Current State: %s" % "Undefined mode. Check reactivity/common_site_config.json.")

	click_format("*" * 35, color=color)


@click.command('current-dev-app')
@click.argument('app')
def set_current_app(app):
	"""Set the current app."""
	from fluorine.utils.reactivity import meteor_config
	from fluorine.utils.meteor.utils import update_common_config

	if meteor_config and meteor_config.get("developer_mode"):
		meteor_config["current_dev_app"] = app
		update_common_config(meteor_config)
	else:
		color = click_format("*" * 40)
		click.echo("You must be in developer mode to change current dev app.")
		click_format("*" * 40, color)


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

	color = click_format("*" * 30)
	click.echo("Common config restored.")
	click_format("*" * 30, color)


@click.command('set-state')
@click.argument('state')
@click.option('--site', default=None, help='The site to work with. If not provided it will use the currentsite')
@click.option('--custom-mongo', help='Set False to use custom mongo. Set mongo custom options in folder reactivity/common_site_config.json. By default is True.', is_flag=True)
@click.option('--user', default=None, help='Name of the user to use to start production mode. Default to the current user.')
@click.option('--server-port', default=None, help='Nginx listen port. Supply the port number if it is different then 80.')
@click.option('--ddp-port', default=None, help='Port used to connect with meteor. Used only by desk app.')
@click.option('--mac_sup_prefix_path', default="/usr/local", help='Name of the user to use to start production mode. Default to the current user.')
@click.option('--debug', is_flag=True)
@click.option('--update', is_flag=True)
@click.option('--force', is_flag=True)
@click.option('--skip-package-check-updates', is_flag=True)
@click.option('--custom-file-to-add', default=None, help='Name of the custom file with packages to add.')
@click.option('--custom-file-to-remove', default=None, help='Name of the custom file with packages to remove.')
def setState(state, site=None, custom_mongo=None, user=None, server_port=None, ddp_port=None, mac_sup_prefix_path=None, debug=None,
			update=None, force=None, custom_file_to_add=None, custom_file_to_remove=None, skip_package_check_updates=False):
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

	color = click_format("*" * 80)
	_setState(site=site, state=state, debug=debug, update= update, force=force, mongo_custom=custom_mongo, user=user, bench=bench,
		server_port=server_port, ddp_port=ddp_port, mac_sup_prefix_path=mac_sup_prefix_path, file_to_add=custom_file_to_add, file_to_remove=custom_file_to_remove, skip_package_check_updates=skip_package_check_updates)
	click_format("*" * 80, color)


def _setState(site=None, state=None, debug=False, update=False, force=False, mongo_custom=False, user=None, bench="..",
			server_port=None, ddp_port=None, mac_sup_prefix_path="/usr/local", file_to_add=None, file_to_remove=None, skip_package_check_updates=False):
	from fluorine.utils.fcache import clear_frappe_caches
	from fluorine.commands_helpers.meteor import MeteorContext
	doc = get_doctype("Fluorine Reactivity", site)

	devmode = doc.fluor_dev_mode
	fluor_state = doc.fluorine_state
	what = state.lower()
	if what == "init":
		mctx = MeteorContext()
		mctx.meteor_init(mongo_custom=mongo_custom)
	elif what == "develop":
		from fluorine.commands_helpers import get_current_dev_app

		current_dev_app = get_current_dev_app()
		start_meteor(doc, current_dev_app, site=site, mongo_custom=mongo_custom, bench=bench, server_port=server_port, ddp_port=ddp_port,
					file_to_add=file_to_add, file_to_remove=file_to_remove, skip_package_check_updates=skip_package_check_updates)
	elif what == "stop":
		stop_meteor(doc, devmode, fluor_state, force=force, site=site, bench=bench)
	elif what == "production":
		from fluorine.commands_helpers import get_current_dev_app
		from fluorine.utils.reactivity import meteor_config

		current_dev_app = get_current_dev_app()

		if not update and not debug:
			if meteor_config.get("on_update", 0):
				update = True
		in_production = start_meteor_production_mode(doc, current_dev_app, server_port=server_port, ddp_port=ddp_port, site=site, debug=debug,
				update=update, force=force, user=user, bench=bench, mac_sup_prefix_path=mac_sup_prefix_path, file_to_add=file_to_add, file_to_remove=file_to_remove)
		if in_production and update:
			from fluorine.utils.meteor.utils import update_common_config

			meteor_config["on_update"] = 0
			update_common_config(meteor_config)

	else:
		click.echo("The command %s does not exist." % what)

	clear_frappe_caches()

	if frappe.db:
		frappe.db.commit()
		frappe.destroy()


def start_meteor(doc, current_dev_app, site=None, mongo_custom=False, server_port=None, ddp_port=None, bench="..", file_to_add=None, file_to_remove=None, skip_package_check_updates=False):
	"""
	from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import save_to_procfile, make_mongodb_default, check_meteor_apps_created
	from fluorine.utils.meteor.utils import PORT
	from fluorine.utils.reactivity import meteor_config
	from fluorine.commands_helpers.meteor import MeteorContext
	import platform


	click.echo("Checking for meteor apps folder. Please wait.")
	if not check_meteor_apps_created(doc):
		click.echo("Please install meteor app first. From command line issue 'bench fluorine create-meteor-apps.'")
		return

	#if not devmode or state != "on":
	doc.fluor_dev_mode = 1
	doc.fluorine_state = "on"

	meteor_config["developer_mode"] = 1
	meteor_config["production_mode"] = 0
	meteor_config["stop"] = 0

	mctx = MeteorContext(production=False)
	mctx.meteor_init(mongo_custom=mongo_custom)
	#use mongo from meteor by default
	if not mongo_custom:
		meteor_config.pop("meteor_mongo", None)
		make_mongodb_default(meteor_config, doc.fluor_meteor_port or PORT.meteor_web)
		mongo_default = 0
	else:
		mongo_conf = meteor_config.get("meteor_mongo", None)
		if not mongo_conf or mongo_conf.get("type", None) == "default":
			click.echo("You must set mongo custom in reactivity/common_site_config.json or remove --custom-mongo option to use the mongo default.")
			return
		mongo_default = 1

	#update_common_config(meteor_config)
	doc.check_mongodb = mongo_default
	#also save meteor_config to file
	doc.save()
	mctx.make_context()

	#mh.make_public_folders()
	mh.remove_from_assets()
	save_to_procfile(doc)
	bench_generate_nginx_config(bench=bench)
	ch._generate_fluorine_nginx_conf(production=False, site=site)
	try:
		src = os.path.abspath(os.path.join("..", 'config', 'nginx.conf'))
		if platform.system() == 'Darwin':
			frappe.create_folder('/usr/local/etc/nginx/sites-enabled/')
			if not os.path.exists('/usr/local/etc/nginx/sites-enabled/frappe.conf'):
				os.symlink(src, '/usr/local/etc/nginx/sites-enabled/frappe.conf')
		else:
			if not os.path.exists('/etc/nginx/conf.d/frappe.conf'):
				os.symlink(src, '/etc/nginx/conf.d/frappe.conf')

		sh.start_nginx_supervisor_services(debug=True)
		click.echo("Please issue `bench start` and go to http://localhost or http://127.0.0.1.")

	except:
		click.echo("nginx link not set. You must make a symlink to frappe-bench/config/nginx.conf from nginx conf folder.")
		return
	"""
	from fluorine.commands_helpers.meteor import MeteorDevelop
	md = MeteorDevelop(doc, current_dev_app, site=site, mongo_custom=mongo_custom, server_port=server_port, ddp_port=ddp_port,
					bench=bench, file_to_add=file_to_add, file_to_remove=file_to_remove, skip_package_check_updates=skip_package_check_updates)
	md.start()


def stop_meteor(doc, devmode, state, force=False, site=None, production=False, bench=".."):
	from fluorine.utils import meteor_config
	#from fluorine.utils.meteor.utils import update_common_config
	from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import remove_from_procfile


	doc.fluorine_state = "off"
	doc.fluor_dev_mode = 1
	meteor_config["stop"] = 1
	meteor_config["developer_mode"] = 1
	meteor_config["production_mode"] = 0
	#update_common_config(meteor_config)

	#also save meteor_config to file
	doc.save()

	remove_from_procfile()
	click.echo("Please issue `bench start` go to http://localhost:8000 or http://127.0.0.1:8000.")



def start_meteor_production_mode(doc, current_dev_app, server_port=None, ddp_port=None, site=None, debug=False,
			update=False, force=False, user=None, bench="..", mac_sup_prefix_path="/usr/local", file_to_add=None, file_to_remove=None):
	from fluorine.commands_helpers.meteor import MeteorProduction
	"""
	from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import remove_from_procfile, make_final_app_client, save_to_procfile, check_meteor_apps_created
	from fluorine.utils.meteor.utils import make_meteor_files, cmd_packages_from
	from fluorine.commands_helpers.meteor import MeteorContext
	from fluorine.utils import meteor_config


	#meteor_config = get_meteor_configuration_file()
	#prodmode = check_prod_mode()
	#if state == "off" and devmode == 0 and prodmode:
	doc.fluorine_state = "off"
	doc.fluor_dev_mode = 0
	meteor_config["stop"] = 1
	#meteor_config["developer_mode"] = 0
	meteor_config["production_mode"] = 1
	#update_common_config(meteor_config)

	#also save meteor_config to file
	doc.save()

	click.echo("Checking for meteor apps folder. Please wait.")
	if not check_meteor_apps_created(doc):
		click.echo("Please install meteor app first. From command line issue 'bench fluorine create-meteor-apps.'")
		return

	if _check_updates(bench=bench):
		click.echo("There are updates in your apps. To update production you must press button 'run_updates' in fluorine app.")
		return

	mgh._check_custom_mongodb(doc)
	remove_from_procfile()

	m_ctx = MeteorContext()
	m_ctx.meteor_init(mongo_custom=True)
	#get context to work with desk
	m_ctx.make_context()

	#only save the meteor packages installed in fluorine if fluorine app is in development.
	if current_dev_app != "fluorine" or force:
		#prepare_client_files(current_dev_app)
		cmd_packages_from(current_dev_app)
	#If debug then do not run frappe setup production and test only meteor in production mode.
	click.echo("Make meteor bundle for Desk APP")
	make_meteor_files(doc.fluor_meteor_host, doc.fluor_meteor_port, doc.ddpurl, doc.meteor_target_arch)
	#Patch: run twice for fix nemo64:bootstrap less problem
	click.echo("Run twice to patch nemo64:bootstrap less problem")
	click.echo("Make meteor bundle for WEB")
	make_meteor_files(doc.fluor_meteor_host, doc.fluor_meteor_port, doc.ddpurl, doc.meteor_target_arch)

	#context = frappe._dict()
	#build_meteor_context(context, meteor_desk_app)
	#make_meteor_props(context, meteor_desk_app)
	m_ctx.make_meteor_properties()

	#mh.copy_meteor_runtime_config()
	click.echo("Make build.json for meteor_app")
	make_final_app_client()
	click.echo("Run npm install for meteor server:")
	mh.run_npm()
	click.echo("Make production links.")
	mh.make_production_link()
	click.echo("Make js and css hooks.")

	#common_site_config.json must have meteor_dns for production mode or use default
	ch.generate_nginx_supervisor_conf(doc, user=user, debug=debug, update=update, bench=bench, mac_sup_prefix_path=mac_sup_prefix_path)

	#hosts_web, hosts_app = get_hosts(doc, production=True)
	ch._generate_fluorine_nginx_conf(production=True, site=site)

	if debug:
		mh.make_start_meteor_script(doc)
		save_to_procfile(doc, production_debug=True)

	sh.build_assets(bench_path=bench)

	mh.remove_public_link()

	sh.start_nginx_supervisor_services(debug=debug)
	"""


	mp = MeteorProduction(doc, current_dev_app, site=site, debug=debug, update=update, force=force, user=user, server_port=server_port,
						ddp_port=ddp_port, bench=bench, mac_sup_prefix_path=mac_sup_prefix_path, file_to_add=file_to_add, file_to_remove=file_to_remove)

	mp.start()

	if debug:
		click.echo("Please issue `bench start` and go to http://localhost or http://127.0.0.1.")
	else:
		click.echo("Please go to http://localhost or http://127.0.0.1.")

	return True

	#else:
	#	click.echo("You must set state to off in fluorine doctype and remove developer mode.")
	#	return False

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



commands = [
	mongodb_conf,
	nginx_conf,
	set_current_app,
	cmd_create_meteor_apps,
	cmd_reset_meteor_packages,
	cmd_add_meteor_packages,
	cmd_remove_meteor_packages,
	cmd_restore_common_config,
	cmd_get_state,
	cmd_get_apps_packages_list,
	#setup_production,
	cmd_update_version,
	cmd_check_updates,
	setState
]