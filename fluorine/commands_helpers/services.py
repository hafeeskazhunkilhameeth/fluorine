__author__ = 'luissaguas'

import os, click


def linux_system_service(service, bench=".."):
	from bench_helpers import get_program, is_running_systemd

	if os.path.basename(get_program("utils", ['systemctl'], bench=bench) or '') == 'systemctl' and is_running_systemd("production_setup", bench=bench):
		exec_cmd = "{prog} restart {service}".format(prog='systemctl', service=service)
	elif os.path.basename(get_program("utils", ['service'], bench=bench) or '') == 'service':
		exec_cmd = "{prog} {service} restart ".format(prog='service', service=service)
	else:
		raise Exception, 'No service manager found'

	return exec_cmd


def start_nginx_supervisor_services(debug=False):
	from bench_helpers import exec_cmd
	from fluorine.commands_helpers.bench_helpers import CommandFailedError
	import platform

	if platform.system() == 'Darwin':
		try:
			click.echo("restarting nginx...")
			exec_cmd("sudo -S nginx -s reload", with_password=True)
			click.echo("nginx restarted.")
		except CommandFailedError:
			click.echo("nginx not running. Starting nginx...")
			exec_cmd("sudo -S nginx", with_password=True)
			click.echo("nginx started.")
			#os.popen("sudo -S %s"%("sudo -S nginx"), 'w').write(password)

	else:
		click.echo("restarting nginx...")
		cmd = "sudo -S " + linux_system_service('nginx')
		exec_cmd(cmd, with_password=True)
		click.echo("nginx restarted.")

	if not debug:
		click.echo("restarting supervisor...")
		exec_cmd("sudo -S supervisorctl reload", with_password=True)
		click.echo("supervisor restarted.")

def build_assets(bench_path=".."):
	from bench_helpers import run_frappe_cmd

	click.echo("Building assets...")
	run_frappe_cmd(bench_path, 'build')

def build(make_copy=False, verbose=False):
	"Minify + concatenate JS and CSS files, build translations"
	import frappe.build
	frappe.build.bundle(False, make_copy=make_copy, verbose=verbose)
