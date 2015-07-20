# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'


from frappe.website.utils import scrub_relative_urls
#from frappe.website.template import render_blocks
from jinja2.utils import concat
from jinja2 import contextfunction, contextfilter
import frappe
from frappe.utils.jinja import set_filters, get_allowed_functions_for_jenv
#from frappe.website.context import get_context
#from fluorine.utils.packages_path import get_package_path
from fjinja import MyFileSystemLoader
#from jinja2 import ChoiceLoader
import hashlib, json, os, re
from collections import OrderedDict


def get_encoding():
	return "utf-8"

#from jinja2 import contextfunction, environmentfunction

def is_in_extend_path(doc, template):
	for d in doc.docs:
		if d.template == template:
			print "one template found in is:in 5 {}".format(d.template)
			return d
		found = is_in_extend_path(d, template)
		if found:
			return found
	return None

def get_template_from_doc(doc, tname, encoding="utf-8"):
	from file import read

	content = doc.content
	if not content:
		content = read(doc.file_temp_path).decode(encoding)
	template = r"<\s*template\s+name\s*=\s*(['\"])%s\1(.*?)\s*>(.*?)<\s*/\s*template\s*>" % tname
	g = re.search(template, content, re.S|re.I|re.M)
	t = ""
	if g:
		t = g.group(3)

	return t

def get_doc_from_template(template):
		doc = None
		obj = frappe.local.meteor_map_path.get(template)
		if obj:
			doc = obj.get("doc")
		return doc

def get_doc_from_deep(template, deep=1):

	obj = frappe.local.meteor_map_path.get(template)
	if obj:
		doc = obj.get("doc")
		if doc.extends_found and deep > 0:
			return get_doc_from_deep(doc.extends_path[0], deep-1)
		return doc, deep
	return None, 1
	#frappe.msgprint("The is no doc with xhtml template {} for deep {}.".format(template, deep), raise_exception=1)

c = lambda t:re.compile(t, re.S|re.M)

def get_pattern_path(name, path):

	#basename = os.path.basename(realpath)
	#dirpath = os.path.dirname(realpath)
	#path = os.path.join(dirpath, basename[:-6])
	pattern = path + r"/(?:.+?/)?(?:(?:%s)/(?:.+)|(?:%s/?$))" % (name, name)
	return pattern

def get_deep_refs(refs, tname, deep):

	if deep == 1:
		return get_page(refs, tname)

	page = None
	#first is the extends so only this count for deep
	if refs:
		obj = frappe.local.meteor_map_templates.get(refs[0])
		nrefs = obj.get("refs")
		page = get_deep_refs(nrefs, tname, deep-1)

	return page


def get_page(refs, tname):

	for ref in refs:
		sobj = frappe.local.meteor_map_templates.get(ref)
		template = sobj.get("template_obj")
		for block in template.blocks.keys():
			if block == tname.strip():
				return ref

	return None

@contextfunction
def tkeep(ctx, tname, page=None, deep=1, patterns=None):

	if not page:
		obj = frappe.local.meteor_map_templates.get(ctx.name)
		refs = obj.get("refs")
		page = get_deep_refs(refs, tname, deep)

	fadd = ctx.get("files_to_add",{})
	fadd.append({"tname": tname, "pattern": patterns, "page": page})


def local_tkeep(ctx, tname, page, patterns=None):
	fadd = ctx.get("files_to_add",{})

	if  patterns and isinstance(patterns, basestring):
		patterns = [patterns]

	obj = frappe.local.meteor_map_templates.get(page)
	appname = obj.get("appname")

	if not fadd.get(appname):
		fadd[appname] = []
	#realpath = obj.get("realpath")
	template_path = obj.get("template")
	if not patterns:
		#pattern = get_pattern_path(tname, realpath)
		pattern = get_pattern_path(tname, template_path[:-6])
		print "templates paths to add tname 3 {} template_path {} pattern {}".format(tname, template_path, pattern)
		fadd.get(appname).append({"tname": page, "pattern":pattern})
	elif tname:
		for pattern in patterns:
			#print "templates paths to add tname {} template_path {} pattern {}".format(tname, template_path, pattern)
			#pat = realpath[:-6] + "/.*/"+ tname + "/" + pattern
			pat = template_path[:-6] + r"/.*/"+ tname + "/" + pattern
			fadd.get(appname).append({"tname": page, "pattern": pat})
	else:
		for pattern in patterns:
			fadd.get(appname).append({"tname": page, "pattern": pattern})


@contextfunction
#@environmentfunction
def files_to_add(ctx, tname, appname, page):
	#filename = re.findall('\'([^\']*)\'', str(mself))
	#fadd = ctx.get("files_to_add",{})
	#print "files to add function tname 24 {} appname {} ctx {} filename {}".format(tname, appname, ctx.get("files_to_add"), page)
	"""
	if page:
		obj = frappe.local.meteor_map_templates.get(page)
		if not fadd.get(appname):
			fadd[appname] = []
		realpath = obj.get("realpath")
		pattern = get_pattern_path(tname, realpath)
		#fadd.get(appname).append({"tname": tname, "path": realpath[:-6] + "[./]*"})
		fadd.get(appname).append({"tname": tname, "path": pattern})
	"""
	return ""

STARTTEMPLATE_SUB_ALL = c(r"<\s*template\s+name\s*=\s*(['\"])(\w+)\1(.*?)\s*>(.*?)<\s*/\s*template\s*>")
STARTDIV_SUB_ALL = r"<\s*div\s+class\s*=\s*(['\"])%s\1\s*>(.*?)<\s*/\s*div\s*>"

