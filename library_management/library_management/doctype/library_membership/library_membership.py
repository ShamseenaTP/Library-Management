# Copyright (c) 2025, Shamseena and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.docstatus import DocStatus
from frappe.utils import today, getdate


class LibraryMembership(Document):

	def before_submit(self):
		exists = frappe.db.exists(
			"Library Membership",
			{
				"library_member": self.library_member,
				"docstatus": DocStatus.submitted(),
				"to_date": (">", self.from_date),
			},
		)
		if exists:
			frappe.throw("There is an active membership for this member")

		loan_period = frappe.db.get_single_value("Library Settings", "loan_period")
		self.to_date = frappe.utils.add_days(self.from_date, loan_period or 30)

		from_date = self.from_date

		if not from_date:
			frappe.throw("From Date is required.")

		from_date_obj = getdate(from_date)
		today_obj = getdate(today())

		if from_date_obj < today_obj :
			frappe.throw("The From Date must be grater than or equal to Today")
