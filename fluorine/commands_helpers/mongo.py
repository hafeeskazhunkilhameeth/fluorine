__author__ = 'luissaguas'


def _check_custom_mongodb(doc):
	from fluorine.utils.file import get_path_reactivity, save_js_file
	from fluorine.utils.reactivity import meteor_config
	import click, os

	path_reactivity = get_path_reactivity()
	config_file_path = os.path.join(path_reactivity, "common_site_config.json")
	mongo_conf = meteor_config.get("meteor_mongo", None)
	if not mongo_conf or mongo_conf.get("type", None) == "default":
		if doc.fluor_mongo_host:
			mghost = doc.fluor_mongo_host.replace("http://","").replace("mongodb://","").strip(' \t\n\r')
		else:
			mghost = "localhost"
		mgport = doc.fluor_mongo_port or 27017
		mgdb = doc.fluor_mongo_database.strip() or "fluorine"
		meteor_config["meteor_mongo"] = {
			"host": mghost,
			"port": mgport,
			"db": mgdb,
		}
		save_js_file(config_file_path, meteor_config)

		click.echo("Using mongodb with host {}, port {} and db {}.".format(mghost, mgport, mgdb))
	else:
		click.echo("Using mongodb with host {}, port {} and db {}.".format(mongo_conf.get("host"), mongo_conf.get("port"), mongo_conf.get("db")))

	return True