def get_msuper_inner_content(ctx, source):
	s = STARTTEMPLATE_SUB_ALL.search(source)
	if s:
		name = s.group(2)
		source = s.group(4)
		#TODO remove not? or remove all code below
		if not ctx.get("developer_mode"):
			print "in developer mode inside msuper helper"
			m = re.search(STARTDIV_SUB_ALL % (name,), source, re.S|re.M)
			if m:
				source = m.group(2)
	return source

@contextfunction
def msuper(ctx, tname, deep=1):
	#encoding = get_encoding()
	#tp = tPages(ctx.name)
	#for r in tp:
	code = ""
	page = ctx.name
	obj = frappe.local.meteor_map_templates.get(page)
	refs = obj.get("refs")

	if deep >= 1:
		page = get_deep_refs(refs, tname, deep)

	if page:
		sobj = frappe.local.meteor_map_templates.get(page)
		template = sobj.get("template_obj")
		render = template.blocks.get(tname)
		code = scrub_relative_urls(concat(render(template.new_context(ctx))))
		code = get_msuper_inner_content(ctx, code)

	print "after msuper call from template code {}".format(code)

	return code

@contextfunction
def mself(ctx, tname):
	return msuper(ctx, tname, deep=0)

class tPages:
	def __init__(self, template_path):
		self.template_path = template_path
		self.cdeep = 1
		self.i = 0
		obj = frappe.local.meteor_map_templates.get(self.template_path)
		self.refs = obj.get("refs")

	def __iter__(self):
		return self

	def next(self):
		ref = None

		if not self.refs:
			raise StopIteration()

		if self.i < len(self.refs):
			ref = self.refs[self.i]
			self.i += 1
		else:
			self.cdeep += 1
			self.refs = self.get_deep_refs(self.refs, self.cdeep)
			if self.refs:
				self.i = 1
				ref = self.refs[0]

		if ref:
			return ref
		else:
			raise StopIteration()

	def get_deep_refs(self, refs, deep):

		if deep == 1:
			return refs

		nrefs = None
		#first is the extends so only this count for deep
		if refs:
			obj = frappe.local.meteor_map_templates.get(refs[0])
			nrefs = obj.get("refs")
			nrefs = self.get_deep_refs(nrefs, deep-1)

		return nrefs

def flat_refs(template_path):
	flat = []
	obj = frappe.local.meteor_map_templates.get(template_path)
	refs = obj.get("refs") or []
	#if refs:
	flat.extend(refs)
	for ref in refs:
		flat.extend(flat_refs(ref))

	return flat


@contextfilter
def mdom_filter(ctx, source, page, **keyargs):
	template_path = ctx.name
	code = None

	refs = [template_path]
	refs.extend(flat_refs(template_path))

	for ref in refs:
		obj = frappe.local.meteor_map_templates.get(ref)
		appname = obj.get("appname")
		m = frappe.local.module_registe.get(appname)
		if m:
			module = m.module
			if hasattr(module, "mdomfilter"):
				code = module.mdomfilter(ctx, appname, page, source, obj.get("template_obj"), **keyargs)
		if code:
			break

	return code or source


def mecho(value, content=""):
	print "mecho content is value 2 {} content {}".format(value, content)
	return value + "  " + content

def fluorine_get_fenv():

	from jinja2 import DebugUndefined
	from fluorine.utils.fjinja import MyEnvironment
	from extension_template import MeteorTemplate

	if not frappe.local.fenv:
		encoding = get_encoding()
		fenv = MyEnvironment(loader = fluorine_get_floader(encoding=encoding),
			undefined=DebugUndefined, extensions=[MeteorTemplate, "jinja2.ext.do"])# ["jinja2.ext.do",]
		set_filters(fenv)

		fenv.globals.update(get_allowed_functions_for_jenv())
		fenv.globals.update({"msuper":msuper})
		fenv.globals.update({"mfiles_to_add":files_to_add})
		fenv.globals.update({"mtkeep":tkeep})
		fenv.filters["mecho"] = mecho
		fenv.filters["mdom_filter"] = mdom_filter

		frappe.local.fenv = fenv

	return frappe.local.fenv


def fluorine_get_floader(encoding="utf-8"):

	from fluorine.utils.fjinja import MyChoiceLoader

	if not frappe.local.floader:

		path = os.path.normpath(os.path.join(os.getcwd(), "..")) + "/apps"
		#first template to load is the last installed
		#So, we can replace the oldest template by new one with the same name
		apps = frappe.get_installed_apps()[::-1]
		app_fluorine = frappe.get_app_path("fluorine")
		dbname = os.path.join(app_fluorine, "templates/react/temp", "fluorinedb")
		db_dirpath = os.path.dirname(os.path.join(dbname))
		frappe.create_folder(db_dirpath)
		m = MyFileSystemLoader(apps, path, dbpath=dbname, encoding=encoding)
		fluor_loader = [m]

		frappe.local.floader = MyChoiceLoader(fluor_loader)

	return frappe.local.floader


def fluorine_get_template(path):
	return fluorine_get_fenv().addto_meteor_templates_list(path)

