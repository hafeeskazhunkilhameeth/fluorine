__author__ = 'luissaguas'

import frappe, os, re

from fluorine.utils import file
from fluorine.utils import assets_public_path



"""
client file loader
for each module read files with extension js
special atention to files in client/compatibility
ignore files in tests, in public in private and server
files in lib first and inside lib alphabetic order
other folders deepest first
files with main.* (start with main) are load last
"""


def copy_file(src, dst):
	import shutil
	shutil.copyfile(src, dst)

def remove_directory(path):
	import shutil
	shutil.rmtree(path)


def get_js_to_client(fluorine_publicjs_dst_path, whatfor):
	#fluorine_temp_path = os.path.join(frappe.get_app_path("fluorine"), "templates", "react", "temp")
	#frappe.create_folder(fluorine_temp_path)
	#fluorine_publicjs_path = os.path.join(frappe.get_app_path("fluorine"), "public", "js", "react")
	#copy_client_files(fluorine_temp_path, whatfor, extension="js")
	copy_client_files(fluorine_publicjs_dst_path, whatfor, extension="js")
	#files_in_lib, files_to_read, main_files, main_lib_files, compatibility_files = read_client_files(fluorine_temp_path, whatfor)
	#files = read_client_files(fluorine_temp_path, whatfor, extension="js")
	files = read_client_files(fluorine_publicjs_dst_path, whatfor, extension="js")
	#hooks_js = move_to_public(files_in_lib, files_to_read, main_files, main_lib_files, compatibility_files, whatfor)
	print "files 2 {}".format(files)
	hooks_js = move_to_public(files, whatfor)

	#remove_directory(fluorine_temp_path)

	return hooks_js

#def move_to_public(files_in_lib, files_to_read, main_files, main_lib_files, compatibility_files, whatfor):
def move_to_public(files, whatfor):
	#{"name":file, "path": path}
	import fluorine
	hooks_js = {"client_hooks_js":[]}
	fpath = assets_public_path

	fluorine_publicjs_path = os.path.join(frappe.get_app_path("fluorine"), "public", "js", "react")
	#empty folder
	#file.remove_folder_content(fluorine_publicjs_path)

	for f in files:
		hooks_js["client_hooks_js"].extend(prepare_files_and_copy(f, fpath))

	"""
	for f in reversed(compatibility_files):
		dest = os.path.join(fluorine_publicjs_path, f.get("name"))
		#copy_file(f.get("path"), dest)
		copy_with_wrapper(f.get("path"), dest)
		hooks_js["client_hooks_js"].append(os.path.join(fpath, f.get("name")))

	for f in reversed(files_in_lib):
		dest = os.path.join(fluorine_publicjs_path, f.get("name"))
		#copy_file(f.get("path"), dest)
		copy_with_wrapper(f.get("path"), dest)
		hooks_js["client_hooks_js"].append(os.path.join(fpath, f.get("name")))
		#make_app_hook(where, f.get("name"), fpath)

	for f in reversed(files_to_read):
		dest = os.path.join(fluorine_publicjs_path, f.get("name"))
		#copy_file(f.get("path"), dest)
		copy_with_wrapper(f.get("path"), dest, use_wrapper=not f.get("compatibility", False))
		hooks_js["client_hooks_js"].append(os.path.join(fpath, f.get("name")))
		#make_app_hook(where, f.get("name"), fpath)

	#check if contain lib directory
	for f in reversed(main_lib_files):
		dest = os.path.join(fluorine_publicjs_path, f.get("name"))
		#copy_file(f.get("path"), dest)
		copy_with_wrapper(f.get("path"), dest)
		hooks_js["client_hooks_js"].append(os.path.join(fpath, f.get("name")))
	"""
	"""lib = [l for l in reversed(main_files) if re.search(r"\blib\b", l)]
	for l in lib:
		dest = os.path.join(fluorine_publicjs_path, l.get("name"))
		#copy_file(f.get("path"), dest)
		copy_with_wrapper(l.get("path"), dest)
		hooks_js["client_hooks_js"].append(os.path.join(fpath, l.get("name")))
		main_files.remove(l)
	"""
	"""
	for f in reversed(main_files):
		dest = os.path.join(fluorine_publicjs_path, f.get("name"))
		#copy_file(f.get("path"), dest)
		copy_with_wrapper(f.get("path"), dest)
		hooks_js["client_hooks_js"].append(os.path.join(fpath, f.get("name")))
		#make_app_hook(where, f.get("name"), fpath)
	"""

	return hooks_js


