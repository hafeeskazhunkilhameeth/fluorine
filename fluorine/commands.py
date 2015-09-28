from __future__ import unicode_literals, absolute_import
__author__ = 'luissaguas'


import click
from fluorine.utils import whatfor_all
from fluorine.commands_helpers import *
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


def _reset_packages(app, whatfor, file_add=None, file_remove=None):
	from fluorine.utils.meteor.packages import meteor_reset_package

	meteor_reset_package(app, whatfor, file_add=file_add, file_remove=file_remove)


def _reset_packages_all(file_add=None, file_remove=None):
	from fluorine.utils.apps import get_active_apps

	for whatfor in whatfor_all:
		apps = get_active_apps(whatfor)
		for app in apps:
			_reset_packages(app, whatfor, file_add=file_add, file_remove=file_remove)


def remove_meteor_packages(apps=None, file_remove=None):
	from fluorine.utils.meteor.packages import meteor_remove_package
	from fluorine.utils.apps import get_active_apps

	for whatfor in whatfor_all:
		if not apps:
			apps = get_active_apps(whatfor)
		for app in apps:
			meteor_remove_package(app, whatfor, file_remove=file_remove)


def add_meteor_packages(apps=None, file_add=None):
	from fluorine.utils.meteor.packages import meteor_add_package
	from fluorine.utils.apps import get_active_apps

	for whatfor in whatfor_all:
		if not apps:
			apps = get_active_apps(whatfor)
		for app in apps:
			meteor_add_package(app, whatfor, file_add=file_add)

def _cmd_create_meteor_apps():
	from fluorine.utils.install import create_meteor_apps
	from fluorine.utils.apps import check_meteor_apps_created

	if not check_meteor_apps_created(with_error=False):
		create_meteor_apps()
		add_meteor_packages()


@click.command('make-fluorine-app')
@click.argument('app')
@click.option('--web', is_flag=True, help='Make only for web.')
@click.option('--desk', is_flag=True, help='Make only for desk.')
def cmd_make_fluorine_app(app, web=False, desk=False):
	"""Turn any frappe module into a fluorine app.\n
	Default is to make a web and a desk app."""
	from shutil import copyfile

	try:
		app_path = frappe.get_app_path(app)
	except:
		meteor_echo("%s: This app does not exist." % app)
		return

	whatfor = whatfor_all

	if web:
		whatfor = meteor_web_app
	elif desk:
		whatfor = meteor_desk_app

	fluorine_path = frappe.get_app_path("fluorine")

	for w in whatfor:
		frappe.create_folder(os.path.join(app_path, "templates", "react"), with_init=True)
		frappe.create_folder(os.path.join(app_path, "templates", "react", w), with_init=True)


	dst = os.path.join(app_path, "templates", "react", ".gitignore")
	if not os.path.exists(dst):
		src = os.path.join(fluorine_path, "templates", "react",".gitignore")
		copyfile(src, dst)


@click.command('check-updates')
@click.option('--site', default=None, help='The site to work with. If not provided it will use the currentsite')
def cmd_check_updates(site=None):
	"""Check for update in fluorine apps.\n
	This check only if version is changed from last check."""
	from fluorine.commands_helpers.meteor import check_updates

	if site == None:
		site = get_default_site()

	bench = "../../bench-repo/"
	start_frappe_db(site)

	for whatfor in whatfor_all:
		if check_updates(whatfor, bench=bench):
			click.echo("%s: fluorine apps needs to update." % whatfor)
		else:
			click.echo("%s: fluorine apps are updated." % whatfor)


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
	"""Remove meteor packages from an app."""
	from fluorine.utils.apps import is_valid_fluorine_app
	from fluorine.commands_helpers.config import get_custom_packages_files

	if site == None:
		site = get_default_site()

	start_frappe_db(site)

	if app and not is_valid_fluorine_app(app):
		click.echo("Sorry. App %s does not exist as meteor app." % app)
		return

	file_add, file_remove = get_custom_packages_files()

	if app:
		app = [app]

	remove_meteor_packages(apps=app, file_remove=file_remove)



@click.command('add-meteor-packages')
@click.option('--app', default=None, help='The name of the fluorine app to reset packages.')
@click.option('--site', default=None, help='The site to work with. If not provided it will use the currentsite')
def cmd_add_meteor_packages(app=None, site=None):
	"""Add meteor packages from an app."""
	from fluorine.utils.apps import is_valid_fluorine_app
	from fluorine.commands_helpers.config import get_custom_packages_files

	if site == None:
		site = get_default_site()

	start_frappe_db(site)

	if app and not is_valid_fluorine_app(app):
		click.echo("Sorry. App %s does not exist as meteor app." % app)
		return

	file_add, file_remove = get_custom_packages_files()

	if app:
		app = [app]

	add_meteor_packages(apps=app, file_add=file_add)


