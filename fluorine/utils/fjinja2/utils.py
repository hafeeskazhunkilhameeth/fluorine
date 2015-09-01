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

def get_pattern_path(name, path):
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
	template_path = obj.get("template")
	if not patterns:
		pattern = get_pattern_path(tname, template_path[:-6])
		fadd.get(appname).append({"tname": page, "pattern":pattern})
	elif tname:
		for pattern in patterns:
			pat = template_path[:-6] + r"/.*/"+ tname + "/" + pattern
			fadd.get(appname).append({"tname": page, "pattern": pat})
	else:
		for pattern in patterns:
			fadd.get(appname).append({"tname": page, "pattern": pattern})

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
def msuper(ctx, tname, deep=1):
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
		code = concat(render(template.new_context(ctx)))
		code = get_msuper_inner_content(ctx, code)


	return code

@contextfunction
def mself(ctx, tname):
	return msuper(ctx, tname, deep=0)

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
