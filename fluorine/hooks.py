app_url=["http://localhost"]
app_name=["fluorines"]
app_icon=["icon-beaker"]
app_color=["#336600"]
app_description=["The most reactive app."]
website_clear_cache=["fluorine.utils.fcache.clear_cache"]
app_publisher=["Luis Fernandes"]
app_title=["Fluorine"]
home_page=["fluorine_home"]
app_version=["0.0.1"]
base_template=["templates/fluorine_base.html"]
app_email=["luisfmfernandes@gmail.com"]

fluorine_files_templates = {
    "ekaiser":{
		"remove": ["templates/react/meteor_web/client/body.xhtml"]
    }
}

fluorine_meteor_templates = {
    "fluorine":{
		"remove": [{"name":"main", "file":"templates/react/meteor_web/client/teste_copy.xhtml"}]
    }
}

fluorine_apps = {
    "ekaiser":{
		"remove": 1
    }
}

"""
fluorine_folders = {
    "ekaiser":{
		"remove": ["path"]
    }
}
"""