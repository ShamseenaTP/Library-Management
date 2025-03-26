# Copyright (c) 2025, Shamseena and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns = [
        {"label": "Transaction ID", "fieldname": "name", "fieldtype": "Data", "width": 150},
        {"label": "Library Member", "fieldname": "library_member", "fieldtype": "Link", "options": "Library Member", "width": 200},
        {"label": "Article", "fieldname": "article", "fieldtype": "Link", "options": "Article", "width": 200},
        {"label": "Transaction Type", "fieldname": "type", "fieldtype": "Select", "width": 150},
        {"label": "Transaction Date", "fieldname": "date", "fieldtype": "Date", "width": 150},
        {"label": "Fine Amount", "fieldname": "fine_amount", "fieldtype": "Currency", "width": 150},
    ]

    conditions = []

    if filters.get("from_date") and filters.get("to_date"):
        conditions.append(["date", "between", [filters.get("from_date"), filters.get("to_date")]])
    elif filters.get("from_date"):
        conditions.append(["date", ">=", filters.get("from_date")])
    elif filters.get("to_date"):
        conditions.append(["date", "<=", filters.get("to_date")])

    if filters.get("library_member"):
        conditions.append(["library_member", "=", filters.get("library_member")])

    if filters.get("article"):
        conditions.append(["article", "=", filters.get("article")])

    if filters.get("type"):
        conditions.append(["type", "=", filters.get("type")])

    if filters.get("fine_amount"):
        conditions.append(["fine_amount", ">=", filters.get("fine_amount")])

    data = frappe.db.get_list(
        "Library Transaction",
        filters=conditions,
        fields=["name", "library_member", "article", "type", "date", "fine_amount"],
        order_by="date desc"
    )

    return columns, data
