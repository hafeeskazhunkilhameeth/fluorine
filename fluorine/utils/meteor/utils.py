# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'


import frappe
from collections import OrderedDict
import hashlib, json, os
from fluorine.utils import whatfor_all, meteor_desk_app, meteor_web_app


port_inc = 10
default_port_web = 3070
default_port_desk = default_port_web + port_inc
default_host = "http://127.0.0.1"
default_path_prefix = "/meteordesk"


PORT = frappe._dict({meteor_web_app: default_port_web, meteor_desk_app: default_port_desk, "port_inc": port_inc})

def meteor_url_path_prefix(whatfor):
	if whatfor == meteor_desk_app:
		url_prefix = default_path_prefix
	else:
		url_prefix = ""

	return url_prefix


def build_meteor_context(context, whatfor):
	from fluorine.utils.reactivity import meteor_config

	conf = meteor_config
	meteor = conf.get("meteor_dev") or {}

	meteor_conf = meteor.get(whatfor) or {}
	context.mport = meteor_conf.get("port") or PORT.get(whatfor)

	prefix = meteor_conf.get("ROOT_URL_PATH_PREFIX")
	if whatfor == meteor_web_app:
		host = meteor_conf.get("host") or meteor.get("host", default_host) + (prefix if prefix else "")
	else:
		host = meteor_conf.get("host") or meteor.get("host", default_host) + (prefix if prefix else default_path_prefix)

	ddpurl = meteor_conf.get("ddpurl")

	meteor_host =  host + ":" + str(context.mport)
	ddpurl_port = None
	if whatfor == meteor_web_app and ddpurl:
		ddpurl_port = ddpurl + (prefix if prefix else "")
	elif whatfor == meteor_desk_app:
		if not ddpurl:
			ddpurl = default_host
		ddpurl_port = ddpurl + (prefix if prefix else default_path_prefix)

	#host
	context.meteor_root_url = host
	#host:port
	context.meteor_root_url_port = meteor_host
	#hpst/prefix
	context.meteor_url_path_prefix = meteor_url_path_prefix(whatfor)
	#ddpurl:port
	context.meteor_ddp_default_connection_url = ddpurl_port


def get_meteor_release(cpath):

	if os.path.exists(cpath):
		config = frappe.get_file_json(cpath)
		return config.get("meteorRelease", "")

	return ""

def get_meteor_config_old(mthost, mtddpurlport, meteor_url_path_prefix, version, version_fresh, mrelease, whatfor, appId=None):

	from fluorine.utils import check_dev_mode

	devmod = check_dev_mode()

	meteor_config = """__meteor_runtime_config__ = {
		%(appId)s"meteorRelease": "%(meteorRelease)s",
		"ROOT_URL": "%(meteor_root_url)s",
		"ROOT_URL_PATH_PREFIX": "%(meteor_url_path_prefix)s",
		"autoupdateVersion": "%(meteor_autoupdate_version)s",
		"autoupdateVersionRefreshable": "%(meteor_autoupdate_version_freshable)s"%(meteor_ddp_default_connection_url)s
	};
	%(jquery)s
	""" % {"appId": "'appId':'" + appId + "',\n\t\t" if devmod else "", "meteorRelease": mrelease, "meteor_root_url": mthost, "meteor_url_path_prefix": meteor_url_path_prefix,
				"meteor_autoupdate_version": version, "meteor_autoupdate_version_freshable": version_fresh,
				"meteor_ddp_default_connection_url": ",\n\t\t'DDP_DEFAULT_CONNECTION_URL': '" + mtddpurlport + "'" if whatfor == meteor_desk_app else "", "jquery": """
if (typeof Package === 'undefined')
	Package = {};
Package.jquery = {
	$: $,
	jQuery: jQuery
}; """ if whatfor == meteor_desk_app else ""}

	return meteor_config

