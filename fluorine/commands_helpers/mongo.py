__author__ = 'luissaguas'


def _check_custom_mongodb(doc):
	from fluorine.utils.file import get_path_reactivity, save_js_file
	import frappe, click, os

	path_reactivity = get_path_reactivity()
	config_file_path = os.path.join(path_reactivity, "common_site_config.json")
	meteor_config = frappe.get_file_json(config_file_path)
	mongo_conf = meteor_config.get("meteor_mongo", None)
	if not mongo_conf or mongo_conf.get("type", None) == "default":
		#click.echo("You must set mongo custom in reactivity/common_site_config.json.")
		click.echo("Using mongodb with localhost, port 27017 and db fluorine.")
		mghost = doc.fluor_mongo_host.strip()
		mgport = doc.fluor_mongo_port or 27017
		mgdb = doc.fluor_mongo_database.strip() or "fluorine"
		meteor_config["meteor_mongo"] = {
			"host": mghost,
			"port": mgport,
			"db": mgdb,
		}
		save_js_file(config_file_path, meteor_config)
	else:
		click.echo("Using mongodb with host {}, port {} and db {}.".format(mongo_conf.get("host"), mongo_conf.get("port"), mongo_conf.get("db")))

	return True