@click.command('reset-meteor-packages')
@click.option('--app', default=None, help='The name of the fluorine app to reset packages.')
@click.option('--site', default=None, help='The site to work with. If not provided it will use the currentsite')
def cmd_reset_meteor_packages(app=None, site=None):
	"""Reset meteor packages."""
	from fluorine.utils.apps import is_valid_fluorine_app
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
def cmd_create_meteor_apps():
	"""Create meteor apps. This create meteor web and meteor desk apps."""
	_cmd_create_meteor_apps()


@click.command('get-apps-packages-list')
@click.option('--custom-file-to-add', default=None, help='Name of the custom file with packages to add.')
@click.option('--custom-file-to-remove', default=None, help='Name of the custom file with packages to remove.')
def cmd_get_apps_packages_list(custom_file_to_add=None, custom_file_to_remove=None):
	"""Get a list of packages to install and to remove by meteor app. This also show the packages already installed."""
	from fluorine.utils.meteor.packages import print_meteor_packages_list, get_package_list_updates

	curr_app = get_current_dev_app()
	for whatfor in whatfor_all:
		pckg_add, pckg_remove, i_pckgs = get_package_list_updates(curr_app, whatfor, file_add=custom_file_to_add, file_remove=custom_file_to_remove)
		print_meteor_packages_list(whatfor, pckg_add, pckg_remove, i_pckgs)

@click.command('get-current-state')
def cmd_get_state():
	"""Get the current state. The states are: developer mode, production mode or stop."""
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


@click.command('set-current-dev-app')
@click.argument('app')
def set_current_app(app):
	"""Set the current app for develop."""
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
@click.option('--site', default=None, help='The site to work with. If not provided it will use the currentsite.')
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
@click.option('--guess-mongodb-port', help='Try to guess the mongodb port.', is_flag=True)
def setState(state, site=None, custom_mongo=None, user=None, server_port=None, ddp_port=None, mac_sup_prefix_path=None, debug=None,
			update=None, force=None, custom_file_to_add=None, custom_file_to_remove=None, skip_package_check_updates=False, guess_mongodb_port=None):
	"""Prepare Frappe for meteor.\n
		STATE: \n
		`develop` to enter in developer mode;\n
		`production` to enter in production mode;\n
		`stop` to enter in original frappe web.
	"""
	import getpass
	from fluorine.utils.meteor.utils import update_common_config

	if site == None:
		site = get_default_site()
	else:
		from fluorine.utils.reactivity import meteor_config
		from fluorine.utils import is_valid_site
		if not is_valid_site(site):
			meteor_echo("Sorry, but the site %s is not a valid site." % site)
			return
		meteor_config["site"] = site
		update_common_config(meteor_config)

	if not user:
		user = getpass.getuser()

	bench = "../../bench-repo/"

	color = click_format("*" * 80)
	_setState(site=site, state=state, debug=debug, update= update, force=force, mongo_custom=custom_mongo, user=user, bench=bench,
		server_port=server_port, ddp_port=ddp_port, mac_sup_prefix_path=mac_sup_prefix_path, file_to_add=custom_file_to_add,
			file_to_remove=custom_file_to_remove, skip_package_check_updates=skip_package_check_updates, guess_mongodb_port=guess_mongodb_port)
	click_format("*" * 80, color)


def _setState(site=None, state=None, debug=False, update=False, force=False, mongo_custom=False, user=None, bench="..",
			server_port=None, ddp_port=None, mac_sup_prefix_path="/usr/local", file_to_add=None, file_to_remove=None, skip_package_check_updates=False, guess_mongodb_port=None):
	from fluorine.utils.fcache import clear_frappe_caches
	from fluorine.utils.context import MeteorContext
	from fluorine.commands_helpers import stop_frappe_db, get_app_installed_site
	from fluorine.utils import make_list_sites

	make_list_sites(bench=bench)
	fluorine_site = get_app_installed_site(app="fluorine")

	doc = get_doctype("Fluorine Reactivity", fluorine_site)

	devmode = doc.fluor_dev_mode
	fluor_state = doc.fluorine_state

	what = state.lower()
	if what == "init":
		mctx = MeteorContext(site)
		mctx.meteor_init(mongo_custom=mongo_custom)
	elif what == "develop":
		from fluorine.commands_helpers import get_current_dev_app

		change_frappe_db(site)
		current_dev_app = get_current_dev_app()
		start_meteor(doc, current_dev_app, site=site, mongo_custom=mongo_custom, bench=bench, server_port=server_port, ddp_port=ddp_port,
					file_to_add=file_to_add, file_to_remove=file_to_remove, skip_package_check_updates=skip_package_check_updates, guess_mongodb_port=guess_mongodb_port)
	elif what == "stop":
		stop_meteor(doc, devmode, fluor_state, force=force, site=site, bench=bench)
	elif what == "production":
		from fluorine.commands_helpers import get_current_dev_app
		from fluorine.utils.reactivity import meteor_config

		change_frappe_db(site)
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

	stop_frappe_db()


