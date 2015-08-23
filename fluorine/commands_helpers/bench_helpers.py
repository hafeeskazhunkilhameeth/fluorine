__author__ = 'luissaguas'

import os


class CommandFailedError(Exception):
	pass


def run_bench_module(module, func, *args, **kwargs):
	cwd = os.getcwd()
	os.chdir("../")
	f = getattr(module, func)
	res = f(*args, **kwargs)
	os.chdir(cwd)

	return res


def get_bench_module(module, bench=".."):
	import sys, importlib

	bench_path = os.path.abspath(bench)
	if bench_path not in sys.path:
		sys.path.append(bench_path)

	#print "cwd {} bench {} abs_bench {} bench_path in sys.path {}".format(os.getcwd(), bench, bench_path, bench_path in sys.path)
	m = importlib.import_module("bench." + module)

	return m


def exec_cmd(cmd, cwd=".", with_password=False):
	import subprocess, getpass

	stdout=subprocess.PIPE
	echo = None

	if with_password:
		password = getpass.getpass("Please enter root password.\n")
		echo = subprocess.Popen(['echo', password], stdout=stdout,)

	p = subprocess.Popen(cmd, cwd=cwd, shell=True, stdin=echo.stdout if echo else None)

	return_code = p.wait()
	if return_code > 0:
		raise CommandFailedError("restarting nginx...")

def is_running_systemd(module, bench=".."):
	m = get_bench_module(module, bench=bench)
	res = run_bench_module(m, "is_running_systemd")
	return res

def get_program(module, p, bench=".."):
	m = get_bench_module(module, bench=bench)
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