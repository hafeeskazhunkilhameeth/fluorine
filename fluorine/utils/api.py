__author__ = 'luissaguas'


import frappe, os



class OnTest(object):

	def __init__(self):
		self.api_use = []
		self.api_imply = []
		self.api_export = []
		self.api_assets = []
		self.api_addFiles = []


	def use(self, pckgnames, architecture=None, options=None):
		self.api_use.append({"packageNames": pckgnames, "architecture": architecture, "options":options})

	def imply(self, pckgnames, architecture=None):
		self.api_imply.append({"packageNames": pckgnames, "architecture": architecture})

	def export(self, exportedObjects, architecture=None, options=None):
		self.api_export.append({"exportedObjects": exportedObjects, "architecture": architecture, "options":options})

	def addAssets(self, filenames, architecture=None):
		self.api_assets.append({"filenames": filenames, "architecture": architecture})


	def addFiles(self, filenames, architecture=None, options=None):
		self.api_addFiles.append({"filenames": filenames, "architecture": architecture, "options": options})



class Cordova(object):
	def __init__(self):
		self._depends = frappe._dict({})

	def depends(self, depends):
		self._depends.update(depends)


class Npm(object):
	def __init__(self):
		self._depends = frappe._dict({})

	def depends(self, depends):
		self._depends.update(depends)



