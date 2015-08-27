__author__ = 'luissaguas'

import os, click


def linux_system_service(service, bench=".."):
	from bench_helpers import get_program, is_running_systemd

	if os.path.basename(get_program("utils", ['systemctl'], bench=bench) or '') == 'systemctl' and is_running_systemd(bench=bench):
		exec_cmd = "{prog} restart {service}".format(prog='systemctl', service=service)
	elif os.path.basename(get_program(['service'], bench=bench) or '') == 'service':
		exec_cmd = "{prog} {service} restart ".format(prog='service', service=service)
	else:
		raise Exception, 'No service manager found'

	return exec_cmd


def start_nginx_supervisor_services(debug=False):
	from bench_helpers import exec_cmd
	from fluorine.commands_helpers.bench_helpers import CommandFailedError, get_password
	import platform, frappe

	echo = None#get_password()

	if platform.system() == 'Darwin':
		try:
			click.echo("restarting nginx...")
			echo = exec_cmd("sudo -S nginx -s reload", service="nginx", with_password=True, echo=echo)
			click.echo("nginx restarted.")
		except CommandFailedError:
			click.echo("nginx not running. Starting nginx...")
			echo = exec_cmd("sudo -S nginx", service="nginx", with_password=True, echo=echo)
			click.echo("nginx started.")
			#os.popen("sudo -S %s"%("sudo -S nginx"), 'w').write(password)

	else:
		click.echo("restarting nginx...")
		cmd = "sudo -S " + linux_system_service('nginx')
		echo = exec_cmd(cmd, service="nginx", with_password=True, echo=echo)
		click.echo("nginx restarted.")

	if not debug:
		click.echo("restarting supervisor...")
		try:
			exec_cmd("sudo -S supervisorctl reload", service="supervisor", with_password=True, echo=echo)
			click.echo("supervisor restarted.")
		except CommandFailedError:
			frappe.throw("Supervisor not restart. Check if supervisor is running.")

def build_assets(bench_path=".."):
	from bench_helpers import run_frappe_cmd

	click.echo("Building assets...")
	run_frappe_cmd(bench_path, 'build')

def build(make_copy=False, verbose=False):
	"Minify + concatenate JS and CSS files, build translations"
	import frappe.build
	frappe.build.bundle(False, make_copy=make_copy, verbose=verbose)
