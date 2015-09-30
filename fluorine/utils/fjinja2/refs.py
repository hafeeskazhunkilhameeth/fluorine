__author__ = 'luissaguas'


import frappe, re



def get_all_know_meteor_templates():
	mtemplates = frappe._dict()
	for k, v in frappe.local.meteor_map_templates.iteritems():
		template = v.get("template_obj")
		if template:
			for block in template.blocks.keys():
				appname = v.get("appname")
				if not mtemplates.get(appname):
					mtemplates[appname] = []
				mtemplates[appname].append(block)

	return mtemplates


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



def get_deep_refs(refs, tname, deep):

	if deep == 1:
		return get_page_from_meteor_template(refs, tname)

	page = None
	#first is the extends so only this count for deep
	if refs:
		obj = frappe.local.meteor_map_templates.get(refs[0])
		nrefs = obj.get("refs")
		page = get_deep_refs(nrefs, tname, deep-1)

	return page


def get_page_templates_and_refs(page):

	parent_relation = frappe._dict()

	tnames = []

	obj = frappe.local.meteor_map_templates.get(page)
	template = obj.get("template_obj")
	refs = obj.get("refs")
	parent_relation[page] = []

	for tname in template.blocks.keys():
		tnames.append(tname)

	alltnames = {"templates": tnames, "appname": obj.get("appname")}
	parent_relation.get(page).append(alltnames)

	for ref in refs:
		res = get_page_templates_and_refs(ref)
		alltnames["childs"] = res

	return parent_relation


def get_page_from_meteor_template(refs, tname):

	for ref in refs:
		sobj = frappe.local.meteor_map_templates.get(ref)
		template = sobj.get("template_obj")
		for block in template.blocks.keys():
			if block == tname.strip():
				return ref

	return None


def flat_refs(template_path):
	flat = []
	obj = frappe.local.meteor_map_templates.get(template_path)
	refs = obj.get("refs") or []
	flat.extend(refs)
	for ref in refs:
		flat.extend(flat_refs(ref))

	return flat

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


def get_meteor_template_parent_path(tname, template_path):

	obj = frappe.local.meteor_map_templates.get(template_path)
	refs = obj.get("refs")
	return check_refs(tname, refs)

def add_to_path(template, refs, tcont, whatfor, context, parent_package):

	api = None

	for tname in tcont.keys():
		if template and tname not in template.blocks.keys():
			ref = check_refs(tname, refs)
		else:
			ref = template.name

		if ref:
			obj = frappe.local.meteor_map_templates.get(ref)
			appname = obj.get("appname")
			package_name = obj.get("package_name")
			if not package_name:
				package = parent_package
			else:
				package = frappe.local.packages.get(package_name)

			api = export_meteor_template(appname, whatfor, ref, tname, context, package.apis)

	return api


def export_meteor_template(appname, whatfor, template_path, tname, context, package_apis):
	from fluorine.utils.api import Api, filter_api_list_members
	from fluorine.utils.context import get_app_meteor_template_files_to_process


	obj = frappe.local.meteor_map_templates.get(template_path)
	readed_meteor_template = obj.get("readed_meteor_templates")
	if tname in readed_meteor_template:
		return get_api_from_meteor_template_and_fluorine_template_name(template_path, tname)

	readed_meteor_template.append(tname)
	api = Api(appname, whatfor, devmode=context.developer_mode)
	api.set_meteor_template_name(tname)
	api.set_fluorine_template_name(template_path)
	get_app_meteor_template_files_to_process(appname, whatfor, template_path, tname, api, context)
	filter_api_list_members(api, package_apis)
	package_apis.append(api)

	return api

def export_fluorine_template(appname, whatfor, template_path, context, package_apis):
	from fluorine.utils.api import Api, filter_api_list_members
	from fluorine.utils.context import get_app_fluorine_template_files_to_process


	api = Api(appname, whatfor, devmode=context.developer_mode)
	api.set_fluorine_template_name(template_path)
	get_app_fluorine_template_files_to_process(appname, whatfor, template_path, api, context)
	filter_api_list_members(api, package_apis)
	package_apis.append(api)

	return api


def get_package_from_fluorine_template_path(template_path):

	obj = frappe.local.meteor_map_templates.get(template_path)
	package_name = obj.get("package_name")
	package = frappe.local.packages.get(package_name)

	return package

def get_api_from_meteor_template_and_fluorine_template_name(template_name, meteor_template_name):

	package = get_package_from_fluorine_template_path(template_name)
	for api in package.apis:
		if api.get_meteor_template_name() == meteor_template_name:
			return api
	return None