class Api(object):

	def __init__(self, app, whatfor, devmode=True):
		self.developer_mode = devmode
		self.dict_jinja_files = frappe._dict()
		self.dict_final_assets_add = frappe._dict()
		self.dict_final_assets_remove = frappe._dict()
		self.dict_final_files_add = frappe._dict()
		self.dict_final_files_remove = frappe._dict()
		self.dict_packages = frappe._dict()
		self.app = app
		self.whatfor = whatfor
		self.startpath = "templates/react"
		self.template_path = None
		self.template_name = None
		self._describe = None
		self._versionsFrom = None
		self.api_use = []
		self.api_imply = []
		self.api_export = []
		self._Npm = None
		self._Cordova = None
		self.onTest = OnTest()
		self.registerBuildPlugin = {}
		self.public_folder = False
		self.tests_folder = False
		self.meteor_template_name = None
		self.fluorine_template_host_name = None


	def set_meteor_template_name(self, name):
		self.meteor_template_name = name

	def get_meteor_template_name(self):
		return self.meteor_template_name

	def set_fluorine_template_name(self, name):
		self.fluorine_template_host_name = name

	def get_fluorine_template_name(self):
		return self.fluorine_template_host_name

	def versionsFrom(self, version):
		self._versionsFrom = version

	def Npm(self, options):
		if not self._Npm:
			self._Npm = Npm()
		self._Npm.depends(frappe._dict(options))

	def Cordova(self, options):
		if not self._Cordova:
			self._Cordova = Cordova()
		self._Cordova.depends(frappe._dict(options))

	def describe(self, options):
		print "in describe %s" % options
		self._describe = frappe._dict(options)

	def use(self, pckgnames, architecture=None, options=None):
		if isinstance(architecture, basestring):
			architecture = [architecture]
		if isinstance(pckgnames, basestring):
			pckgnames = [pckgnames]
		self.api_use.append({"packageNames": pckgnames, "architecture": architecture, "options":options})

	def imply(self, pckgnames, architecture=None):
		if isinstance(architecture, basestring):
			architecture = [architecture]
		if isinstance(pckgnames, basestring):
			pckgnames = [pckgnames]
		self.api_imply.append({"packageNames": pckgnames, "architecture": architecture})

	def export(self, exportedObjects, architecture=None, options=None):
		if isinstance(architecture, basestring):
			architecture = [architecture]
		if isinstance(exportedObjects, basestring):
			exportedObjects = [exportedObjects]
		self.api_export.append({"exportedObjects": exportedObjects, "architecture": architecture, "options":options})

	def registerBuildPlugin(self, options):
		self.registerBuildPlugin.update(options)

	def getApp(self):
		return self.app

	def set_template_path(self, template_path):
		self.template_path = template_path

	def get_template_path(self):
		return self.template_path

	def set_template_name(self, template_name):
		self.template_path = template_name

	def get_template_name(self):
		return self.template_name

	def set_startpath(self, startpath):
		self.startpath = startpath

	def change_file_path_if_not_relative(self, file_to_add):

		if file_to_add.startswith("/"):
			new_prefix = file_to_add
		else:
			new_prefix = os.path.normpath(os.path.join(self.startpath, file_to_add))

		return new_prefix

	def addAssets(self, files, app=None, architecture=None):
		app, files = self.get_processed_input_data(app, files)

		if isinstance(architecture, basestring):
			architecture = [architecture]

		for file in files:
			new_prefix = self.change_file_path_if_not_relative(file)
			real_path = self.get_real_path(app, new_prefix, file)
			self.dict_final_assets_add[real_path] = frappe._dict({"relative_path": new_prefix, "internal_path": file, "app":app, "architecture": architecture})


	def addFiles(self, files, app=None, architecture=None, options=None, type="normal"):
		app, files = self.get_processed_input_data(app, files)
		if isinstance(architecture, basestring):
			architecture = [architecture]
		for file in files:
			new_prefix = self.change_file_path_if_not_relative(file)
			real_path = self.get_real_path(app, new_prefix, file)
			#print "real_path {} new prefix {}".format(real_path, new_prefix)
			#self.list_final_files_add.append({"source_final_path": final_path, "relative_path": os.path.join(new_prefix, file), "app": app})
			#self.dict_final_files_add[real_path] = {"relative_path": os.path.join(new_prefix, file), "app": app}
			self.dict_final_files_add[real_path] = frappe._dict({"relative_path": new_prefix, "internal_path": file,"app": app, "architecture": architecture, "options": options, "type": type})


	def addJinjaFiles(self, files, app=None, out_ext="html", export=True):
		app, files = self.get_processed_input_data(app, files)
		for file in files:
			new_prefix = self.change_file_path_if_not_relative(file)
			real_path = self.get_real_path(app, new_prefix, file)
			#self.dict_jinja_files[real_path] = {"relative_path": os.path.join(new_prefix, file), "ext_out": out_ext, "export": export, "prefix": new_prefix}
			self.dict_jinja_files[real_path] = frappe._dict({"relative_path": new_prefix, "internal_path": file, "ext_out": out_ext, "export": export, "prefix": new_prefix})

	#add packages only if it is installed
	def addPackages(self, packages):
		from fluorine.utils.meteor.packages import filterPackagesApi

		if isinstance(packages, dict):
			packages = [packages]

		packages_to_add = filterPackagesApi(self.whatfor, packages)
		self.filterPackages(packages_to_add)

	def filterPackages(self, files):
		app, files = self.get_processed_input_data(self.app, files)
		for file in files:
			new_prefix = self.change_file_path_if_not_relative(file)
			real_path = self.get_real_path(app, new_prefix, file)
			package_folder_name = file.rsplit("/", 1)[1]
			self.dict_packages[real_path] = frappe._dict({"relative_path": new_prefix, "internal_path": file, "folder_name": package_folder_name})

	def removeFiles(self, files, app=None):
		app, files = self.get_processed_input_data(app, files)
		for file in files:
			new_prefix = self.change_file_path_if_not_relative(file)
			real_path = self.get_real_path(app, new_prefix, file)
			#self.list_final_files_remove.append(final_path)
			#self.dict_final_files_add[real_path] = {"relative_path": os.path.join(new_prefix, file), "app": app}
			self.dict_final_files_remove[real_path] = frappe._dict({"relative_path": new_prefix, "internal_path": file, "app": app})

	def removeAssets(self, files, app=None):
		app, files = self.get_processed_input_data(app, files)
		for file in files:
			new_prefix = self.change_file_path_if_not_relative(file)
			real_path = self.get_real_path(app, new_prefix, file)
			#self.list_final_files_remove.append(final_path)
			#self.dict_final_files_add[real_path] = {"relative_path": os.path.join(new_prefix, file), "app": app}
			self.dict_final_assets_remove[real_path] = frappe._dict({"relative_path": new_prefix, "internal_path": file, "app": app})


	def is_developer_mode(self):
		return self.developer_mode

	def get_processed_input_data(self, app, files):
		if not app or app.strip() == "":
			app = self.app

		if isinstance(files, basestring):
			files = [files]

		return app, files

	def remove_final_file_from_add_list(self, final_file):
		self.dict_final_files_add.pop(final_file, None)

	def remove_final_file_from_remove_list(self, final_file):
		self.dict_final_files_remove.pop(final_file, None)

	def get_real_path(self, app, path_prefix, file):
		if file.startswith("/"):
			#real_path = os.path.join(path_prefix, file)
			real_path = path_prefix
		else:
			app_path = frappe.get_app_path(app)
			real_path = os.path.join(app_path, path_prefix)

		return real_path

	def get_dict_jinja_files(self):
		return self.dict_jinja_files

	def get_dict_final_Assets_add(self):
		return self.dict_final_assets_add

	def get_dict_final_Assets_remove(self):
		return self.dict_final_assets_remove

	def get_dict_final_files_add(self):
		return self.dict_final_files_add

	def get_dict_final_files_remove(self):
		return self.dict_final_files_remove

	def filter_add_new_dict_members(self, original_dict_files_to_remove):
		self._filter_add_new_dict_members(original_dict_files_to_remove, self.dict_final_files_add)

	def _filter_add_new_dict_members(self, original_dict_files_to_remove, dict_files_add):
		list_original_files_to_remove = original_dict_files_to_remove.keys()
		for new_file in dict_files_add.keys():
			if new_file in list_original_files_to_remove:
				dict_files_add.pop(new_file, None)

	def filter_remove_new_dict_members(self, original_dict_files_to_add):
		self._filter_remove_new_dict_members(original_dict_files_to_add, self.dict_final_files_remove)

	def _filter_remove_new_dict_members(self, original_dict_files_to_add, dict_files_remove):
		list_original_files_to_add = original_dict_files_to_add.keys()
		for new_file_folder in dict_files_remove.keys():
			for orig_file in list_original_files_to_add:
				if new_file_folder == orig_file or orig_file.startswith(new_file_folder):
					dict_files_remove.pop(file, None)
					break

	def filter_assets_add_new_dict_members(self, original_dict_files_to_remove):
		self._filter_add_new_dict_members(original_dict_files_to_remove, self.dict_final_files_add)

	def filter_assets_remove_new_dict_members(self, original_dict_files_to_add):
		self._filter_remove_new_dict_members(original_dict_files_to_add, self.dict_final_files_remove)

	def check_can_remove_final_files(self, file_to_remove):
		return file_to_remove not in self.dict_final_files_add.keys()

	def check_can_add_final_files(self, file_to_add):
		for file_folder in self.dict_final_files_remove.keys():
			if file_to_add == file_folder or file_to_add.startswith(file_folder):
				return True

		return False

	def check_can_remove_jinja_files(self, list_files_remove):
		pass

	def check_can_add_jinja_files(self, list_files_add):
		pass

	def check_can_add_packages(self, list_files_add):
		pass

	def get_packages_list(self):
		return self.dict_packages

	def get_packagejs_file(self):
		from jinja2 import Environment, PackageLoader

		addFiles = []
		env = Environment(loader=PackageLoader('fluorine', 'templates'), trim_blocks=True)
		template = env.get_template('package.template')
		for k,v in self.dict_final_files_add.iteritems():
			addFiles.append({"filenames": k, "architecture": v.get("architecture"), "options": v.get("options")})
		config = template.render(**{
			"describe": self._describe,
			"api": {"use": self.api_use, "imply": self.api_imply, "export": self.api_export, "addFiles": addFiles},
			"Npm": self._Npm,
			"Cordova": self._Cordova,
			"registerBuildPlugin": self.registerBuildPlugin
		})

		print "package.js %s" % config


def filter_api_list_files_members(api, original_list_apis):

	for app_api in original_list_apis:
		api.filter_add_new_dict_members(app_api.get_dict_final_files_remove())
		api.filter_remove_new_dict_members(app_api.get_dict_final_files_add())


def filter_api_list_assets_members(api, original_list_apis):

	for app_api in original_list_apis:
		api.filter_assets_add_new_dict_members(app_api.get_dict_final_files_remove())
		api.filter_assets_remove_new_dict_members(app_api.get_dict_final_Assets_add())