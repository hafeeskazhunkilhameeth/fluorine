__author__ = 'luissaguas'


from fluorine.utils.mongodb.utils import get_mongo_exports
import os

def save_to_procfile(doc, production_debug=False):
	from fluorine.utils.file import writelines

	procfile, procfile_path = get_procfile()
	#tostart = {"Both": ("meteor_app", "meteor_web"), "Reactive App": ("meteor_app", ), "Reactive Web": ("meteor_web", )}
	#meteor_apps = tostart.get(doc.fluorine_reactivity)

	from fluorine.commands_helpers.meteor import get_meteor_settings

	for app in ("meteor_app", "meteor_web"):
		export_mongo, mongo_default = get_mongo_exports(doc)
		mthost, mtport, forwarded_count = get_root_exports(app)

		if production_debug:
			final_app = app.replace("meteor", "final")
			procfile.insert(0, "%s: (cd apps/reactivity/%s/bundle && ./exec_meteor)\n" %
							(final_app, final_app))
		else:
			if app == "meteor_web" and mongo_default:
				exp_mongo = ""
			else:
				exp_mongo = export_mongo + " && "

			msf= get_meteor_settings(app)
			procfile.insert(0, "%s: (%s%s && export ROOT_URL=%s && cd apps/reactivity/%s && meteor --port %s%s)\n" %
							(app, exp_mongo, forwarded_count, mthost, app, mtport, msf))

		writelines(procfile_path, procfile)


def get_procfile():
	from fluorine.utils.file import readlines
	from fluorine.utils.fjinja2.utils import c

	re_meteor_procfile = c(r"^(meteor_app:|meteor_web:|final_app:|final_web:)")
	procfile_dir = os.path.normpath(os.path.join(os.getcwd(), ".."))
	procfile_path = os.path.join(procfile_dir, "Procfile")

	procfile = readlines(procfile_path)
	procfile = [p for p in procfile if not re_meteor_procfile.match(p)]

	return procfile, procfile_path

def remove_from_procfile():
	from fluorine.utils.file import writelines

	procfile, procfile_path = get_procfile()
	writelines(procfile_path, procfile)


def get_root_exports(app):
	from fluorine.utils.reactivity import meteor_config
	from fluorine.utils.meteor.utils import default_path_prefix, PORT

	meteor_dev = meteor_config.get("meteor_dev", None)
	count = meteor_config.get("meteor_http_forwarded_count") or "1"
	forwarded_count = "export HTTP_FORWARDED_COUNT='" + str(count) + "'"
	if meteor_dev:
		meteor = meteor_dev.get(app)
		default_prefix = default_path_prefix if app=="meteor_app" else ""
		prefix = meteor.get("ROOT_URL_PATH_PREFIX") or ""
		mthost = meteor_dev.get("host") + (prefix if prefix else default_prefix)
		mtport = meteor.get("port") or PORT.get(app)

		return (mthost, mtport, forwarded_count)