"""
def fluorine_render_blocks(context, whatfor):
	env = fluorine_get_fenv()

	def _render_blocks(template_path):
		#print "template_paths {}".format(template_path)
		#get the first template. The last installed in this case
		source = frappe.local.floader.get_source(frappe.local.fenv, template_path)[0]
		for referenced_template_path in meta.find_referenced_templates(env.parse(source)):
			if referenced_template_path:
				_render_blocks(referenced_template_path)

		#fluorine_get_template(template_path)
	fluorine_get_template(context["spacebars_template"])
	#_render_blocks(context["spacebars_template"])
"""

#def compile_jinja_templates(mtl, context, whatfor):
def compile_jinja_templates(context, whatfor):

	from file import save_file
	from Templates import STARTTEMPLATE_SUB_ALL

	#print "mtl list de templates {}".format(mtl)
	out = {}
	toadd = {}
	print "frappe.local.meteor_map_templates 2 {}".format(frappe.local.meteor_map_templates.keys())
	keys = frappe.local.meteor_map_templates.keys()

	for template_path in keys:
		obj = frappe.local.meteor_map_templates.get(template_path)
		template = obj.get("template_obj")
		realpath = obj.get("realpath")
		dstPath = realpath[:-6] + ".html"
		#template_path = obj.get("template")
		tname = os.path.basename(template_path)
		print "dstPath in compile jinja2 17 {} template {} appname {} template {}".format(dstPath, tname, obj.get("appname"), template)
		#dstPath = frappe.local.meteor_map_path[l.get("tpath")].get("realpath")[:-6] + ".html"
		#dstPath = template.filename[:-6].replace("templates/react/temp","templates/react",1) + ".html"

		try:
			#if not frappe.local.files_to_add.get(obj.get("appname")):
			#	frappe.local.files_to_add[obj.get("appname")] = []
			if template_path not in frappe.local.templates_referenced:
				print "calling render template from compile jinja {}".format(template_path)
				content = scrub_relative_urls(concat(template.render(template.new_context(context))))
			#re_file = fnmatch.translate(realpath[:-6] + "[./]*")
			#pattern = get_pattern_path(tname[:-6], realpath)
			#content = ""
			#print "template in compile jinja templates 23 pattern {} blocks {} content {}".format(pattern, template, template.blocks, content)
				if content and template: #and template.blocks:
					#print "l.get save to file {}".format(l.get("save"))
					content = "\n\n".join([s for s in content.splitlines() if s])
					#if template_path not in frappe.local.templates_referenced:
					#print "not in reference files template_path 4 {} referenced {}\n".format(template_path, frappe.local.templates_referenced)
					#pattern = realpath[:-6] + r"[/.](.*)"
					#pattern = realpath[:-6] + r"(?:\.).*"
					pattern = template_path[:-6] + r"(?:\.).*"
					#frappe.local.files_to_add.get(obj.get("appname")).append({"tname": template_path, "pattern":pattern})
					context.files_to_add.append({"tname": "", "pattern":pattern, "page": template_path})
					#pattern = realpath[:-6] + r"/common/(.*)"
					#context.files_to_add.get(obj.get("appname")).append({"tname": template_path, "path": c(pattern), "pattern":pattern})
					save_file(dstPath, content.encode(get_encoding()))
					refs = obj.get("refs")
					#template_path = obj.get("template")
					tcont = {}
					for m in STARTTEMPLATE_SUB_ALL.finditer(content):
						name = m.group(2)
						tcont[name] = m.group(0)
					add = add_to_path(context, template, refs, tcont)
					toadd.update(add)
					if whatfor in ("meteor_app", "meteor_frappe"):
						out.update(tcont)
					#print "templates teste with finditer template name 9 {} template is {}".format(m.group(2), m.group(0))

				"""
				items = template.blocks.items()
				for block, render in items:
					if block.startswith("spacebars"):
						nameblock = block[10:]
						#make_heritage(block, context)
						block = scrub_relative_urls(concat(render(template.new_context(context))))
						out[nameblock] = block
						print "templates teste with finditer template name 5 {} template is {}".format(nameblock, block)
				"""
			#else:
			#	os.remove(dstPath)
		except Exception as e:
			file_temp_path = obj.get("file_temp_path")
			print "an error occurr removing file {} error {}".format(file_temp_path, e)
			#os.remove(file_temp_path)

		#file_temp_path = doc.file_temp_path
		#frappe.create_folder(os.path.dirname(file_temp_path))
		#write(file_temp_path, contents)

	remove_from_path(context, toadd)

	for obj in context.files_to_add:
		#appname = obj.get("appname")
		tname = obj.get("tname")
		pattern = obj.get("pattern")
		page = obj.get("page")
		local_tkeep({"files_to_add":frappe.local.files_to_add}, tname, page, patterns=pattern)

	"""
	for k, v in frappe.local.meteor_map_templates.itemitems():
		if k not in frappe.local.templates_referenced:
			template = v.get("template_obj")
			tname = v.get("template")
			refs = v.get("refs")
			add_to_path(tname, template, refs)
	"""

	return out


def remove_from_path(ctx, toadd):
	#fremove = ctx.get("files_to_remove", {})
	for k, v in frappe.local.meteor_map_templates.iteritems():
		template = v.get("template_obj")
		if template:
			for block in template.blocks.keys():
				appname = v.get("appname")
				if appname == toadd.get(block):
					continue
				#if not frappe.local.files_to_remove.get(appname):
				#	frappe.local.files_to_remove[appname] = []
				#realpath = v.get("realpath")
				ctx.files_to_remove.append({"tname": k[:-6], "pattern": "", "page": k})
				#pattern = get_pattern_path(block, k[:-6])
				#fremove.get(appname).append({"tname": block, "path": c(pattern)})
				#frappe.local.files_to_remove.get(appname).append({"tname": k, "pattern": pattern})
				print "blocks to remove are: block name 7 {} appname {} toadd {}".format(block, appname, toadd)

