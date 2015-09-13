__author__ = 'luissaguas'


import frappe, os



def make_page_relations(context, whatfor):
	from fluorine.utils.spacebars_template import fluorine_get_fenv
	from fluorine.utils.file import save_file, get_path_reactivity
	from fluorine.utils import get_encoding
	from fluorine.utils.reactivity import get_read_file_patterns


	file_patterns = get_read_file_patterns()

	if context.page_relations:
		try:
			template_path = "templates/react/page_relations.xhtml"
			template = fluorine_get_fenv().get_template(template_path)
			if template:
				content = template.render(relations={"whatfor": whatfor, "rel": frappe.local.page_relations.get(whatfor)})
				if content and frappe.local.page_relations.get(whatfor):
					obj = frappe.local.meteor_map_templates.get(template_path)
					appname = obj.get("appname")
					app_path = frappe.get_app_path(appname)
					realpath = obj.get("realpath")
					in_ext = realpath.rsplit(".", 1)[1]
					fp = file_patterns.get("*.%s" % in_ext)
					out_ext = fp.get("ext")
					ext_len = len(in_ext) + 1
					dstPath = "%s_%s.%s" % (realpath[:-ext_len], whatfor, out_ext)
					save_file(dstPath, content.encode(get_encoding()))
					path_reactivity = get_path_reactivity()
					app_react_path = os.path.join(app_path, "templates", "react")
					dst_base = os.path.join(path_reactivity, whatfor, os.path.relpath(dstPath, app_react_path))
					os.symlink(dstPath, dst_base)
					print "page_relations {} dstPath {} dst_base {}".format(frappe.local.page_relations.get(whatfor), dstPath, dst_base)
		except:
			pass