"""
def make_auto_update_version(path, meteorRelease, root_url, root_prefix, whatfor, appId=None):
	from fluorine.utils import file

	runtimeCfg = OrderedDict()
	runtimeCfg["meteorRelease"] = meteorRelease
	runtimeCfg["ROOT_URL"] = root_url
	if whatfor == "meteor_web":
		runtimeCfg["ROOT_URL_PATH_PREFIX"] = root_prefix
	else:
		runtimeCfg["ROOT_URL_PATH_PREFIX"] = "/meteordesk"

	if appId:
		runtimeCfg["appId"] = appId

	manifest = file.read(path)
	manifest = json.loads(manifest).get("manifest")
	autoupdateVersion, autoupdateVersionRefresh, frappe_manifest_js, frappe_manifest_css = meteor_hash_version(manifest, runtimeCfg, whatfor)
	print "sha1 digest {} {}".format(autoupdateVersion, autoupdateVersionRefresh)
	return autoupdateVersion, autoupdateVersionRefresh, frappe_manifest_js, frappe_manifest_css
"""

def get_meteor_config(mthost, mtddpurlport, meteor_url_path_prefix, version, version_fresh, mrelease, appId=None):

	from fluorine.utils import check_dev_mode

	devmod = check_dev_mode()

	meteor_config = """__meteor_runtime_config__ = {
		%(appId)s"meteorRelease": "%(meteorRelease)s",
		"ROOT_URL": "%(meteor_root_url)s",
		"ROOT_URL_PATH_PREFIX": "%(meteor_url_path_prefix)s",
		"autoupdateVersion": "%(meteor_autoupdate_version)s",
		"autoupdateVersionRefreshable": "%(meteor_autoupdate_version_freshable)s"%(meteor_ddp_default_connection_url)s
	};
	%(jquery)s
	""" % {"appId": "'appId':'" + appId + "',\n\t\t" if devmod else "", "meteorRelease": mrelease, "meteor_root_url": mthost, "meteor_url_path_prefix": meteor_url_path_prefix,
				"meteor_autoupdate_version": version, "meteor_autoupdate_version_freshable": version_fresh,
				"meteor_ddp_default_connection_url": ",\n\t\t'DDP_DEFAULT_CONNECTION_URL': '" + mtddpurlport + "'", "jquery": """
if (typeof Package === 'undefined')
	Package = {};
Package.jquery = {
	$: $,
	jQuery: jQuery
};"""}

	return meteor_config


def make_auto_update_version(path, meteorRelease, root_url, appId=None):
	from fluorine.utils import file

	runtimeCfg = OrderedDict()
	runtimeCfg["meteorRelease"] = meteorRelease
	runtimeCfg["ROOT_URL"] = root_url
	runtimeCfg["ROOT_URL_PATH_PREFIX"] = default_path_prefix

	if appId:
		runtimeCfg["appId"] = appId

	manifest = file.read(path)
	manifest = json.loads(manifest).get("manifest")
	autoupdateVersion, autoupdateVersionRefresh, frappe_manifest_js, frappe_manifest_css = meteor_hash_version(manifest, runtimeCfg)
	print "sha1 digest {} {}".format(autoupdateVersion, autoupdateVersionRefresh)
	return autoupdateVersion, autoupdateVersionRefresh, frappe_manifest_js, frappe_manifest_css

def meteor_hash_version(manifest, runtimeCfg):
	sh1 = hashlib.sha1()
	sh2 = hashlib.sha1()
	frappe_manifest_js = []
	frappe_manifest_css = []

	rt = json.dumps(runtimeCfg).replace(" ", "").encode('utf8')
	print "json.dumps ", rt
	sh1.update(rt)
	sh2.update(rt)

	prefix = default_path_prefix

	for m in manifest:
		if m.get("where") == "client" or m.get("where") == "internal":
			path = m.get("path")
			mhash = m.get("hash")
			if m.get("where") == "client":
				nurl = prefix + m.get("url")
				if m.get("type") == "css":
					frappe_manifest_css.append(nurl)
					sh2.update(path)
					sh2.update(mhash)
					continue
				elif m.get("type") == "js":
					if "jquery" not in path:
						frappe_manifest_js.append(nurl)
			sh1.update(path)
			sh1.update(mhash)

	return sh1.hexdigest(), sh2.hexdigest(), frappe_manifest_js, frappe_manifest_css

