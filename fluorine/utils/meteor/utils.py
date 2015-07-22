# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'


import frappe
from collections import OrderedDict
import hashlib, json, os


def meteor_url_path_prefix(whatfor):
	return os.path.join("assets", "fluorine",  whatfor, "webbrowser")


def build_meteor_context(context, devmode, whatfor):
	#from file import get_path_reactivity
	import random
	from fluorine.utils.reactivity import meteor_config

	#path_reactivity = get_path_reactivity()

	#config_path = os.path.join(path_reactivity, "common_site_config.json")
	#conf = frappe.get_file_json(config_path)
	conf = meteor_config

	if not devmode:
		add = 0
		meteor_dns = conf.get("meteor_dns") or {}
		all_dns = meteor_dns.get(whatfor)
		n = random.randint(0, len(all_dns) - 1)
		meteor = all_dns[n]
	else:
		meteor = conf.get("meteor_dev") or {}
		add = 80 if whatfor == "meteor_app" else 0

	context.mport = meteor.get("port", 3000) + add

	#base_url = frappe.local.request.url
	#burl = base_url.rsplit(":",1)
	#if burl > 1:
		#port = burl[1]
	#	host_url = burl[0]
	#else:
	#	host_url = base_url
		#port = ""

	host = meteor.get("host", "http://localhost")
	ddpurl = meteor.get("ddpurl", "http://localhost")
	meteor_host =  host + ":" + str(context.mport)
	ddpurl_port = ddpurl + ":" + str(context.mport)
	context.meteor_root_url = host
	context.meteor_root_url_port = meteor_host
	context.meteor_url_path_prefix = ""#meteor_url_path_prefix(whatfor)
	context.meteor_ddp_default_connection_url = ddpurl_port


def get_meteor_release(cpath):

	if os.path.exists(cpath):
		config = frappe.get_file_json(cpath)
		return config.get("meteorRelease", "")

	return ""

def get_meteor_config(mthost, mtddpurlport, meteor_url_path_prefix, version, version_fresh, mrelease, whatfor):

	meteor_config = """__meteor_runtime_config__ = {
		"meteorRelease": "%(meteorRelease)s",
		"ROOT_URL": "%(meteor_root_url)s",
		"ROOT_URL_PATH_PREFIX": "%(meteor_url_path_prefix)s",
		"autoupdateVersion": "%(meteor_autoupdate_version)s",
		"autoupdateVersionRefreshable": "%(meteor_autoupdate_version_freshable)s",
		"DDP_DEFAULT_CONNECTION_URL": "%(meteor_ddp_default_connection_url)s"
	};
	%(jquery)s
	""" % {"meteorRelease": mrelease, "meteor_root_url": mthost, "meteor_url_path_prefix": meteor_url_path_prefix,
				"meteor_autoupdate_version": version, "meteor_autoupdate_version_freshable": version_fresh,
				"meteor_ddp_default_connection_url": mtddpurlport, "jquery": """
if (typeof Package === 'undefined')
	Package = {};
Package.jquery = {
	$: $,
	jQuery: jQuery
}; """ if whatfor == "meteor_app" else ""}

	return meteor_config


def make_auto_update_version(path, meteorRelease, root_url, root_prefix, whatfor, appId=None):
	from fluorine.utils import file

	runtimeCfg = OrderedDict()
	runtimeCfg["meteorRelease"] = meteorRelease#"METEOR@1.1.0.2"
	runtimeCfg["ROOT_URL"] = root_url#"http://localhost"
	runtimeCfg["ROOT_URL_PATH_PREFIX"] = root_prefix
	if appId:
		runtimeCfg["appId"] = appId
	#runtimeCfg["appId"] = "1uo02wweyt6o11xsntyy"
	manifest = file.read(path)
	manifest = json.loads(manifest).get("manifest")
	autoupdateVersion, autoupdateVersionRefresh, frappe_manifest_js, frappe_manifest_css = meteor_hash_version(manifest, runtimeCfg, whatfor)
	print "sha1 digest {} {}".format(autoupdateVersion, autoupdateVersionRefresh)
	#runtimeCfg["autoupdateVersion"] = autoupdateVersion
	#autoupdateVersionRefresh = meteor_hash_version(manifest, runtimeCfg, css=True)
	#print "sha1 digest ", autoupdateVersionRefresh
	return autoupdateVersion, autoupdateVersionRefresh, frappe_manifest_js, frappe_manifest_css