def prepare_files_and_copy(files, fpath):
	hooks = []
	for f in reversed(files):
		hooks.append(os.path.join(fpath, f.get("relpath"), f.get("name")))

	return hooks


def copy_with_wrapper(src, dst, use_wrapper=True):
	content = file.read(src)
	if use_wrapper:
		content = wrapper(content)
	file.write(dst, content)
	return content

def wrapper(content):
	w = """
	(function(){ %s })()
	"""

	return w % content


def copy_client_files(fluorine_temp_path, whatfor, extension="js", with_wrapper=True, exclude_top=None, exclude_any=None):
	apps = frappe.get_installed_apps()[::-1]

	_whatfor = ["meteor_app", "meteor_web", "meteor_frappe"]
	exclude_top = exclude_top or ["public", "private", "tests","server","temp"]
	exclude_any = exclude_any or ["tests","server","temp"]
	folders_path = []

	exclude = [""]

	if isinstance(extension, basestring):
		extension = [extension]

	if isinstance(whatfor, basestring):
		whatfor = [whatfor]

	is_for_meteor_frappe = "meteor_frappe" in whatfor
	if is_for_meteor_frappe:
		exclude_top.extend(["meteor_app", "meteor_web"])

	try:
		for w in whatfor:
			_whatfor.remove(w)
		exclude = _whatfor
	except:
		pass

	exclude_top.extend(exclude)
	exclude_any.extend(exclude)

	frappe.local.fenv = None
	frappe.local.floader = None
	context = frappe._dict()

	for app in apps:
		pathname = frappe.get_app_path(app)
		startpath = os.path.join(pathname, "templates", "react")
		print "remove exclude in copy_client_files app 2 {} startpath {} exist? {}".format(app, startpath, os.path.exists(startpath))
		if os.path.exists(startpath):
			topfolder = True
			folders_path.append(app)
			for root, dirs, files in os.walk(startpath):
				relpath = os.path.relpath(root, startpath)
				print "dirs in copy client files 2 {}".format(dirs)
				try:
					if topfolder:
						[dirs.remove(toexclude) for toexclude in exclude_top if toexclude in dirs]
						topfolder = False
					else:
						[dirs.remove(toexclude) for toexclude in exclude_any if toexclude in dirs]
					print "remove exclude in copy_client_files {} dirs {}".format(exclude_top, dirs)

				except:
					print "remove exclude 3 {} no exclude in dirs ".format(exclude_top)
					pass

				if is_for_meteor_frappe:
					if not re.search(r"\bmeteor_frappe\b", root):
						continue

				app_folders = "/".join(folders_path)
				destpath = os.path.join(fluorine_temp_path, app_folders, relpath)
				print "destpath 27 {} relpath {} root {} app {} app_folders {}".format(destpath, relpath, root, app, app_folders)
				for f in files:
					ext = f.rsplit(".", 1)
					#if file.endswith("." + extension):
					if ext > 1 and ext[1] in extension:
						frappe.create_folder(destpath)
						print "in copy client files folder 2 {} created".format(destpath)
						srcPath = os.path.join(root, f)
						dstPath = os.path.join(destpath, f)
						if ext[1] == "html":
							from spacebars_template import get_spacebars_context
							out = get_spacebars_context(context, srcPath, f, pathname, app)
							for k in out.keys():
								file.save_file(dstPath, out[k])
						elif with_wrapper:
							copy_with_wrapper(srcPath, dstPath)
						else:
							copy_file(srcPath, dstPath)



def copy_client_files2(fluorine_temp_path, extension="js"):
	apps = frappe.get_installed_apps()#[::-1]
	for app in apps:
		pathname = frappe.get_app_path(app)
		startpath = os.path.join(pathname, "templates", "react")
		if pathname:
			for root, dirs, files in os.walk(startpath):
				relpath = os.path.relpath(root, startpath)
				#if not root.endswith("public") and not root.endswith("server") and not root.endswith("tests") and not root.endswith("private") and not root.endswith("temp"):
				#if not relpath.startswith(("public", "tests", "private", "temp", "server")):
				m = re.search(r"\b(public|tests|server|temp|private)\b",relpath)
				if not m:
					destpath = os.path.join(fluorine_temp_path, relpath)
					print "destpath {} relpath {} root {}".format(destpath, relpath, root)
					frappe.create_folder(destpath)
					for file in files:
						if file.endswith("." + extension):
							copy_file(os.path.join(root, file), os.path.join(destpath, app + "_" + file))


