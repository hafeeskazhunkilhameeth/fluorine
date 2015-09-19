__author__ = 'luissaguas'


import frappe


def boot_session(bootinfo):

	meteor_init = get_meteor_init()

	bootinfo['Fluorine'] = {"site": meteor_init}



def get_meteor_init():
	return get_meteor_init_file_names()


def get_meteor_init_file_names():
	from fluorine.utils import fluorine_common_data

	file_map_site = fluorine_common_data.file_map_site
	if not file_map_site:
		return

	current_site = frappe.local.site

	sitename = file_map_site.get(current_site)
	return sitename
