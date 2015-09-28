__author__ = 'luissaguas'


import frappe, click, os
from fluorine.utils import whatfor_all, meteor_desk_app, meteor_web_app


def get_meteor_app_files():
	from shutil import copyfile

	meteor_app_path = os.path.join("assets", "js", meteor_desk_app)
	meteordesk_path = os.path.join(meteor_app_path, "meteordesk")
	app_include_js = []
	app_include_css = []

	if os.path.exists(meteordesk_path):
		app_include_js.append("assets/js/%s/meteor_runtime_config.js" % meteor_desk_app)
		progfile = frappe.get_file_json(os.path.join(meteordesk_path, "program.json"))
		manifest = progfile.get("manifest")
		for obj in manifest:
			if obj.get("type") == "js" and obj.get("where") == "client":
				app_include_js.append("assets/js/%s/meteordesk%s" % (meteor_desk_app, obj.get("url")))#+ obj.get("url"))
			elif obj.get("type") == "css" and obj.get("where") == "client":
				app_include_css.append("assets/js/%s/meteordesk%s" % (meteor_desk_app, obj.get("url")))

		fluorine_path = frappe.get_app_path("fluorine")
		src = os.path.join(fluorine_path, "public", meteor_desk_app, "meteor_runtime_config.js")
		dst = os.path.join(meteor_app_path, "meteor_runtime_config.js")
		copyfile(src, dst)

	return app_include_js, app_include_css


#Run npm install for meteor server
def run_npm(site):
	from fluorine.utils import get_meteor_final_name
	from fluorine.utils.file import get_path_reactivity
	import subprocess

	final_app_name_desk = get_meteor_final_name(site, meteor_desk_app)
	final_app_name_web = get_meteor_final_name(site, meteor_web_app)
	path_reactivity = get_path_reactivity()
	final_app_path = os.path.join(path_reactivity, final_app_name_desk, "bundle", "programs", "server")
	final_web_path = os.path.join(path_reactivity, final_app_name_web, "bundle", "programs", "server")
	click.echo("npm install meteor server Desk APP")
	subprocess.call(["npm", "install"], cwd=final_app_path)
	click.echo("npm install meteor server WEB")
	subprocess.call(["npm", "install"], cwd=final_web_path)


def make_start_meteor_script(doc, site):
	from fluorine.utils import get_meteor_final_name
	from fluorine.utils.procfile import get_root_exports
	from fluorine.utils.mongodb.utils import get_mongo_exports
	from fluorine.utils.file import get_path_reactivity, save_file
	from distutils.spawn import find_executable
	import stat


	react_path = get_path_reactivity()

	node = find_executable("node") or find_executable("nodejs")

	for app in whatfor_all:
		final_app_name = get_meteor_final_name(site, app)
		meteor_final_path = os.path.join(react_path, final_app_name, "bundle/exec_meteor")
		exp_mongo, mongo_default = get_mongo_exports(doc)
		mthost, mtport, forwarded_count = get_root_exports(app)
		msf = get_meteor_settings(app, production=True)
		if msf:
			msf = "export %s" % msf
		script =\
"""#!/usr/bin/env bash
export ROOT_URL=%s
export PORT=%s
%s
%s
%s

%s main.js""" % (mthost, mtport, forwarded_count, exp_mongo, msf, node)
		save_file(meteor_final_path, script)

		st = os.stat(meteor_final_path)
		os.chmod(meteor_final_path, st.st_mode | stat.S_IEXEC)


def get_meteor_settings(app, production=False):
	from fluorine.utils import meteor_config
	from fluorine.utils.file import readlines

	msf=""
	msfile = meteor_config.get("meteor_settings", {}).get(app)
	content = ""
	if production and msfile:
		if os.path.exists(msfile):
			lines = readlines(msfile)
			for line in lines:
				content = content + line.strip(" \t\n\r")
			msf = "METEOR_SETTINGS='%s'" % content
	elif msfile:
		msf = " --settings %s" % msfile

	return msf