"""
def meteor_hash_version(manifest, runtimeCfg, whatfor):
	sh1 = hashlib.sha1()
	sh2 = hashlib.sha1()
	frappe_manifest_js = []
	frappe_manifest_css = []

	rt = json.dumps(runtimeCfg).replace(" ", "").encode('utf8')
	print "json.dumps ", rt
	sh1.update(rt)
	sh2.update(rt)

	if whatfor == meteor_desk_app:
		prefix = "/meteordesk"
	else:
		prefix = ""

	for m in manifest:
		if m.get("where") == "client" or m.get("where") == "internal":
			path = m.get("path")
			mhash = m.get("hash")
			if m.get("where") == "client":
				if whatfor == meteor_desk_app:
					nurl = prefix + m.get("url")
				else:
					nurl = m.get("url")
				if m.get("type") == "css":
					frappe_manifest_css.append(nurl)
					sh2.update(path)
					sh2.update(mhash)
					continue
				elif m.get("type") == "js":
					if whatfor == meteor_desk_app:
						if "jquery" not in path:
							frappe_manifest_js.append(nurl)
					else:
						frappe_manifest_js.append(nurl)
			sh1.update(path)
			sh1.update(mhash)

	return sh1.hexdigest(), sh2.hexdigest(), frappe_manifest_js, frappe_manifest_css
"""

def make_meteor_props(context, whatfor, production=False):
	from fluorine.utils import get_meteor_runtime_config_path
	from fluorine.utils.file import get_path_reactivity

	path_reactivity = get_path_reactivity()

	"""
		This is only called in developer mode or when making production mode
		Used when issued from command line
		From web force production = False
	"""
	#try:
	#	production = frappe.local.making_production
	#except:
	#	production = False

	appId = ""
	if not production:
		progarm_path = os.path.join(path_reactivity, whatfor, ".meteor/local/build/programs/web.browser/program.json")
		config_path = os.path.join(path_reactivity, whatfor, ".meteor/local/build/programs/server/config.json")
		appId = get_meteor_appId(os.path.join(path_reactivity, whatfor, ".meteor/.id"))
	else:
		progarm_path = os.path.join(path_reactivity, whatfor.replace("meteor", "final"), "bundle/programs/web.browser/program.json")
		config_path = os.path.join(path_reactivity, whatfor.replace("meteor", "final"), "bundle/programs/server/config.json")

	context.meteorRelease = get_meteor_release(config_path)
	context.appId = appId.replace(" ","").replace("\n","")

	context.meteor_autoupdate_version, context.meteor_autoupdate_version_freshable, manifest_js, manifest_css =\
				make_auto_update_version(progarm_path, context.meteorRelease, context.meteor_root_url, appId=context.appId)


	meteor_runtime_path = get_meteor_runtime_config_path(whatfor)
	context.meteor_package_js = [meteor_runtime_path] + manifest_js
	context.meteor_package_css = manifest_css
	context.meteor_runtime_config = True

	url_prefix = meteor_url_path_prefix(whatfor)


	props = get_meteor_config(context.meteor_root_url, context.meteor_ddp_default_connection_url, url_prefix, context.meteor_autoupdate_version,
							context.meteor_autoupdate_version_freshable, context.meteorRelease, context.appId)

	meteor_runtime_real_path = get_meteor_runtime_config_path(whatfor, real=True)
	#if not production:
	save_meteor_props(props, meteor_runtime_real_path)
	#else:
	#	try:
	#		os.unlink(meteor_runtime_real_path)
	#	except:
	#		pass


