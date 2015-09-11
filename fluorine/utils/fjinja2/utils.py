# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'luissaguas'

from jinja2 import contextfunction, contextfilter
from jinja2.utils import concat
import frappe, re



c = lambda t:re.compile(t, re.S|re.M)

STARTTEMPLATE_SUB_ALL = c(r"<\s*template\s+name\s*=\s*(['\"])(\w+)\1(.*?)\s*>(.*?)<\s*/\s*template\s*>")
STARTDIV_SUB_ALL = r"<\s*div\s+class\s*=\s*(['\"])%s\1\s*>(.*?)<\s*/\s*div\s*>"


def is_in_extend_path(doc, template):
	for d in doc.docs:
		if d.template == template:
			return d
		found = is_in_extend_path(d, template)
		if found:
			return found
	return None

def get_template_from_doc(doc, tname, encoding="utf-8"):
	from fluorine.utils.file import read

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

"""
def get_pattern_path(name, path):
	pattern = path + r"/(?:.+?/)?(?:(?:%s)/(?:.+)|(?:%s/?$))" % (name, name)
	#pattern = path + r"(/.+?/%s/.*)?|(/.+/%s$)?" % (name, name)
	return pattern
"""

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

@contextfilter
def mtlog(ctx, msg):
	from fluorine.commands import meteor_echo

	obj = frappe.local.context.current_xhtml_template

	msg = "fluorine template path: %s\n\nmeteor template:%s\n\n%s" % (ctx.name, obj.get("tname"), msg)

	meteor_echo(msg, 80)

@contextfunction
def tkeep(ctx, patterns):
	import os
	from fluorine.utils.fjinja2.extension_template import get_appname, get_template_path
	#from fluorine.utils.spacebars_template import check_refs

	obj = frappe.local.context.current_xhtml_template
	appname = get_appname(obj.get("template"))
	tname = obj.get("tname")
	template_path = get_template_path(appname, obj.get("template"))
	#print "ctx.name {} blocks {}".format(ctx.name, obj.get("template"))
	#obj = frappe.local.meteor_map_templates.get(template_path)
	#refs = obj.get("refs")
	#ref = check_refs(tname, refs)
	ref = get_meteor_template_parent_path(tname, template_path)

	if not ref:
		frappe.throw("mtkeep command only can be used inside meteor templates and only with fluorine templates (Ex. xhtml files) that extends another fluorine template.")
	#get parent data. This template is in onother template because tkeep is used when extends templates
	parent_obj = frappe.local.meteor_map_templates.get(ref)
	parent_appname = parent_obj.get("appname")

	#app_path = frappe.get_app_path(parent_appname)

	pfs_out = frappe.local.context.pfs_out
	list_meteor_files_folders_add = pfs_out.get_add_files_folders()
	appname_files_folder_add = list_meteor_files_folders_add.get(parent_appname)
	if not appname_files_folder_add:
		list_meteor_files_folders_add[parent_appname] = set([])

	appname_files_folder_add = list_meteor_files_folders_add.get(parent_appname)

	if isinstance(patterns, basestring):
		patterns = [patterns]

	reactpath = os.path.join("templates", "react")
	relpath = os.path.relpath(ref, reactpath)

	tpath = relpath.rsplit(".", 1)[0]

	for pattern in patterns:
		pattern = "%s/.*/?%s/%s" % (tpath, tname, pattern)
		#print "pattern to use %s" % pattern
		p = c(pattern)
		appname_files_folder_add.add(p)
	#export_meteor_template_out(tname, template_path)
	#print "tname {} template_real_path {} pattern {}".format(obj.get("tname"), obj.get("template"), patterns)


	"""
	if not page:
		obj = frappe.local.meteor_map_templates.get(ctx.name)
		refs = obj.get("refs")
		page = get_deep_refs(refs, tname, deep)

	fadd = ctx.get("files_to_add")
	if fadd == None:
		ctx["files_to_add"] = {}
		fadd = ctx.get("files_to_add")

	fadd.append({"tname": tname, "pattern": patterns, "page": page})
	"""

"""
def local_tkeep(ctx, tname, page, patterns=None):

	fadd = ctx.get("files_to_add")
	if fadd == None:
		ctx["files_to_add"] = {}
		fadd = ctx.get("files_to_add")

	if  patterns and isinstance(patterns, basestring):
		patterns = [patterns]

	obj = frappe.local.meteor_map_templates.get(page)
	appname = obj.get("appname")

	if not fadd.get(appname):
		fadd[appname] = []
	template_path = obj.get("template")

	in_ext = template_path.rsplit(".", 1)[1]
	ext_len = len(in_ext) + 1

	if not patterns:
		pattern = get_pattern_path(tname, template_path[:-ext_len])
		fadd.get(appname).append({"tname": page, "pattern":pattern})
	elif tname:
		for pattern in patterns:
			pat = template_path[:-ext_len] + r"/.*/"+ tname + "/" + pattern
			fadd.get(appname).append({"tname": page, "pattern": pat})
	else:
		for pattern in patterns:
			fadd.get(appname).append({"tname": page, "pattern": pattern})
"""