def get_meteor_environment(doc, whatfor):
	from fluorine.utils.mongodb.utils import get_mongo_exports
	from fluorine.utils.procfile import get_root_exports

	conf = frappe._dict()

	#METEOR MAIL
	if hasattr(doc, "mailurl"):
		conf.mail_url = ", MAIL_URL='{mail_url}'".format(doc.mailurl)
	else:
		conf.mail_url = ""

	mongo_url, mongo_default = get_mongo_exports(doc)

	conf.mongo_url = mongo_url.strip().replace("export MONGO_URL=", "")
	conf.root_url, conf.port, forwarded_count = get_root_exports(whatfor)
	conf.forwarded_count = forwarded_count.replace("export", "").strip()
	msettings = get_meteor_settings(whatfor, production=True)
	if msettings:
		conf.msettings = "%s, " % msettings
	else:
		conf.msettings = ""

	#SUPERVISOR
	env = "{msettings}PORT={port}, ROOT_URL='{root_url}', MONGO_URL='{mongo_url}'{mail_url}, {forwarded_count}".format(**conf)

	return env


def remove_from_assets():
	try:
		meteor_path = os.path.join("assets", "js", meteor_web_app)
		os.unlink(meteor_path)
	except:
		pass


def check_updates(whatfor, bench=".."):
	from fluorine.utils.apps import get_active_apps
	from fluorine.utils.reactivity import meteor_config
	from bench_helpers import get_current_version
	import semantic_version

	apps = get_active_apps(whatfor)
	versions = meteor_config.get("versions")

	if not versions:
		return False

	app_version = versions.get(whatfor)

	for app in apps:
		curr_version = get_current_version(app, bench=bench)
		old_version = app_version.get(app, None)
		if not old_version or curr_version > semantic_version.Version(old_version):
			return True


	return False

def update_versions(whatfor=None, bench=".."):
	from fluorine.utils.apps import get_active_apps
	from bench_helpers import get_current_version
	from fluorine.utils.reactivity import meteor_config
	from fluorine.utils.meteor.utils import update_common_config

	meteor_config.pop("versions", None)
	versions = meteor_config["versions"] = frappe._dict({meteor_desk_app:{}, meteor_web_app:{}})

	if not whatfor:
		whatfor = whatfor_all
	elif isinstance(whatfor, basestring):
		whatfor = [whatfor]

	for w in whatfor:
		apps = get_active_apps(w)
		app_version = versions.get(w)
		for app in apps:
			version = get_current_version(app, bench=bench)
			app_version[app] = str(version)

	update_common_config(meteor_config)


def meteor_run(app, app_path, mongo_custom=False):
	from fluorine.utils.meteor.utils import PORT
	from fluorine.utils.reactivity import meteor_config
	import subprocess, shlex


	print "starting meteor..."
	env = None
	if mongo_custom:
		mongo_conf = meteor_config.get("meteor_mongo", None)
		if mongo_conf and mongo_conf.get("type", None) != "default":
			db = mongo_conf.get("db").strip(' \t\n\r')
			host = mongo_conf.get("host").replace("http://","").replace("mongodb://","").strip(' \t\n\r')
			mgport = mongo_conf.get("port")
			env = os.environ.copy()
			env["MONGO_URL"] = "mongodb://%s:%s/%s" % (host, mgport, db)

	args = shlex.split("meteor --port %s" % PORT.get(app))
	meteor = subprocess.Popen(args, cwd=app_path, shell=False, stdout=subprocess.PIPE, env=env)
	while True:
		line = meteor.stdout.readline()
		if "App running at" in line:
			meteor.terminate()
			break
		click.echo(line)


