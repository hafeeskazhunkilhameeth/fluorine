__author__ = 'luissaguas'

import os, click


def linux_system_service(service, bench=".."):
	from bench_helpers import get_program, is_running_systemd

	if os.path.basename(get_program(['systemctl'], bench=bench) or '') == 'systemctl' and is_running_systemd(bench=bench):
		exec_cmd = "{service_manager} restart {service}".format(service_manager='systemctl', service=service)
	elif os.path.basename(get_program(['service'], bench=bench) or '') == 'service':
		exec_cmd = "{service_manager} {service} restart ".format(service_manager='service', service=service)
	else:
		# look for 'service_manager' and 'service_manager_command' in environment
		service_manager = os.environ.get("BENCH_SERVICE_MANAGER")
		if service_manager:
			service_manager_command = (os.environ.get("BENCH_SERVICE_MANAGER_COMMAND")
				or "{service_manager} restart {service}").format(service_manager=service_manager, service=service)
			exec_cmd = service_manager_command
		else:
			raise Exception, 'No service manager found'

	return exec_cmd


def start_nginx_supervisor_services(debug=False):
	from bench_helpers import exec_cmd
	from fluorine.commands_helpers.bench_helpers import CommandFailedError
	from distutils.spawn import find_executable
	import platform, frappe

	echo = None

	if platform.system() == 'Darwin':
		nginx = find_executable("nginx")
		try:
			click.echo("restarting nginx...")
			echo = exec_cmd("sudo -S %s -s reload" % nginx, service="nginx", with_password=True, echo=echo)
			click.echo("nginx restarted.")
		except CommandFailedError:
			click.echo("nginx not running. Starting nginx...")
			echo = exec_cmd("sudo -S %s" % nginx, service="nginx", with_password=True, echo=echo)
			click.echo("nginx started.")

	elif not os.environ.get('NO_SERVICE_RESTART'):
		click.echo("restarting nginx...")
		cmd = "sudo -S " + linux_system_service('nginx')
		echo = exec_cmd(cmd, service="nginx", with_password=True, echo=echo)
		click.echo("nginx restarted.")
	else:
		click.echo("No service to restart!")

	if not debug:
		supervisorctl = find_executable("supervisorctl")
		click.echo("restarting supervisor...")
		try:
			exec_cmd("sudo -S %s reload" % supervisorctl, service="supervisor", with_password=True, echo=echo)
			click.echo("supervisor restarted.")
		except CommandFailedError:
			frappe.throw("Supervisor not restart. Check if supervisor is running then to restart production again use the option --force.")

def build_assets(bench_path=".."):
	from bench_helpers import run_frappe_cmd

	click.echo("Building assets...")
	run_frappe_cmd(bench_path, 'build')

def build(make_copy=False, verbose=False):
	"Minify + concatenate JS and CSS files, build translations"
	import frappe.build
	frappe.build.bundle(False, make_copy=make_copy, verbose=verbose)