def update_common_config(config):
	from fluorine.utils.file import get_path_reactivity, save_js_file

	path_reactivity = get_path_reactivity()
	config_file_path = os.path.join(path_reactivity, "common_site_config.json")

	save_js_file(config_file_path, config)


def save_meteor_props(props, path):
	from fluorine.utils.file import save_file
	save_file(path, props)

def get_meteor_appId(path):
	appid = None
	with open(path, "r") as f:
		for line in f:
			if line.startswith("#") or line.startswith("\n"):
				continue
			appid = line
			break
	print "appId {}".format(appid)
	return appid


def prepare_client_files(curr_app):
	from fluorine.utils.react_file_loader import remove_directory
	from fluorine.utils.file import get_path_reactivity, save_file
	from fluorine.commands_helpers.meteor import get_active_apps

	react_path = get_path_reactivity()
	curr_app_path = frappe.get_app_path(curr_app)

	for whatfor in whatfor_all:#("meteor_web", "meteor_app"):
		meteor_final_path = os.path.join(react_path, whatfor.replace("meteor", "final"))
		if os.path.exists(meteor_final_path):
			try:
				remove_directory(os.path.join(meteor_final_path, "bundle"))
			except:
				pass

		apps = get_active_apps()
		apps.remove(curr_app)
		src = os.path.join(react_path, whatfor, ".meteor", "packages")
		dst = os.path.join(curr_app_path, "templates", "packages_add_" + whatfor)
		installed_packages = frappe.get_file_items(src)

		for app in apps:
			tmp_app_path = frappe.get_app_path(app)
			tmp_dst = os.path.join(tmp_app_path, "templates", "packages_add_" + whatfor)
			tmp_app_pckg = frappe.get_file_items(tmp_dst)
			for pckg in tmp_app_pckg:
				if pckg in installed_packages:
					installed_packages.remove(pckg)

		save_file(dst, "\n".join(installed_packages))


def cmd_packages_from(curr_app):
	from fluorine.utils.install import get_packages_version
	from fluorine.utils.react_file_loader import remove_directory
	from fluorine.utils.file import get_path_reactivity, save_file
	from fluorine.commands_helpers.meteor import get_active_apps
	import re

	react_path = get_path_reactivity()
	curr_app_path = frappe.get_app_path(curr_app)

	for whatfor in whatfor_all:#("meteor_web", "meteor_app"):
		meteor_final_path = os.path.join(react_path, whatfor.replace("meteor", "final"))
		if os.path.exists(meteor_final_path):
			try:
				remove_directory(os.path.join(meteor_final_path, "bundle"))
			except:
				pass

		apps = get_active_apps()
		apps.remove(curr_app)
		dst = os.path.join(curr_app_path, "templates", "packages_add_" + whatfor)
		installed_packages = get_packages_version(whatfor, path_reactivity=react_path)
		packages_to_remove = set([])

		for app in apps:
			tmp_app_path = frappe.get_app_path(app)
			tmp_dst = os.path.join(tmp_app_path, "templates", "packages_add_" + whatfor)
			tmp_app_pckg = frappe.get_file_items(tmp_dst)
			#Not permited upgrade packages installed by other modules
			for i_pckg in installed_packages:
				for pckg in tmp_app_pckg:
					pckg_name = pckg.split("@=")[0]
					if re.match(pckg_name, i_pckg):
						packages_to_remove.add(pckg)

		packages_to_add = set(installed_packages).difference(packages_to_remove)

		save_file(dst, "\n".join(packages_to_add))




def make_meteor_files(mthost, mtport, mtddpurl, architecture):
	from fluorine.utils.file import make_meteor_file

	for w in whatfor_all:#("meteor_web", "meteor_app"):
		make_meteor_file(whatfor=w, mtport=mtport, mthost=mthost, architecture=architecture)


"""
def template_replace(m):
	content = m.group(3)
	return content
"""
