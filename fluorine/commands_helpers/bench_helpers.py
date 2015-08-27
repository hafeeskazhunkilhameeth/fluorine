__author__ = 'luissaguas'

import os


class CommandFailedError(Exception):
	pass

class PasswordError(Exception):
	pass

def run_bench_module(module, func, *args, **kwargs):
	cwd = os.getcwd()
	os.chdir("../")
	f = getattr(module, func)
	res = f(*args, **kwargs)
	os.chdir(cwd)

	return res


def get_bench_module(module, depends=None, bench=".."):
	import sys, importlib

	depends = depends or []
	bench_path = os.path.abspath(bench)
	if bench_path not in sys.path:
		sys.path.append(bench_path)

	#print "cwd {} bench {} abs_bench {} bench_path in sys.path {}".format(os.getcwd(), bench, bench_path, bench_path in sys.path)
	for d in depends:
		importlib.import_module("bench." + d)

	m = importlib.import_module("bench." + module)

	return m


def run_frappe_cmd(bench_path, *args, **kwargs):
	#bench = kwargs.get('bench', '..')
	m = get_bench_module("utils", bench=bench_path)
	run_bench_module(m, "run_frappe_cmd", *args, **kwargs)
	return


def get_password():
	import subprocess, getpass

	stdout=subprocess.PIPE
	password = getpass.getpass("Please enter root password.\n")
	echo = subprocess.Popen(['echo', password], stdout=stdout,)

	return echo

def exec_cmd(cmd, service="service", cwd=".", with_password=False, echo=None):
	import subprocess, click

	stderr=stdout=subprocess.PIPE
	#echo = None

	return_code = 1
	password_error = 0
	password_error_txt = "Password:Sorry, try again."

	for i in range(3):
		if with_password and not echo:
			echo = get_password()

		p = subprocess.Popen(cmd, cwd=cwd, shell=True, stdin=echo.stdout if echo else None, stdout=stdout, stderr=stderr)

		#return_code = p.wait()
		#out, err = p.communicate()
		p.wait()
		return_code = p.returncode
		error = p.stderr.read()
		#out = p.stdout.read()
		#print "return code out {} err {} retcode {} i {}".format(out, error, return_code, i)
		if not with_password:
			break
		elif return_code == 0:
			return echo
		elif password_error_txt in error: #or not with_password or return_code == 0:
			password_error = 1
			click.echo(error.replace("1",str(i + 1)))
			echo = None
		else:
			password_error = 0
			break
		#return_code = 0
	if return_code > 0:
		if password_error:
			raise PasswordError("Password error.")
		else:
			raise CommandFailedError("starting %s..." % service)

def is_running_systemd(bench=".."):
	m = get_bench_module("production_setup", bench=bench)
	res = run_bench_module(m, "is_running_systemd")
	return res

def get_program(p, bench=".."):
	m = get_bench_module("utils", bench=bench)
	res = run_bench_module(m, "get_program", p)
	return res

def fix_prod_setup_perms(frappe_user=None, bench="."):
	m = get_bench_module("utils", bench=bench)
	run_bench_module(m, "fix_prod_setup_perms", frappe_user=frappe_user)

def bench_generate_supervisor_config(bench="..", user=None):
	m = get_bench_module("config", bench=bench)
	run_bench_module(m, "generate_supervisor_config", user=user)

def bench_generate_nginx_config(bench=".."):
	m = get_bench_module("config", bench=bench)
	run_bench_module(m, "generate_nginx_config")

def bench_setup_production(user=None, bench=".."):
	import getpass

	if not user:
		user = getpass.getuser()

	cwd = os.getcwd()
	os.chdir("../")
	exec_cmd("sudo -S bench setup production %s" % user, with_password=True)
	os.chdir(cwd)

def get_supervisor_confdir(bench="."):
	m = get_bench_module("production_setup", bench=bench)
	res = run_bench_module(m, "get_supervisor_confdir")
	return res


def get_supervisor_conf_filename(bench="."):
	m = get_bench_module("production_setup", bench=bench)
	res = run_bench_module(m, "is_centos7")
	if res:
		return 'frappe.ini'
		#copy_default_nginx_config()
	else:
		return 'frappe.conf'


def get_current_version(app, bench='.'):
	import semantic_version

	#get_bench_module("utils", bench=bench)
	m = get_bench_module("app", depends=["utils"], bench=bench)
	version = run_bench_module(m, "get_current_version", app)

	return semantic_version.Version(version)