def start_meteor(doc, current_dev_app, site=None, mongo_custom=False, server_port=None, ddp_port=None, bench="..", file_to_add=None, file_to_remove=None, skip_package_check_updates=False, guess_mongodb_port=None):

	from fluorine.commands_helpers.meteor import MeteorDevelop
	md = MeteorDevelop(doc, current_dev_app, site=site, mongo_custom=mongo_custom, server_port=server_port, ddp_port=ddp_port,
					bench=bench, file_to_add=file_to_add, file_to_remove=file_to_remove, skip_package_check_updates=skip_package_check_updates, guess_mongodb_port=guess_mongodb_port)
	md.start()
	fluorine_site = get_app_installed_site(app="fluorine")
	start_frappe_db(fluorine_site)
	md.save_doc_and_meteor_config()


def stop_meteor(doc, devmode, state, force=False, site=None, production=False, bench=".."):
	from fluorine.utils import meteor_config
	#from fluorine.utils.meteor.utils import update_common_config
	from fluorine.utils.procfile import remove_from_procfile


	doc.fluorine_state = "off"
	doc.fluor_dev_mode = 1
	meteor_config["stop"] = 1
	meteor_config["developer_mode"] = 1
	meteor_config["production_mode"] = 0
	#update_common_config(meteor_config)

	#also save meteor_config to file
	doc.save()

	remove_from_procfile(site)
	click.echo("Please issue `bench start` go to http://localhost:8000 or http://127.0.0.1:8000.")


def start_meteor_production_mode(doc, current_dev_app, server_port=None, ddp_port=None, site=None, debug=False,
			update=False, force=False, user=None, bench="..", mac_sup_prefix_path="/usr/local", file_to_add=None, file_to_remove=None):
	from fluorine.commands_helpers.meteor import MeteorProduction


	mp = MeteorProduction(doc, current_dev_app, site=site, debug=debug, update=update, force=force, user=user, server_port=server_port,
						ddp_port=ddp_port, bench=bench, mac_sup_prefix_path=mac_sup_prefix_path, file_to_add=file_to_add, file_to_remove=file_to_remove)

	mp.start()
	fluorine_site = get_app_installed_site(app="fluorine")
	start_frappe_db(fluorine_site)
	mp.save_doc_and_meteor_config()

	if debug:
		click.echo("Please issue `bench start` and go to http://localhost or http://127.0.0.1.")
	else:
		click.echo("Please go to http://localhost or http://127.0.0.1.")

	return True


@click.command('make-addfiles-template')
@click.option('--app', default=None, help='Name of app where to add the template file. Default to current app.')
@click.option('--author', default="fluorine", help='Name of the author.')
@click.option('--templates', default=None, help='A string with a comma separated names of meteor templates with files to add. Used with option --fluorine-template-name')
@click.option('--fluorine-template-path', default=None, help='If this is for addFiles of meteor templates you must indicate the path to fluorine template.')
def make_addfiles_template(app=None, templates=None, fluorine_template_path=None, author=None):
	from fluorine.utils.reactivity import meteor_config
	from jinja2 import Environment, PackageLoader
	from fluorine.utils.file import save_file

	if not app:
		app = meteor_config.get("current_dev_app")


	app_path = frappe.get_app_path(app)

	if fluorine_template_path:
		dest_path = os.path.join(app_path, "templates", "react", fluorine_template_path, "meteor_files.py")
	else:
		dest_path = os.path.join(app_path, "templates", "react", "meteor_files.py")


	is_meteor_template = fluorine_template_path != None

	env = Environment(loader=PackageLoader('fluorine', 'templates'), trim_blocks=True)
	jinja_template = env.get_template('meteor_files.template')

	template_content = jinja_template.render(**{
		"is_meteor_template": is_meteor_template,
		"meteor_templates": templates.split(",") if templates else [],
		"author": author or "fluorine"
	})

	rel_path = os.path.relpath(dest_path, app_path)
	if os.path.exists(dest_path):
		if not click.confirm('There is one file in %s for app %s. Do you want to continue?' % (rel_path, app)):
			meteor_echo("Did not save.")
			return
	if os.path.exists(os.path.dirname(dest_path)):
		save_file(dest_path, template_content)
		__init__file = os.path.join(os.path.dirname(dest_path), "__init__.py")
		print "init file {}".format(__init__file)
		if not os.path.exists(__init__file):
			from frappe.utils import touch_file
			touch_file(os.path.join(os.path.dirname(dest_path), "__init__.py"))
		meteor_echo("Saved to %s for app %s." % (rel_path, app))
	else:
		meteor_echo("Did not saved, path %s for app %s does not exist." % (os.path.dirname(rel_path), app))


def _check_updates(whatfor, bench="."):
	from fluorine.commands_helpers.meteor import check_updates

	click.echo("Checking for updates...")
	return check_updates(whatfor, bench=bench)

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
	cmd_make_fluorine_app,
	cmd_get_apps_packages_list,
	#setup_production,
	cmd_update_version,
	cmd_check_updates,
	setState,
	make_addfiles_template
]