def add_to_path(ctx, template, refs, tcont):
	#fadd = ctx.get("files_to_add",{})
	toadd = {}
	for tname in tcont.keys():

		if template and tname not in template.blocks.keys():
			ref = check_refs(tname, refs)
		else:
			ref = template.name

		if ref:
			obj = frappe.local.meteor_map_templates.get(ref)
			appname = obj.get("appname")
			#if not frappe.local.files_to_add.get(appname):
			#	frappe.local.files_to_add[appname] = []
			#realpath = obj.get("realpath")
			ctx.files_to_add.append({"tname": tname, "pattern": "", "page": ref})
			#pattern = get_pattern_path(tname, ref[:-6])
			#fadd.get(appname).append({"tname": tname, "path": c(pattern)})
			#frappe.local.files_to_add.get(appname).append({"tname": ref, "pattern":pattern})
			toadd[tname] = appname

	return toadd


def check_refs(tname, refs):
	for ref in refs:
		obj = frappe.local.meteor_map_templates.get(ref)
		template = obj.get("template_obj")
		if template and tname in template.blocks.keys():
			return ref
		nrefs = obj.get("refs")
		found = check_refs(tname, nrefs)
		if found:
			return found
	return None

"""
def fluorine_render_blocks(context, whatfor):
	#import inspect
	#print 'I am f1 and was called by', inspect.currentframe().f_back.f_code.co_name
	out = {}
	#env = frappe.get_jenv()
	env = fluorine_get_fenv()

	def _render_blocks(template_path):
		#print "template_paths {}".format(template_path)
		#get the first template. The last installed in this case
		source = frappe.local.floader.get_source(frappe.local.fenv, template_path)[0]
		for referenced_template_path in meta.find_referenced_templates(env.parse(source)):
			if referenced_template_path:
				_render_blocks(referenced_template_path)

		template = fluorine_get_template(template_path)
		items = template.blocks.items()
		#if not items:
		from file import save_file
		#from shutil import copyfile
		dstPath = template.filename[:-6] + ".html"
		content = scrub_relative_urls(concat(template.render(template.new_context(context))))
		save_file(dstPath, content)
		#return
			#copyfile(template.filename, dst)
			#out[block] = scrub_relative_urls(concat(render(template.new_context(context))))
		#if whatfor in ("meteor_app", "meteor_frappe"):
		for block, render in items:
			if block.startswith("spacebars"):
				block = block[10:]
				make_heritage(block, context)
				out[block] = scrub_relative_urls(concat(render(template.new_context(context))))

	_render_blocks(context["spacebars_template"])

	return out
"""

"""
def fluorine_build_context3(context, whatfor):

	from react_file_loader import read_client_files
	from . import check_dev_mode
	#print "befores fluorine_spacebars_build_context path {}".format(path)
	#if path.find(".") == -1 and not path == "404":
		#print "news fluorine_spacebars_build_context path {}".format(path)
	#fl = frappe.get_doc("Fluorine Reactivity")
	#if fl.fluorine_base_template and fl.fluorine_base_template.lower() != "default":
	#	app_base_template = fl.fluorine_base_template
	#else:
	#	app_base_template = frappe.get_hooks("base_template")
	#	if not app_base_template:
	#		app_base_template = "templates/base.html"

	#if context.base_template_path == app_base_template:

		#if not context.spacebars_data:
		#	context.spacebars_data = {}
		#print "context data path in override {}".format(context.data)
		#context.update(context.data or {})
	if not check_dev_mode():
		return

	apps = frappe.get_installed_apps()#[::-1]
	#apps.remove("fluorine")
	name_templates = []
	spacebars_templates = {}

	for app in apps:
		#print "app {}".format(app)
		pathname = frappe.get_app_path(app)#get_package_path(app, "", "")
		path = os.path.join(pathname, "templates", "react")
		if os.path.exists(path):
			files = read_client_files(path, whatfor, extension="html")
			for file in files:
				#l = prepare_files(files)
				for obj in reversed(file):
					#print "app is {} path is {}".format(app, os.path.join(os.path.relpath(root, pathname), file))
					#print(os.path.join(root, file[:-5] + ".py"))
					#filename = os.path.join(root, file)
					file_path = obj.get("path")
					py_path = file_path[:-5]
					root = file_path[:-len(obj.get("name"))]
					context.spacebars_template = os.path.join(os.path.relpath(root, pathname), obj.get("name"))
					if os.path.exists(os.path.join(root, py_path + ".py")):
						controller_path = os.path.join(app, context.spacebars_template).replace(os.path.sep, ".")[:-5]
						print "app_path 4 {} root {} context.spacebars_template {}".format(controller_path + ".py", root, context.spacebars_template)
						module = frappe.get_module(controller_path)
						if module:
							if hasattr(module, "get_context"):
								ret = module.get_context(context)
								if ret:
									context.update(ret)
							if hasattr(module, "get_children"):
								context.get_children = module.get_children
					#heritage
					out = fluorine_render_blocks(context)
					#context.spacebars_data.update(out)
					print "out {}".format(out)
					#print "context teste123 {} out {}".format(context.teste123, out.get("teste123", None))
					#print frappe.utils.pprint_dict(out)
					spacebars_templates.update(out)
					#for name in out:
					#	name_templates.append(name)
					context.update(out)
						#print "new spacebars_data {}".format(context)
	#context.data.update(context.spacebars_data or {})
#print "In fluorine_spacebars_build_context"
	if spacebars_templates:
		compiled_spacebars_js = compile_spacebars_templates(spacebars_templates)
		arr = compiled_spacebars_js.split("__templates__\n")
		arr.insert(0, "(function(){\n")
		arr.append("})();\n")
		context.compiled_spacebars_js = arr

	fluorine_publicjs_dst_path = os.path.join(frappe.get_app_path("fluorine"), "public", "js", "react")
	hooks_js = get_js_to_client(fluorine_publicjs_dst_path, whatfor)

	context.update(hooks_js)
	#print "A compilar templates \n{}".format(context.compiled_spacebars_js)

	return context
"""

