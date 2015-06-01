__author__ = 'luissaguas'



#from fluorine.utils.packages_path import get_package_path
from jinja2 import FileSystemLoader, TemplateNotFound
import re, os, frappe


def delimeter_match(m):
	#print m.group(0)
	if m.group(0).startswith("{{%"):
		#print m.group(2)
		source = "{% endraw %}\n{{"+ m.group(2) +"}}{% raw %}\n"
	elif m.group(1) and m.group(1).startswith("end"):
		source = m.group(0) + "\n" + "{% raw %}\n"
	else:
		source = "\n" + "{% endraw %}\n" + m.group(0)

	return source

def jinjarepl(m):
	#print "my group 2 {}".format(m.group(2))
	source = re.sub(r"{%-?\s+(.*?)\s+-?%}|{{%(-?\s+.*?\s+-?)}}", delimeter_match, m.group(3))
	#print source
	source = '\n{% block '+ "{}".format(m.group(1)) + ' %}\n{% raw %}\n' + "<template name='{0}'{1}>".format(m.group(1), m.group(2)) + source + '\n{% endraw %}\n</template>\n{% endblock %}\n'
	#print "source in jinjareple {}".format(source)
	return source


class MyFileSystemLoader(FileSystemLoader):
	def __init__(self, apps, searchpath, encoding='utf-8'):
		super(MyFileSystemLoader, self).__init__(searchpath, encoding='utf-8')
		self.apps = apps

	def get_source(self, environment, template):
		print "new get_source templates {}".format(template)
		found = False
		contents = filename = uptodate = None

		for app in self.apps:
			#temp = template.split("/")
			#temp.insert(0, app + "/" + app)
			#temp = "/".join(temp)
			app_path = frappe.get_app_path(app)#get_package_path(app, "", "")
			filepath = os.path.join(app_path, template)
			relpath = os.path.relpath(filepath, os.path.normpath(os.path.join(os.path.join(os.getcwd(), ".."), "apps")))
			#print "filepath {} {}".format(relpath, temp)#os.path.relpath("apps", app_path)
			try:
				contents, filename, uptodate = super(MyFileSystemLoader, self).get_source(environment, relpath)
				contents = re.sub("<template name=['\"](.+?)['\"](.*?)>(.*?)</template>", jinjarepl, contents, flags=re.S)
				#print "new Contents get_source {}".format(contents)
				found = True
				break
			except TemplateNotFound, e:
				#print "Not Found {}".format(e)
				continue

		if not found:
			raise TemplateNotFound(template)
		else:
			return contents, filename, uptodate