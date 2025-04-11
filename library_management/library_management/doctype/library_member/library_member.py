# Copyright (c) 2025, Shamseena and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import formatdate

class LibraryMember(Document):

    def before_save(self):
        self.full_name = f'{self.first_name} {self.last_name or ""}'
