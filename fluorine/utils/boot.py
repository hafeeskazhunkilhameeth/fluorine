__author__ = 'luissaguas'




def boot_session(bootinfo):

	meteor_init = get_meteor_init()
	bootinfo['Fluorine'] = meteor_init



def get_meteor_init():
	return get_meteor_init_file_names()


def get_meteor_init_file_names():
	from fluorine.utils import file_map_site
	return file_map_site
