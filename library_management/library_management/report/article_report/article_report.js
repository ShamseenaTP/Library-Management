// Copyright (c) 2025, Shamseena and contributors
// For license information, please see license.txt

frappe.query_reports["Article Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": "From Date",
			"fieldtype": "Date",
			"default": frappe.datetime.add_days(frappe.datetime.nowdate(), -30)
		},
		{
			"fieldname": "to_date",
			"label": "To Date",
			"fieldtype": "Date",
			"default": frappe.datetime.nowdate()
		},
		{
			"fieldname": "library_member",
			"label": "Library Member",
			"fieldtype": "Link",
			"options": "Library Member"
		},
		{
			"fieldname": "article",
			"label": "Article",
			"fieldtype": "Link",
			"options": "Article"
		},
		{
			"fieldname": "type",
			"label": "Transaction Type",
			"fieldtype": "Select",
			"options": ["", "Issue", "Return"]
		},
		{
			"fieldname": "fine_amount",
			"label": "Fine Amount",
			"fieldtype": "Currency"
		}
	]
};