def read_client_files(temp_folder, whatfor, extension="js"):
	files_to_read = []
	files_in_lib = []
	main_files = []
	main_lib_files = []
	compatibility_files = []
	_whatfor = ["meteor_app", "meteor_web", "meteor_frappe"]
	exclude = [""]

	ignored_names_top = ["public","tests","server","temp","private"]
	ignored_names_any = ["tests","server","temp"]

	if isinstance(extension, basestring):
		extension = [extension]

	if isinstance(whatfor, basestring):
		whatfor = [whatfor]

	is_for_meteor_frappe = "meteor_frappe" in whatfor
	if is_for_meteor_frappe:
		ignored_names_top.extend(["meteor_app", "meteor_web"])

	try:
		for w in whatfor:
			_whatfor.remove(w)
		exclude = _whatfor
	except:
		pass

	ignored_names_top.extend(exclude)
	ignored_names_any.extend(exclude)

	topfolder = True

	for root, dirs, files in os.walk(temp_folder):
		print "pathname: 3 {}".format(dirs)
		#if root.endswith(exclude):
		#	continue
		#only works for topdown=True
		#dirs[:] = [d for d in dirs if d not in exclude]
		try:
			if topfolder:
				[dirs.remove(toexclude) for toexclude in ignored_names_top if toexclude in dirs]
				topfolder = False
			else:
				[dirs.remove(toexclude) for toexclude in ignored_names_any if toexclude in dirs]

			print "remove exclude 3 {} dirs {}".format(ignored_names_top, dirs)
		except:
			print "remove exclude 3 {} no exclude in dirs ".format(ignored_names_top)
			pass

		#only read files within meteor_frappe folder
		if is_for_meteor_frappe:
			if not re.search(r"\bmeteor_frappe\b", root):
				continue

		islib = False
		iscompatibility = False

		if re.search(r"\blib\b", root):
			islib = True
		if re.search(r"\bclient/compatibility\b", root):
			iscompatibility = True

		deeper = len(root.split("/"))

		#for file in sorted(files, reverse=True):
		for file in files:
			print "files in read {}".format(files)
			ext = file.rsplit(".", 1)
			#if file.endswith("." + extension):
			if ext > 1 and ext[1] in extension:
				#path = os.path.join(os.path.relpath(root, pathname), file)
				path = os.path.join(root, file)
				print "path read_client_files {}".format(path)
				relpath = os.path.relpath(root, temp_folder)
				obj = {"name":file, "path": path, "relpath": relpath, "filePath": root, "fileName": ext[0], "deep": deeper}
				#if root.endswith("lib"):
				if iscompatibility:
					obj["compatibility"] = True
					compatibility_files.append(obj)
				elif re.search(r"main.*", file):
					if islib:
						main_lib_files.append(obj)
						continue
					main_files.append(obj)
				elif islib:
					files_in_lib.append(obj)
				else:
					files_to_read.append(obj)

	return (compatibility_files, files_in_lib, files_to_read, main_lib_files, main_files)


"""
def read_client_files2(temp_folder, whatfor):
	files_to_read = []
	files_in_lib = []
	main_files = []
	_whatfor = ["meteor_app", "meteor_web", "meteor_frappe"]
	exclude = ""
	try:
		_whatfor.remove(whatfor)
		exclude = _whatfor
	except:
		pass

	for root, dirs, files in os.walk(temp_folder):
		print "pathname: 3 {}".format(dirs)
		#if root.endswith(exclude):
		#	continue
		#only works for topdown=True
		#dirs[:] = [d for d in dirs if d not in exclude]
		try:
			[dirs.remove(toexclude) for toexclude in exclude]
			dirs.sort(reverse=True)
			print "remove exclude 3 {} dirs {}".format(exclude, dirs)
		except:
			print "remove exclude 3 {} no exclude in dirs ".format(exclude)
			pass

		for file in sorted(files, reverse=True):
		#for file in files:
			if file.endswith(".js"):
				#path = os.path.join(os.path.relpath(root, pathname), file)
				path = os.path.join(root, file)
				print "path read_client_files {}".format(path)
				obj = {"name":file, "path": path}
				#if root.endswith("lib"):
				if re.search(r"\blib\b", root):
					files_in_lib.append(obj)
				#elif root.endswith("client/compatibility"):
				elif re.search(r"\bclient/compatibility\b", root):
					obj["compatibility"] = True
					files_to_read.append(obj)
				elif re.search(r"main.*", file):
					main_files.append(obj)
				else:
					files_to_read.append(obj)

	return files_in_lib, files_to_read, main_files
"""