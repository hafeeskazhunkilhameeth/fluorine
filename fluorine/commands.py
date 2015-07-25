from __future__ import unicode_literals, absolute_import
__author__ = 'luissaguas'


import frappe
import click


@click.command('mongodb-conf')
@click.argument('site')
@click.argument('db-name')
@click.argument('username')
@click.argument('password')
@click.option('--host', default='localhost', help='MongoDB Host default to localhost')
@click.option('--port', default=27017, help='MongoDB Port default to 27017')
#@click.option('--db-name', default='fluorine', help='Database name')
#@click.option('--username', default='root', help='Root username for MongoDB')
#@click.option('--password', help='Username password for MongoDB')
def mongodb_conf(site, db_name, username, password, host=None, port=None):
	"""prepare Fluorine for mongodb.
		Make reset to mongodb collection fUsers and set the frappe current users.
	"""
	from fluorine.utils.mongodb.utils import set_frappe_users

	#host = re.sub(r"http://", "", host)
	if not frappe.db:
		frappe.init(site=site)
		frappe.connect()

	set_frappe_users(host, port, db_name)



commands = [
	mongodb_conf,
]