def make_auto_update_version(path, meteorRelease, root_url, root_prefix, whatfor, appId=None):
	from fluorine.utils import file

	runtimeCfg = OrderedDict()
	runtimeCfg["meteorRelease"] = meteorRelease#"METEOR@1.1.0.2"
	runtimeCfg["ROOT_URL"] = root_url#"http://localhost"
	runtimeCfg["ROOT_URL_PATH_PREFIX"] = ""#root_prefix
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


def make_meteor_ignor_files(apps):
	from fjinja import process_hooks_apps, process_hooks_meteor_templates
	from file import process_ignores_from_modules#, save_js_file, get_path_reactivity

	if not frappe.local.meteor_ignores:
		apps_last_first = apps[::-1]
		list_apps_remove = process_hooks_apps(apps_last_first)
		list_meteor_files_add, list_meteor_files_remove = process_hooks_meteor_templates(apps_last_first, "fluorine_files_templates")
		list_meteor_files_folders_add, list_meteor_files_folders_remove = process_hooks_meteor_templates(apps_last_first, "fluorine_files_folders")
		list_meteor_tplt_add, list_meteor_tplt_remove = process_hooks_meteor_templates(apps_last_first, "fluorine_meteor_templates")

		list_ignores = frappe._dict({
			"remove":{
				"apps": list_apps_remove,
				"files_folders": list_meteor_files_folders_remove,
				"meteor_files_templates": list_meteor_files_remove,
				"meteor_templates": list_meteor_tplt_remove
			},
			"add":{
				"files_folders": list_meteor_files_folders_add,
				"meteor_files": list_meteor_files_add,
				"meteor_templates": list_meteor_tplt_add
			},
		    "templates_to_remove": frappe.local.templates_found_remove,
			"templates_to_add": frappe.local.templates_found_add

		})

		#this is for teste how it will stay when cached
		#save_js_file(os.path.join(get_path_reactivity(), "teste_list_dump.json"), list_ignores)
		frappe.local.meteor_ignores = list_ignores

		# Process list_ignores from all installed apps.
		# Last installed app process last.
		# In this way last installed app can remove or add what others added or removed
		apps_last_last = apps
		process_ignores_from_modules(apps_last_last, "proces_all_meteor_lists", frappe.local.meteor_ignores)


def fluorine_build_context(context, whatfor):

	from file import make_all_files_with_symlink, empty_directory, get_path_reactivity#, save_js_file
	#import fnmatch

	#c = lambda t:re.compile(t, re.S|re.M)

	frappe.local.context = context
	frappe.local.fenv = None
	frappe.local.floader = None
	frappe.local.meteor_map_path = None
	frappe.local.meteor_Templates = None
	frappe.local.meteor_dynamic_templates_remove = frappe._dict({})
	frappe.local.jinja_blocks = None
	frappe.local.meteor_ignores = None
	#frappe.local.templates_found_add = set([])
	frappe.local.templates_found_add = frappe._dict({})
	#frappe.local.templates_found_remove = set([])
	frappe.local.templates_found_remove = frappe._dict({})

	frappe.local.meteor_map_templates = OrderedDict()#frappe._dict({})
	frappe.local.templates_referenced = []

	frappe.local.context.files_to_add = []#frappe._dict({})
	frappe.local.context.files_to_remove = []#frappe._dict({})

	frappe.local.files_to_add = frappe._dict({})
	frappe.local.files_to_remove = frappe._dict({})
	frappe.local.module_registe = frappe._dict({})

	path_reactivity = get_path_reactivity()
	devmode = context.developer_mode
	refresh = False
	space_compile = True
	apps = frappe.get_installed_apps()#[::-1]

	make_meteor_ignor_files(apps)
	#process_ignores_from_files(apps)
	if devmode:
		frefresh = os.path.join(path_reactivity, "common_site_config.json")
		refresh = True
		if os.path.exists(frefresh):
			f = frappe.get_file_json(frefresh)
			meteor = f.get("meteor_folder", {})
			refresh = meteor.get("folder_refresh", True)
			space_compile = meteor.get("compile", True)

	if refresh or space_compile or whatfor == "meteor_app":
		process_react_templates(context, apps[::-1], whatfor)

	if refresh:
		#list_meteor_files_add, list_meteor_files_remove = process_hooks_meteor_templates(apps, "fluorine_files_templates")
		#list_meteor_files_folders_add, list_meteor_files_folders_remove = process_hooks_meteor_templates(apps, "fluorine_files_folders")
		#ignore = {"templates":list_meteor_files_remove, "files_folders":list_meteor_files_folders_remove}
		fluorine_publicjs_dst_path = os.path.join(path_reactivity, whatfor)
		empty_directory(fluorine_publicjs_dst_path, ignore=(".meteor",))
		#pattern = fnmatch.translate("*.xhtml")
		#frappe.local.templates_found_remove.add(c(pattern))
		#frappe.local.meteor_ignores["templates_remove"] = frappe.local.templates_found_remove
		print "context files_to_add {}".format(context.files_to_add)
		make_all_files_with_symlink(fluorine_publicjs_dst_path, whatfor, meteor_ignore=frappe.local.meteor_ignores, custom_pattern=["*.xhtml"])

	make_meteor_props(context, whatfor)

	return context

