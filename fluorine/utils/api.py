__author__ = 'luissaguas'


import frappe, os


class Api(object):

	def __init__(self, app, whatfor, devmode=True):
		self.developer_mode = devmode
		#self.list_jinja_files = []
		self.dict_jinja_files = frappe._dict()
		#self.list_final_files_add = []
		self.dict_final_files_add = frappe._dict()
		#self.list_final_files_remove = []
		self.dict_final_files_remove = {}
		self.list_packages = []
		#self.list_packages = {}
		self.app = app
		self.whatfor = whatfor
		self.startpath = "templates/react"
		self.template_path = None
		self.template_name = None


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

		if file_to_add.startswith("../"):
			new_prefix = os.path.normpath(os.path.join(self.startpath, "../"))
			file_to_add = file_to_add.replace("../", "", 1)
		elif file_to_add.startswith("/"):
			new_prefix = ""
			file_to_add = file_to_add.replace("/", "", 1)
		else:
			new_prefix = self.startpath

		return file_to_add, new_prefix

	def addFiles(self, files, app=None, prefix=None):
		app, files = self.get_processed_input_data(app, files)
		for file in files:
			file, new_prefix = self.change_file_path_if_not_relative(file)
			final_path = self.get_final_path(app, new_prefix, file)
			#self.list_final_files_add.append({"source_final_path": final_path, "relative_path": os.path.join(new_prefix, file), "app": app})
			self.dict_final_files_add[final_path] = {"relative_path": os.path.join(new_prefix, file), "app": app}

	def addJinjaFiles(self, files, app=None, prefix=None, out_ext="html", export=True):
		app, files = self.get_processed_input_data(app, files)
		for file in files:
			file, new_prefix = self.change_file_path_if_not_relative(file)
			final_path = self.get_final_path(app, new_prefix, file)
			self.dict_jinja_files[final_path] = {"relative_path": os.path.join(new_prefix, file), "ext_out": out_ext, "export": export, "prefix": new_prefix}

	def addPackages(self, files, prefix=None):
		app, files = self.get_processed_input_data(self.app, files)
		for file in files:
			file, new_prefix = self.change_file_path_if_not_relative(file)
			final_path = self.get_final_path(app, new_prefix, file)
			self.list_packages.append(final_path)

	def removeFiles(self, files, app=None, prefix=None):
		app, files = self.get_processed_input_data(app, files)
		for file in files:
			file, new_prefix = self.change_file_path_if_not_relative(file)
			final_path = self.get_final_path(app, new_prefix, file)
			#self.list_final_files_remove.append(final_path)
			self.dict_final_files_add[final_path] = {"relative_path": os.path.join(new_prefix, file), "app": app}


	def is_developer_mode(self):
		return self.developer_mode

	def get_processed_input_data(self, app, files):
		if not app or app.strip() == "":
			app = self.app

		if isinstance(files, basestring):
			files = [files]

		return app, files

	"""
	def remove_final_file_from_add_list(self, final_file):
		for obj in self.list_final_files_add[:]:
			if final_file == obj.get("source_final_path"):
				self.list_final_files_add.remove(obj)
				break
	"""
	def remove_final_file_from_add_list(self, final_file):
		self.dict_final_files_add.pop(final_file, None)

	def remove_final_file_from_remove_list(self, final_file):
		self.dict_final_files_remove.pop(final_file, None)

	"""
	def remove_final_file_from_remove_list(self, final_file):
		for obj in self.list_final_files_add[:]:
			if final_file == obj.get("source_final_path"):
				self.list_final_files_add.remove(obj)
				break
	"""

	def get_final_path(self, app, relative_path_prefix, file):
		app_path = frappe.get_app_path(app)
		file_path = os.path.join(app_path, relative_path_prefix, file)
		return file_path

	def get_dict_jinja_files(self):
		return self.dict_jinja_files

	def get_dict_final_files_add(self):
		return self.dict_final_files_add

	def get_dict_final_files_remove(self):
		return self.dict_final_files_remove

	def get_list_packages(self):
		return self.list_packages

	def filter_add_new_dict_members(self, original_dict_files_to_remove):
		list_original_files_to_remove = original_dict_files_to_remove.keys()
		for new_file in self.dict_final_files_add.keys():
			if new_file in list_original_files_to_remove:
				self.dict_final_files_add.pop(new_file, None)

	"""
	def validate_add_list_members(self, original_list_files_to_remove):
		for original_check_file_obj in original_list_files_to_remove:
			original_check_file_path = original_check_file_obj.get("source_final_path")
			for check_file_obj in self.list_final_files_add[:]:
				check_file_path = check_file_obj.get("source_final_path")
				if original_check_file_path == check_file_path:
					self.list_final_files_add.remove(check_file_obj)
					break
	"""

	def filter_remove_new_dict_members(self, original_dict_files_to_add):
		list_original_files_to_add = original_dict_files_to_add.keys()
		for new_file_folder in self.dict_final_files_remove.keys():
			for orig_file in list_original_files_to_add:
				if new_file_folder == orig_file or orig_file.startswith(new_file_folder):
					self.dict_final_files_remove.pop(file, None)
					break

	"""
	def validate_remove_list_members(self, original_list_files_to_add):
		for original_check_file_obj in original_list_files_to_add:
			original_check_file_path = original_check_file_obj.get("source_final_path")
			for check_file_obj in self.dict_final_files_remove[:]:
				check_file_path = check_file_obj.get("source_final_path")
				if original_check_file_path == check_file_path:
					self.dict_final_files_remove.remove(check_file_obj)
					break
	"""

	def check_can_remove_final_files(self, file_to_remove):
		return file_to_remove not in self.dict_final_files_add.keys()

	def check_can_add_final_files(self, file_to_add):
		for file_folder in self.dict_final_files_remove.keys():
			if file_to_add == file_folder or file_to_add.startswith(file_folder):
				return True

		return False

	"""
	def check_can_remove_final_files(self, file_to_remove_path):
		for obj in self.dict_final_files_add:
			check_file_path = obj.get("source_final_path")
			if check_file_path == file_to_remove_path:
				return False
		return True

	def check_can_add_final_files(self, file_to_add_path):
		for obj in self.dict_final_files_remove:
			check_file_path = obj.get("source_final_path")
			if check_file_path == file_to_add_path:
				return False
		return True
	"""

	def check_can_remove_jinja_files(self, list_files_remove):
		pass

	def check_can_add_jinja_files(self, list_files_add):
		pass

	def check_can_add_packages(self, list_files_add):
		pass


def filter_api_list_members(api, original_list_apis):

	for app_api in original_list_apis:
		api.filter_add_new_dict_members(app_api.get_dict_final_files_remove())
		api.filter_remove_new_dict_members(app_api.get_dict_final_files_add())