def meteor_hash_version(manifest, runtimeCfg, whatfor):
	sh1 = hashlib.sha1()
	sh2 = hashlib.sha1()
	frappe_manifest_js = []
	frappe_manifest_css = []
	#runtimeCfg = {"meteorRelease": meteorRelease,
	#            "ROOT_URL": 'http://localhost',
	#             "ROOT_URL_PATH_PREFIX": ""}

	#runtimeCfg = """{'meteorRelease': %s,'ROOT_URL': 'http://localhost','ROOT_URL_PATH_PREFIX': ''}""" % meteorRelease
	rt = json.dumps(runtimeCfg).replace(" ", "").encode('utf8')
	print "json.dumps ", rt
	sh1.update(rt)
	sh2.update(rt)
	for m in manifest:
		if m.get("where") == "client" or m.get("where") == "internal":
			prefix = "assets/fluorine/%s/webbrowser" % whatfor

			if m.get("where") == "client":
				url =  m.get("url").split("?")[0]
				app = url.split("/", 2)[1]
				is_app = ""
				path = m.get("path")
				if app in frappe.get_installed_apps():
					is_app = "/app"
				nurl = prefix + is_app + url
				if m.get("type") == "css":
					frappe_manifest_css.append(nurl)
					sh2.update(path)
					sh2.update(m.get("hash"))
					continue
				else:
					if whatfor == "meteor_app":
						if "jquery" not in path:
							frappe_manifest_js.append(nurl)
					else:
						frappe_manifest_js.append(nurl)
			#if m.get("type") == "css":
			#	sh2.update(m.get("path"))
			#	sh2.update(m.get("hash"))
			#	continue
			sh1.update(m.get("path"))
			sh1.update(m.get("hash"))

	return sh1.hexdigest(), sh2.hexdigest(), frappe_manifest_js, frappe_manifest_css

def make_meteor_props(context, whatfor):
	from fluorine.utils.file import get_path_reactivity

	path_reactivity = get_path_reactivity()
	progarm_path = os.path.join(path_reactivity, whatfor, ".meteor/local/build/programs/web.browser/program.json")
	config_path = os.path.join(path_reactivity, whatfor, ".meteor/local/build/programs/server/config.json")
	context.meteorRelease = get_meteor_release(config_path)
	appId = get_meteor_appId(os.path.join(path_reactivity, whatfor, ".meteor/.id"))
	context.appId = appId.replace(" ","").replace("\n","")

	context.meteor_autoupdate_version, context.meteor_autoupdate_version_freshable, manifest_js, manifest_css =\
				make_auto_update_version(progarm_path, context.meteorRelease, context.meteor_root_url, "", whatfor, appId=context.appId)

	app_path = frappe.get_app_path("fluorine")
	#meteor_runtime_path = os.path.join(app_path, "public", whatfor, "meteor_runtime_web_config.js")
	meteor_runtime_path = os.path.join(app_path, "public", whatfor, "meteor_runtime_config.js")

	meteor_root_url_prefix = os.path.join(app_path, "public", whatfor, "meteor_url_prefix.js")
	#meteor_root_url_prefix = os.path.join(app_path, "public", "js", "meteor_url_prefix.js")

	context.meteor_package_js = [os.path.join("assets", "fluorine", whatfor, "meteor_runtime_config.js")] + manifest_js + [os.path.join("assets", "fluorine", whatfor, "meteor_url_prefix.js")]
	context.meteor_package_css = manifest_css
	context.meteor_runtime_config = True

	#meteor_url_path_prefix(whatfor)

	props = get_meteor_config(context.meteor_root_url, context.meteor_ddp_default_connection_url, "", context.meteor_autoupdate_version,\
							context.meteor_autoupdate_version_freshable, context.meteorRelease, whatfor)

	save_meteor_props(props, meteor_runtime_path)

	save_meteor_root_prefix(meteor_url_path_prefix(whatfor), meteor_root_url_prefix)


def save_meteor_root_prefix(prefix, path):
	save_meteor_props("__meteor_runtime_config__.ROOT_URL_PATH_PREFIX = '%s';" % prefix, path)

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

def make_heritage(block, context):
	import re
	#for block, render in out.items():
	#in_first_block_render, data_first_block_render, outer_first_block_render = context.spacebars_data.get(block, None), context.data.get(block, None),\
	#context.block
	in_first_block_render = context.get(block, None)
	#print frappe.utils.pprint_dict(context)
	#print "make_heritages  template {} data.path {}".format(context["template"], context.get("path"))
	if in_first_block_render:
		contents = re.sub("<template name=['\"](.+?)['\"](.*?)>(.*?)</template>", template_replace, in_first_block_render, flags=re.S)
		#print "my new context block {}".format(context.get(block, None))
		context["_" + block] = contents
	#if data_first_block_render:
	#	context["__" + block] = data_first_block_render
	#if outer_first_block_render:
	#	context["___" + block] = outer_first_block_render


def template_replace(m):
	content = m.group(3)
	return content


def compile_spacebars_templates(context):
	import zerorpc, re
	import subprocess
	from fluorine.utils.file import get_path_reactivity

	templates = []
	for name, template in context.items():
		#template = context.get(name, "")
		m = re.match(r".*?<template\s+.*?>(.*?)</template>", template, re.S)
		if m:
			print "m.group(1) name {} group(1) {}".format(name, m.group(1))
			templates.append({"name":name, "code": m.group(1)})

	path = get_path_reactivity()
	print "path in compile_spacebars_templates {}".format(os.path.join(path, "compile_spacebars_js.js"))
	node = subprocess.Popen(["node", os.path.join(path, "server/compile_spacebars_js.js"), os.path.join(path, "fluorine_program.json")], cwd=os.path.join(path, "server"), shell=False, close_fds=True)
	c = zerorpc.Client()
	c.connect("tcp://127.0.0.1:4242")
	#for key, val in out.items():
	compiled_templates = c.compile(templates)
	node.kill()

	return compiled_templates