"""
def check_in_files_remove_list(app, template, list_meteor_files_remove):

	for name in list_meteor_files_remove.get(app, []):
		if name == template:
			return True

	return False
"""

def process_react_templates(context, apps, whatfor):

	from react_file_loader import read_client_xhtml_files, get_custom_pattern
	#from fjinja import process_hooks_apps, process_hooks_meteor_templates
	#first installed app first
	#list_apps_remove = process_hooks_apps(apps)
	#list_meteor_files_add, list_meteor_files_remove = process_hooks_meteor_templates(apps, "fluorine_files_templates")
	#list_meteor_files_folders_add, list_meteor_files_folders_remove = process_hooks_meteor_templates(apps, "fluorine_files_folders")
	spacebars_templates = {}
	#spacebars_context = []

	#ignore = {"templates":list_meteor_files_remove, "files_folders":list_meteor_files_folders_remove}
	list_apps_remove = frappe.local.meteor_ignores.get("remove").get("apps")

	custom_pattern = get_custom_pattern(whatfor, custom_pattern=None)
	for app in apps:
		if app in list_apps_remove:
			continue
		pathname = frappe.get_app_path(app)
		path = os.path.join(pathname, "templates", "react")
		if os.path.exists(path):
			files = read_client_xhtml_files(path, whatfor, app, meteor_ignore=frappe.local.meteor_ignores, custom_pattern=custom_pattern)
			for f in files:
				for obj in reversed(f):
				#for obj in f:
					file_path = obj.get("path")
					file_name = obj.get("name")
					root = file_path[:-len(file_name)]
					spacebars_template_path = os.path.join(os.path.relpath(root, pathname), file_name)
					#if not check_in_files_remove_list(app, spacebars_template_path, list_meteor_files_remove):
					addto_meteor_templates_list(spacebars_template_path)
						#spacebars_context.append(frappe._dict({"file_path": file_path, "file_name": file_name, "app_path": pathname, "appname": app, "whatfor": whatfor }))

	#get the context from all the python files of templates
	get_xhtml_context(context)

	#get all the templates to use
	#mtl = get_meteor_template_list()
	#and compile them all
	#out = compile_jinja_templates(mtl, context, whatfor)
	#TODO get from hooks
	from reactivity import extras_context_methods
	#from the first app to the last installed to override the changes made by first installed apps
	get_extra_context_func(context, apps[::-1], extras_context_methods)

	get_general_context(context, apps[::-1], whatfor)

	out = compile_jinja_templates(context, whatfor)

	spacebars_templates.update(out)
	#only compile if meteor_app or meteor_frappe
	if spacebars_templates:# and whatfor in ("meteor_app", "meteor_frappe"):
		compiled_spacebars_js = compile_spacebars_templates(spacebars_templates)
		arr = compiled_spacebars_js.split("__templates__\n")
		arr.insert(0, "(function(){\n")
		arr.append("})();\n")
		context.compiled_spacebars_js = arr


def addto_meteor_templates_list(template_path):
	if not frappe.local.meteor_map_templates.get(template_path, None):# and template_path not in frappe.local.templates_referenced:
		template = fluorine_get_fenv().get_template(template_path)
		frappe.local.meteor_map_templates.get(template_path).update({"template_obj": template})
		#TODO get the context from file of the template...pass the context, the template object and template_path
		#TODO with template_path and frappe.local.meteor_map_templates.get(template_path) get refs if needed to pass macro template object
		#TODO get the context from frappe.local.context!
		get_xhtml_files_to_add_remove(frappe.local.context, template_path)
		print "calling render template from addto_meteor_templates_list {}".format(template_path)
		return True
	return False
	#return fluorine_get_fenv().addto_meteor_templates_list(template_path)


def get_general_context(context, apps, whatfor):

	from fluorine.utils.module import get_app_module

	ctx = frappe._dict()

	for app in apps:
		app_path = frappe.get_app_path(app)
		path = os.path.join(app_path, "templates", "react", whatfor)
		module = get_app_module(path, app, app_path, "meteor_general_context.py")
		if module:
			if hasattr(module, "get_context"):
				nctx = module.get_context(context, ctx) or []
				appname = nctx.get("appname")
				pattern = nctx.get("pattern")
				action = nctx.get("action")
				startpath = nctx.get("folders") or []
				if not ctx.get(appname):
					ctx[appname] = []

				ctx[appname].append({"pattern": pattern, "action": action, "folders": startpath})

	for k,v in ctx.iteritems():
		pattern = v.get("pattern")
		startpath = v.get("startpath")
		if v.get("action") == "add":
			frappe.local.files_to_add.get(k).append({"tname": "", "pattern": pattern, "folders": startpath})
		elif v.get("action") == "remove":
			frappe.local.files_to_remove.get(k).append({"tname": "", "pattern": pattern, "folders": startpath})

	return