class MeteorDevelop(object):

	def __init__(self, doc, current_dev_app, site=None, mongo_custom=False, server_port=None, ddp_port=None, bench="..",
				file_to_add=None, file_to_remove=None, skip_package_check_updates=False, guess_mongodb_port=None):
		self.doc = doc
		self.site = site
		self.bench = bench
		self.mongo_custom = mongo_custom
		self.server_port = server_port
		self.ddp_port = ddp_port
		self.current_dev_app = current_dev_app
		self.file_add = file_to_add
		self.file_remove = file_to_remove
		self.skip_package_check_updates = skip_package_check_updates
		self.guess_mongodb_port = guess_mongodb_port

	def start(self):
		from fluorine.utils import meteor_config
		from fluorine.utils.context import MeteorContext

		self.m_ctx = MeteorContext(self.site, production=False)
		self.meteor_config = meteor_config

		if not self.check_meteor_apps():
			raise click.ClickException("Please install meteor app first. From command line issue 'bench fluorine create-meteor-apps.'")

		self.update_doctype()
		self.update_meteor_conf_file()
		update_url_port(self.doc, self.meteor_config, self.server_port, self.ddp_port)
		self.make_mongo()
		#self.doc.save()
		self.check_apps_updates()
		self.update_list_packages()
		self.make_apps_context()
		self.make_meteor_properties()
		self.remove_from_assets()
		self.save_procfile()
		self.generate_configs()
		self.start_services()

	def update_doctype(self):
		self.doc.fluor_dev_mode = 1
		self.doc.fluorine_state = "on"

	def update_meteor_conf_file(self):
		from fluorine.utils import meteor_config

		meteor_config["developer_mode"] = 1
		meteor_config["production_mode"] = 0
		meteor_config["stop"] = 0

	def save_doc_and_meteor_config(self):
		self.doc.save()

	def check_meteor_apps(self):
		from fluorine.utils.apps import check_meteor_apps_created
		#from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import check_meteor_apps_created
		click.echo("Checking for meteor apps folder. Please wait.")
		return check_meteor_apps_created(self.doc)

	def check_apps_updates(self):

		click.echo("Checking for fluorine apps updates. Please wait.")
		for whatfor in whatfor_all:
			if check_updates(whatfor, bench=self.bench):
				click.echo("%s: updating versions." % whatfor)
				update_versions(whatfor=whatfor, bench=self.bench)
			else:
				click.echo("%s: fluorine apps are updated." % whatfor)
		return

	def update_list_packages(self):
		from fluorine.utils.meteor.packages import update_packages_list

		if not self.skip_package_check_updates:
			update_packages_list(self.current_dev_app, file_add=self.file_add, file_remove=self.file_remove)

	def make_apps_context(self):
		self.m_ctx.meteor_init(mongo_custom=True)
		#get context to work with desk
		self.m_ctx.make_context()

	def make_mongo(self):
		#from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import make_mongodb_default
		from fluorine.utils.mongodb.utils import make_mongodb_default
		from fluorine.utils import meteor_config
		from fluorine.utils.meteor.utils import PORT

		if not self.mongo_custom:
			meteor_config.pop("meteor_mongo", None)
			make_mongodb_default(meteor_config, self.doc.fluor_meteor_port or PORT.meteor_web, self.guess_mongodb_port)
			mongo_default = 0
		else:
			mongo_conf = meteor_config.get("meteor_mongo", None)
			if not mongo_conf or mongo_conf.get("type", None) == "default":
				raise click.ClickException("You must set mongo custom in reactivity/common_site_config.json or remove --custom-mongo option to use the mongo default.")

			mongo_default = 1

		self.doc.check_mongodb = mongo_default

	def make_meteor_properties(self):
		click.echo("Make meteor properties.")
		self.m_ctx.make_meteor_properties(meteor_desk_app)

	def remove_from_assets(self):
		remove_from_assets()

	def save_procfile(self):
		from fluorine.utils.procfile import save_to_procfile

		save_to_procfile(self.doc, self.site)

	def generate_configs(self):
		from fluorine.commands_helpers import config
		from fluorine.commands_helpers import bench_generate_nginx_config
		import platform

		bench_generate_nginx_config(bench=self.bench)
		config._generate_fluorine_nginx_conf(production=False, site=self.site)
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
			raise click.ClickException("nginx link not set. You must make a symlink to frappe-bench/config/nginx.conf from nginx conf folder.")

	def start_services(self):
		from fluorine.commands_helpers import services

		services.start_nginx_supervisor_services(debug=True)


