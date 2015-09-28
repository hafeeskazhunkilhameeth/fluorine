__author__ = 'luissaguas'


import frappe, os, logging


list_ignores = None


def make_ignor_apps_list():
	from fluorine.utils import APPS as apps, whatfor_all, meteor_desk_app, meteor_web_app
	from fluorine.commands_helpers import get_default_site
	from fluorine.utils import meteor_config


	global list_ignores

	if list_ignores != None:
		return list_ignores

	list_ignores = frappe._dict({meteor_web_app:{}, meteor_desk_app:{}})

	logger = logging.getLogger("frappe")

	current_site = get_default_site()

	curr_app = meteor_config.get("current_dev_app", "").strip()
	know_apps = apps[::]
	if curr_app != know_apps[-1]:
		#set current dev app in last
		apps.remove(curr_app)
		apps.append(curr_app)

	for whatfor in whatfor_all:
		pfs_in = ProcessFileSystem(whatfor, curr_app)
		##keys are the sites and value is a list of dicts of apps and server_writes to use in the site
		#list_only_for_sites = {}
		only_for_sites = {current_site: []}
		list_know_apps = know_apps[::]
		# Apps removed by current dev app does not remove anything.
		# The same is true for first installed apps that do not removed anything if they are removed by last installed apps.
		while list_know_apps:
			app = list_know_apps.pop()
			app_path = frappe.get_app_path(app)
			meteor_app = os.path.join(app_path, "templates", "react", whatfor)

			if not os.path.exists(meteor_app):
				try:
					list_know_apps.remove(app)
				except:
					pass
				continue

			perm_path = os.path.join(app_path, "templates", "react", whatfor, "permissions.json")
			if os.path.exists(perm_path):
				conf_file = frappe.get_file_json(perm_path)
				conf_apps = conf_file.get("apps") or {}
				list_only_for_sites = get_list_only_apps_for_site(app, whatfor, conf_in=conf_apps)
				only_for_sites.update(list_only_for_sites)
				pfs_in.feed_apps(conf_apps)
				apps_remove = pfs_in.get_apps_remove()
				if not is_app_for_site(app, list_only_for_sites):
					apps_remove.add(app)
				for r in apps_remove:
					try:
						list_know_apps.remove(r)
					except:
						pass
			else:
				only_for_sites.get(current_site).append(app)

		list_apps_remove = pfs_in.get_apps_remove()#get_permission_files_json(whatfor)

		list_ignores.get(whatfor).update({
			"remove":{
				"apps": list_apps_remove,
			},
			"only_for_sites": only_for_sites#,
		})

		#logger.error("list_ignores inside highlight {} w {} apps {}".format(list_ignores.get(whatfor), whatfor, know_apps))

	return list_ignores


def is_app_for_site(app, list_only_for_sites, site=None):
	from fluorine.commands_helpers import get_default_site

	current_site = site
	if not current_site:
		current_site = get_default_site()

	logger = logging.getLogger("frappe")
	#logger.error("current site {} app {} list {}".format(current_site, app, list_only_for_sites))
	if app in list_only_for_sites.get(current_site):
		return True

	return False


def get_list_only_apps_for_site(app, whatfor, conf_in=None):
	from fluorine.commands_helpers import get_default_site
	from fluorine.utils import is_valid_site

	list_only_for_sites = {}
	current_site = get_default_site()

	if not conf_in:
		app_path = frappe.get_app_path(app)
		perm_path = os.path.join(app_path, "templates", "react", whatfor, "permissions.json")
		if os.path.exists(perm_path):
			conf_file = frappe.get_file_json(perm_path)
			conf_in = conf_file.get("IN") or conf_file.get("in") or {}
		else:
			return list_only_for_sites

	sites = conf_in.get("only_for_sites") or []
	if not sites:
		#if get nothing for app it is because this app is for all sites
		if not list_only_for_sites.get(current_site):
			list_only_for_sites[current_site] = []
		list_only_for_sites.get(current_site).append(app)

	for site in sites:
		if not is_valid_site(site):
			continue

		if not list_only_for_sites.get(site):
			list_only_for_sites[site] = []
		list_only_for_sites.get(site).append(app)

	return list_only_for_sites



class ProcessFileSystem(object):

	def __init__(self, whatfor, curr_dev_app):
		self.whatfor = whatfor
		self.curr_dev_app = curr_dev_app

		self.list_apps_add = set([])
		self.list_apps_remove = set([])

		self.logger = logging.getLogger("frappe")

	def feed_apps(self, conf_file):
		self.process_permission_apps(conf_file)

	def get_apps_add(self):
		return self.list_apps_add

	def get_apps_remove(self):
		return self.list_apps_remove

	def process_permission_apps(self, conf_file):
		from fluorine.utils import meteor_config, is_making_production

		devmode = meteor_config.get("developer_mode")
		prodmode = meteor_config.get("production_mode") or is_making_production()

		apps = conf_file.get("apps") or {}
		if self.curr_dev_app in apps:
			apps.remove(self.curr_dev_app)


		for k, v in apps.iteritems():
			constrains = v.get("constrains")
			if v.get("remove", 0):
				if k not in self.list_apps_add:
					if constrains == "dm" and not devmode or constrains == "pm" and not prodmode:
						continue
					self.list_apps_remove.add(k)
			elif v.get("add", 0):
				if k not in self.list_apps_remove:
					self.list_apps_add.add(k)