def get_extra_context_func(context, apps, extras):

	for app in apps:
		obj = frappe.local.module_registe.get(app)
		if not obj:
			continue
		module = obj.module
		template_path = obj.template_path
		for extra in extras:
			if hasattr(module, extra):
				extra_func = getattr(module, extra)#estava 'method_name'
				extra_func(context, app, template_path)


def get_xhtml_files_to_add_remove(context, template_path):
	obj = frappe.local.meteor_map_templates.get(template_path)
	path = obj.realpath[:-6] + ".py"
	appname = obj.get("appname")
	module = get_xhtml_module(appname, template_path, path)
	if module:

		if hasattr(module, "get_files_to_add"):
			ret = module.get_files_to_add(context, appname, template_path, obj.get("template_obj"))
			if ret:
				if isinstance(ret, basestring):
					context.files_to_add.append({"tname": "", "pattern": ret, "page": template_path})
				else:
					context.files_to_add.append(ret)

		if hasattr(module, "get_files_to_remove"):
			ret = module.get_files_to_remove(context, appname, template_path, obj.get("template_obj"))
			if ret:
				if isinstance(ret, basestring):
					context.files_to_remove.append({"tname": "", "pattern": ret, "page": template_path})
				else:
					context.files_to_remove.append(ret)

def get_xhtml_context(context):

	for template_path in reversed(frappe.local.meteor_map_templates.keys()):
		obj = frappe.local.meteor_map_templates.get(template_path)
		path = obj.realpath[:-6] + ".py"
		appname = obj.get("appname")
		module = get_xhtml_module(appname, template_path, path)
		if module:
			if hasattr(module, "get_context"):
				ret = module.get_context(context, appname, template_path, obj.get("template_obj"))
				if ret:
					#print "get context app_path 6 controller_path {} ret {}".format(controller_path + ".py", ret)
					context.update(ret)
			if hasattr(module, "get_children"):
				context.get_children = module.get_children

#TODO - ver file.py function process_ignores_from_files
def get_xhtml_module(appname, template_path, path):

	if os.path.exists(path):
		controller_path = os.path.join(appname, template_path).replace(os.path.sep, ".")[:-6]
		module = frappe.get_module(controller_path)
		frappe.local.module_registe[appname] = frappe._dict({"template_path": template_path, "module": module})
		return module

	return None


def get_meteor_template_list():
	return fluorine_get_fenv().get_meteor_template_list() or {}

"""
def compile_spacebar_templates(context, whatfor):

	from react_file_loader import read_client_files
	from file import save_file

	#first installed app first
	apps = frappe.get_installed_apps()#[::-1]

	spacebars_templates = {}

	for app in apps:

		pathname = frappe.get_app_path(app)
		path = os.path.join(pathname, "templates", "react")
		if os.path.exists(path):
			files = read_client_files(path, whatfor, extension="xhtml")
			for f in files:
				for obj in reversed(f):
					file_path = obj.get("path")
					out = render_spacebar_html(context, file_path, obj.get("name"), pathname, app, whatfor)
					if whatfor in ("meteor_app", "meteor_frappe"):
						spacebars_templates.update(out)
						context.update(out)
					#dstPath = os.path.join(obj.get("filePath"), obj.get("fileName") + ".html")
					#content = ""
					#for k in out.keys():
					#	content = content + out[k] + "\n"
					#if content:
					#	save_file(dstPath, content)

	#only compile if meteor_app or meteor_frappe
	if spacebars_templates and whatfor in ("meteor_app", "meteor_frappe"):
		compiled_spacebars_js = compile_spacebars_templates(spacebars_templates)
		arr = compiled_spacebars_js.split("__templates__\n")
		arr.insert(0, "(function(){\n")
		arr.append("})();\n")
		context.compiled_spacebars_js = arr
"""

def make_meteor_props(context, whatfor):
	from file import get_path_reactivity, get_meteor_release, get_meteor_config
	from . import meteor_url_path_prefix

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

	props = get_meteor_config(context.meteor_root_url, context.meteor_root_url_port, "", context.meteor_autoupdate_version,\
							context.meteor_autoupdate_version_freshable, context.meteorRelease, whatfor)

	save_meteor_props(props, meteor_runtime_path)

	save_meteor_props("__meteor_runtime_config__.ROOT_URL_PATH_PREFIX = '" + meteor_url_path_prefix(whatfor) + "';", meteor_root_url_prefix)

def save_meteor_props(props, path):
	from . import file
	file.save_file(path, props)

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

"""
def get_page(url, context):
	from bs4 import BeautifulSoup
	import urllib2, json, ast

	scripts = []
	html = BeautifulSoup(urllib2.urlopen(url).read())
	for link in html.find_all('script'):
		src = link.get("src")
		if src:
			scripts.append(src)
		else:
			#uq = urllib2.unquote(link.string)
			#mc = urllib2.unquote(link.string)
			#u = mc.split("(")[2][:-3]
			#mc = urllib2.unquote(str(link.string))

			#get __meteor_runtime_config__ string and convert to object and unquote
			c = urllib2.unquote(ast.literal_eval(link.string.split("(")[2][:-3]))
			meteor_config = json.loads(c)
			meteor_config["ROOT_URL"] = url
			meteor_config["DDP_DEFAULT_CONNECTION_URL"] = url
			context.meteor_runtime_config = json.dumps(meteor_config)
			#print "scripts meteor {}".format(json.loads(c).get("ROOT_URL"))

	return scripts
"""