class MeteorProduction(object):

	def __init__(self, doc, current_dev_app, site=None, debug=False, update=False, force=False, user=None, server_port=None, ddp_port=None, bench="..",
				mac_sup_prefix_path="/usr/local", file_to_add=None, file_to_remove=None):
		self.doc = doc
		self.current_dev_app = current_dev_app
		self.site = site
		self.debug = debug
		self.update = update
		self.force = force
		self.user = user
		self.bench = bench
		self.mac_sup_prefix_path = mac_sup_prefix_path
		self.server_port = server_port
		self.ddp_port = ddp_port
		self.file_add = file_to_add
		self.file_remove = file_to_remove

	def start(self):
		from fluorine.utils import meteor_config
		from fluorine.utils.context import MeteorContext

		self.m_ctx = MeteorContext(self.site)
		self.meteor_config = meteor_config

		if not self.check_meteor_apps():
			raise click.ClickException("Please install meteor app first. From command line issue 'bench fluorine create-meteor-apps.'")

		self.update_meteor_conf_file()
		self.update_doctype()
		update_url_port(self.doc, self.meteor_config, self.server_port, self.ddp_port)
		#self.doc.save()
		self.check_apps_updates()
		self.check_hosts()

		self.check_custom_mongo()
		self.remove_from_procfile()

		self.remove_old_final_folders()
		self.make_apps_context()
		self.make_packages_list()

		self.make_meteor_bundle()

		self.make_meteor_properties()
		self.build_json()
		self.npm_install()
		self.generate_configs()
		self.make_script_startup()

		self.build_assets()
		self.remove_public_link()
		self.remove_build()
		self.update_file_map_site()
		self.start_services()


	def update_file_map_site(self):
		from fluorine.utils import update_file_map_site, get_meteor_final_name


		fms = {"%s" % self.site: "%s" % self.site}
		update_file_map_site(fms)

	def update_doctype(self):
		self.doc.fluorine_state = "off"
		self.doc.fluor_dev_mode = 0

	def update_meteor_conf_file(self):

		self.meteor_config["stop"] = 1
		self.meteor_config["production_mode"] = 1

	def save_doc_and_meteor_config(self):
		self.doc.save()

	def check_hosts(self):
		from fluorine.commands_helpers import get_hosts, get_host_address
		from fluorine.utils.meteor.utils import PORT

		self.hosts_web, self.hosts_app = get_hosts(self.doc, production=True)

		if not self.hosts_web:
			raise click.ClickException("You need to provide at least one web host.")

		if not self.hosts_app:
			#must have at least one host app (desk)
			mthost = get_host_address(self.doc).replace("http://", "").replace("https://", "")
			port = (self.doc.fluor_meteor_port + PORT.port_inc) if self.doc.fluor_meteor_port else PORT.get(meteor_desk_app)
			click.echo("One host desk at least must be provided. There are none, so force one: %s:%s" % (mthost, port))
			self.hosts_app.append("%s:%s" % (mthost, port))


	def check_meteor_apps(self):
		from fluorine.utils.apps import check_meteor_apps_created
		#from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import check_meteor_apps_created
		click.echo("Checking for meteor apps folder. Please wait.")
		return check_meteor_apps_created(self.doc)

	def check_apps_updates(self):
		#from fluorine.utils import make_list_installed_packages, get_list_installed_packages

		#if not get_list_installed_packages(whatfor):
			#make_list_installed_packages()
		click.echo("Checking for fluorine apps updates. Please wait.")
		for whatfor in whatfor_all:
			if check_updates(whatfor, bench=self.bench):
				click.echo("%s: updating versions." % whatfor)
				update_versions(whatfor=whatfor, bench=self.bench)
			else:
				click.echo("%s: fluorine apps are updated." % whatfor)
		return

	def check_custom_mongo(self):
		from fluorine.commands_helpers import mongo
		mongo._check_custom_mongodb(self.doc)

	def make_apps_context(self):
		self.m_ctx.meteor_init(mongo_custom=True)
		#get context to work with desk
		self.m_ctx.make_context()

	def make_packages_list(self):
		from fluorine.utils.meteor.packages import cmd_packages_update
		#only save the meteor packages installed in fluorine if fluorine app is in development.
		if self.current_dev_app != "fluorine" or self.force:
			#prepare_client_files(current_dev_app)
			cmd_packages_update(self.current_dev_app)

	def remove_old_final_folders(self):
		from fluorine.utils.meteor.utils import remove_old_final_folders

		remove_old_final_folders(self.site)

	def make_meteor_bundle(self):
		from fluorine.utils.meteor.utils import make_meteor_files
		#If debug then do not run frappe setup production and test only meteor in production mode.
		click.echo("Make meteor bundle for Desk APP")
		make_meteor_files(self.doc.fluor_meteor_host, self.doc.fluor_meteor_port, self.doc.meteor_target_arch, self.site)
		#Patch: run twice for fix nemo64:bootstrap less problem
		click.echo("Run twice to patch nemo64:bootstrap less problem")
		click.echo("Make meteor bundle for WEB")
		make_meteor_files(self.doc.fluor_meteor_host, self.doc.fluor_meteor_port, self.doc.meteor_target_arch, self.site)

	def make_meteor_properties(self):
		click.echo("Make meteor properties.")
		self.m_ctx.make_meteor_properties(meteor_desk_app)

	def build_json(self):
		#from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import make_final_app_client
		from fluorine.utils.finals import make_final_app_client

		click.echo("Make build.json for meteor_app.")
		make_final_app_client(self.site)

	def npm_install(self):
		click.echo("Run npm install for meteor server:")
		run_npm(self.site)

	#Not called. To Remove
	def make_production_link(self):
		from fluorine.utils.finals import make_production_link

		click.echo("Make production links.")
		make_production_link(self.site)

	def remove_from_procfile(self):
		#from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import remove_from_procfile
		from fluorine.utils.procfile import remove_from_procfile

		remove_from_procfile(self.site)

	def generate_configs(self):
		from fluorine.commands_helpers import config
		#common_site_config.json must have meteor_dns for production mode or use default
		config.generate_nginx_supervisor_conf(self.doc, self.site, user=self.user, debug=self.debug, update=self.update, bench=self.bench, mac_sup_prefix_path=self.mac_sup_prefix_path)

		config._generate_fluorine_nginx_conf(hosts_app=self.hosts_app, hosts_web=self.hosts_web, production=True, site=self.site)

	def make_script_startup(self):
		if self.debug:
			from fluorine.utils.procfile import save_to_procfile

			make_start_meteor_script(self.doc, self.site)
			save_to_procfile(self.doc, self.site, production_debug=True)

	def build_assets(self):
		from fluorine.commands_helpers import services

		services.build_assets(bench_path=self.bench)

	def remove_public_link(self):
		from fluorine.utils.finals import remove_public_link

		remove_public_link()

	def remove_build(self):
		from fluorine.utils.finals import remove_build

		remove_build()

	def start_services(self):
		from fluorine.commands_helpers import services

		services.start_nginx_supervisor_services(debug=self.debug)


def update_url_port(doc, meteor_config, server_port, ddp_port):

	if server_port:
		from fluorine.commands_helpers import get_host_address
		host_address = get_host_address(doc)
		doc.fluor_meteor_host = host_address + ":" + server_port
		meteor_config["meteor_dev"]["host"] = doc.fluor_meteor_host

	if ddp_port:
		from fluorine.commands_helpers import get_ddp_address
		ddp_address = get_ddp_address(doc)
		doc.ddpurl = ddp_address + ":" + ddp_port
		meteor_config["meteor_dev"]["meteor_app"]["ddpurl"] = doc.ddpurl
