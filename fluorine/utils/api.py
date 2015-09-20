__author__ = 'luissaguas'


import frappe, os


class Api(object):

	def __init__(self, app, whatfor, devmode=True):
		self.developer_mode = devmode
		self.list_jinja_files = []
		self.list_final_files_add = []
		self.list_final_files_remove = []
		self.list_packages = []
		self.app = app
		self.whatfor = whatfor
		self.startpath = "templates/react"


	def getApp(self):
		return self.app

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
			self.list_final_files_add.append({"source_final_path": final_path, "relative_path": os.path.join(new_prefix, file), "app": app})

	def addJinjaFiles(self, files, app=None, prefix=None, out_ext="html", export=True):
		app, files = self.get_processed_input_data(app, files)
		for file in files:
			file, new_prefix = self.change_file_path_if_not_relative(file)
			final_path = self.get_final_path(app, new_prefix, file)
			self.list_jinja_files.append({"final_path": final_path, "relative_path": os.path.join(new_prefix, file), "ext_out": out_ext, "export": export, "prefix": new_prefix})

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
			self.list_final_files_remove.append(final_path)


	def is_developer_mode(self):
		return self.developer_mode

	def get_processed_input_data(self, app, files):
		if not app or app.strip() == "":
			app = self.app

		if isinstance(files, basestring):
			files = [files]

		return app, files

	def remove_final_file_from_add_list(self, final_file):
		for obj in self.list_final_files_add[:]:
			if final_file == obj.get("source_final_path"):
				self.list_final_files_add.remove(obj)
				break

	def remove_final_file_from_remove_list(self, final_file):
		for obj in self.list_final_files_add[:]:
			if final_file == obj.get("source_final_path"):
				self.list_final_files_add.remove(obj)
				break

	def get_final_path(self, app, relative_path_prefix, file):
		app_path = frappe.get_app_path(app)
		file_path = os.path.join(app_path, relative_path_prefix, file)
		return file_path

	def get_list_jinja_files(self):
		return self.list_jinja_files

	def get_list_final_files_add(self):
		return self.list_final_files_add

	def get_list_final_files_remove(self):
		return self.list_final_files_remove

	def get_list_packages(self):
		return self.list_packages

	def validate_add_list_members(self, original_list_files_to_remove):
		for original_check_file_obj in original_list_files_to_remove:
			original_check_file_path = original_check_file_obj.get("source_final_path")
			for check_file_obj in self.list_final_files_add[:]:
				check_file_path = check_file_obj.get("source_final_path")
				if original_check_file_path == check_file_path:
					self.list_final_files_add.remove(check_file_obj)
					break

	def validate_remove_list_members(self, original_list_files_to_add):
		for original_check_file_obj in original_list_files_to_add:
			original_check_file_path = original_check_file_obj.get("source_final_path")
			for check_file_obj in self.list_final_files_remove[:]:
				check_file_path = check_file_obj.get("source_final_path")
				if original_check_file_path == check_file_path:
					self.list_final_files_remove.remove(check_file_obj)
					break

	def check_can_remove_final_files(self, file_to_remove_path):
		for obj in self.list_final_files_add:
			check_file_path = obj.get("source_final_path")
			if check_file_path == file_to_remove_path:
				return False
		return True

	def check_can_add_final_files(self, file_to_add_path):
		for obj in self.list_final_files_remove:
			check_file_path = obj.get("source_final_path")
			if check_file_path == file_to_add_path:
				return False
		return True

	def check_can_remove_jinja_files(self, list_files_remove):
		pass

	def check_can_add_jinja_files(self, list_files_add):
		pass

	def check_can_add_packages(self, list_files_add):
		pass


def validate_update_api_list_members(api, original_list_apis):

	for app_api in original_list_apis:
		api.validate_add_list_members(app_api.get_list_final_files_remove())
		api.validate_remove_list_members(app_api.get_list_final_files_add())