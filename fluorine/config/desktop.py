from frappe import _

def get_data():
	return {
		"Fluorine": {
			"color": "#336600",
			"icon": "icon-beaker",
			"type": "module",
			"label": _("Fluorine"),

		},
		"Fluorine Admin":{
			"color": "#E62E00",
			"icon": "icon-cogs",
			"type": "page",
			"link": "fluorine-admin"
		}
	}