def get_msuper_inner_content(ctx, source):
	s = STARTTEMPLATE_SUB_ALL.search(source)
	if s:
		name = s.group(2)
		source = s.group(4)
		#TODO remove not? or remove all code below
		if not ctx.get("developer_mode"):
			m = re.search(STARTDIV_SUB_ALL % (name,), source, re.S|re.M)
			if m:
				source = m.group(2)
	return source

@contextfunction
def msuper(ctx, adeep=1, rdeep=0, tkeep=None, tname=None):
	ocode = ""
	#page = ctx.name
	tobj = frappe.local.context.current_xhtml_template
	#print "ctx.name {}".format(ctx.name)
	page = tobj.get("relpath")
	if not tname:
		tname = tobj.get("tname")

	obj = frappe.local.meteor_map_templates.get(page)
	refs = obj.get("refs")

	if not isinstance(rdeep, (list, tuple)):
		rdeep = [rdeep]

	if not isinstance(adeep, (list, tuple)):
		adeep = [adeep]

	if tkeep in (False, True) and not isinstance(tkeep, (list, tuple)):
		tkeep = [tkeep]

	for deep in adeep:
		if deep >= 1:
			page = get_deep_refs(refs, tname, deep)

		if page:
			sobj = frappe.local.meteor_map_templates.get(page)
			template = sobj.get("template_obj")
			render = template.blocks.get(tname)
			code = concat(render(template.new_context(ctx)))
			ocode = "%s\n%s" % (ocode, get_msuper_inner_content(ctx, code))
			if not tkeep or deep in tkeep:
				print "page {} and tname {} relpath {} tkeep {}\n".format(page, tname, tobj.get("relpath"), tkeep)
				export_meteor_template_out(tname, page)
			else:
				appname = sobj.get("appname")
				remove_meteor_template_from_out(appname, tname, page)
		else:
			frappe.throw("Fluorine do not found the page to add for meteor template %s" % tname)

	for deep in rdeep:
		if deep >= 1:
			page = get_deep_refs(refs, tname, deep)

			if page:
				sobj = frappe.local.meteor_map_templates.get(page)
				appname = sobj.get("appname")
				remove_meteor_template_from_out(appname, tname, page)
			else:
				frappe.throw("Fluorine do not found the page to remove for meteor template %s" % tname)

	return ocode

@contextfunction
def mself(ctx):
	return msuper(ctx, deep=0)

def flat_refs(template_path):
	flat = []
	obj = frappe.local.meteor_map_templates.get(template_path)
	refs = obj.get("refs") or []
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
	return value + "  " + content


def add_meteor_template_to_dict(appname, tname, template_path):
	toadd = frappe.local.context.files_to_add

	if not toadd.get(appname):
		toadd[appname] = {}
	tappname = toadd.get(appname)
	if not tappname.get(template_path):
		tappname[template_path] = set([])
	tappname.get(template_path).add(tname)


def add_fluroine_template_to_dict(appname, template_path, is_ref=True):

	ctx = frappe.local.files_to_add

	if not ctx.get(appname):
		ctx[appname] = []

	found = False
	for obj in ctx.get(appname):
		name = obj.get("tname")
		if template_path == name:
			found = True
			break
	if not found:
		ctx.get(appname).append({"tname": template_path, "ref": is_ref})


def add_meteor_template_to_out(appname, tname, template_path, is_ref=True):
	add_fluroine_template_to_dict(appname, template_path, is_ref=is_ref)
	add_meteor_template_to_dict(appname, tname, template_path)


def export_meteor_template_out(tname, template_path):
	obj = frappe.local.meteor_map_templates.get(template_path)
	appname = obj.get("appname")
	add_meteor_template_to_out(appname, tname, template_path)


def get_meteor_template_parent_path(tname, template_path):
	from fluorine.utils.spacebars_template import check_refs

	obj = frappe.local.meteor_map_templates.get(template_path)
	refs = obj.get("refs")
	return check_refs(tname, refs)


def remove_meteor_template_from_out(appname, tname, template_path, is_ref=True):
	toadd = frappe.local.context.files_to_add

	tappname = toadd.get(appname) or {}
	mtemplates = tappname.get(template_path) or []

	found = False

	for t in mtemplates:
		if t == tname:
			found = True
			break

	if found:
		mtemplates.remove(tname)
