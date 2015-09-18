# -*- coding: utf-8 -*-
# Copyright (c) 2015, Luis Fernandes and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class FluorineSiteNames(Document):

	def validate(self, method=None):
		from fluorine.utils import is_valid_site

		if not is_valid_site(self.fluorine_site_name):
			return frappe.throw("The site %s is not a valid site. Please create the site first." % self.fluorine_site_name)