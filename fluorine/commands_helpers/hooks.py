__author__ = 'luissaguas'


def _change_hook(site=None, state="start"):
	from fluorine.utils.fhooks import FluorineHooks

	with FluorineHooks(site=site) as fh:
		if state == "start":
			fh.change_base_template(page_default=False)
			fh.remove_hook_app_include()
		elif state == "stop":
			fh.change_base_template(page_default=True)
			fh.remove_hook_app_include()
		elif state == "production":
			fh.change_base_template(page_default=True)
			#app_include_js, app_include_css = get_meteor_app_files()
			fh.hook_app_include(["/assets/js/meteor_app.min.js"], ["/assets/css/meteor_app.css"])