"""
def render_spacebar_html(context, file_path, file_name, app_path, appname, whatfor):

	py_path = file_path[:-5]
	root = file_path[:-len(file_name)]
	context.spacebars_template = os.path.join(os.path.relpath(root, app_path), file_name)
	if os.path.exists(os.path.join(root, py_path + ".py")):
		controller_path = os.path.join(appname, context.spacebars_template).replace(os.path.sep, ".")[:-5]
		print "app_path 4 {} root {} context.spacebars_template {}".format(controller_path + ".py", root, context.spacebars_template)
		module = frappe.get_module(controller_path)
		if module:
			if hasattr(module, "get_context"):
				ret = module.get_context(context)
				if ret:
					context.update(ret)
			if hasattr(module, "get_children"):
				context.get_children = module.get_children
	#heritage
	out = fluorine_render_blocks(context, whatfor=whatfor)

	return out
"""

"""
def get_html_to_client(whatfor):
	from react_file_loader import copy_client_files, read_client_files, remove_directory

	fluorine_temp_path = os.path.join(frappe.get_app_path("fluorine"), "templates", "react", "temp")
	frappe.create_folder(fluorine_temp_path)
	copy_client_files(fluorine_temp_path, extension="html")
	files = read_client_files(fluorine_temp_path, whatfor, extension="html")

	hooks_js = move_to_public(files, whatfor)

	remove_directory(fluorine_temp_path)

	return hooks_js


def move_to_public(files, whatfor):
	from fluorine.utils import assets_public_path
	hooks_js = {"client_hooks_html":[]}
	fpath = assets_public_path

	for f in files:
		hooks_js["client_hooks_html"].extend(prepare_files(f, fpath))

	return hooks_js


def prepare_files(files):
	hooks = []
	for f in reversed(files):
		hooks.append(f)

	return hooks
"""

"""
def fluorine_build_context2(context, whatfor):

	#print "befores fluorine_spacebars_build_context path {}".format(path)
	#if path.find(".") == -1 and not path == "404":
		#print "news fluorine_spacebars_build_context path {}".format(path)
	#fl = frappe.get_doc("Fluorine Reactivity")
	#if fl.fluorine_base_template and fl.fluorine_base_template.lower() != "default":
	#	app_base_template = fl.fluorine_base_template
	#else:
	#	app_base_template = frappe.get_hooks("base_template")
	#	if not app_base_template:
	#		app_base_template = "templates/base.html"

	#if context.base_template_path == app_base_template:

		#if not context.spacebars_data:
		#	context.spacebars_data = {}
		#print "context data path in override {}".format(context.data)
		#context.update(context.data or {})
	apps = frappe.get_installed_apps()#[::-1]
	#apps.remove("fluorine")
	name_templates = []
	spacebars_templates = {}

	for app in apps:
		#print "app {}".format(app)
		pathname = frappe.get_app_path(app)#get_package_path(app, "", "")
		if pathname:
			for root, dirs, files in os.walk(os.path.join(pathname, "templates", "react")):
				for file in files:
					if file.endswith(".html"):
						#print "app is {} path is {}".format(app, os.path.join(os.path.relpath(root, pathname), file))
						#print(os.path.join(root, file[:-5] + ".py"))
						#filename = os.path.join(root, file)
						context.spacebars_template = os.path.join(os.path.relpath(root, pathname), file)
						if os.path.exists(os.path.join(root, file[:-5] + ".py")):
							controller_path = os.path.join(app, context.spacebars_template).replace(os.path.sep, ".")[:-5]
							print "app_path 3 {} root {} context.spacebars_template {}".format(controller_path + ".py", root, context.spacebars_template)
							module = frappe.get_module(controller_path)
							if module:
								if hasattr(module, "get_context"):
									ret = module.get_context(context)
									if ret:
										context.update(ret)
								if hasattr(module, "get_children"):
									context.get_children = module.get_children
						#heritage
						out = fluorine_render_blocks(context)
						#context.spacebars_data.update(out)
						print "out {}".format(out)
						#print "context teste123 {} out {}".format(context.teste123, out.get("teste123", None))
						#print frappe.utils.pprint_dict(out)
						spacebars_templates.update(out)
						#for name in out:
						#	name_templates.append(name)
						context.update(out)
						#print "new spacebars_data {}".format(context)
	#context.data.update(context.spacebars_data or {})
#print "In fluorine_spacebars_build_context"
	compiled_spacebars_js = compile_spacebars_templates(spacebars_templates)
	arr = compiled_spacebars_js.split("__templates__\n")
	arr.insert(0, "(function(){\n")
	arr.append("})();\n")

	hooks_js = get_js_to_client(whatfor)

	context.compiled_spacebars_js = arr

	context.update(hooks_js)
	#print "A compilar templates \n{}".format(context.compiled_spacebars_js)

	return context
"""

def make_heritage(block, context):
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
	import zerorpc
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
#print "In override spacebars"
#frappe.website.context.build_context = fluorine_spacebars_build_context
#frappe.website.render.build_page = fluorine_spacebars_build_page
#frappe.website.context.__dict__["get_context"] = fluorine_spacebars_get_context

#print "frappe.website.context.get_context {}".format(frappe.website.context.__dict__["get_context"])