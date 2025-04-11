import frappe
from frappe.model.document import Document

class Article(Document):
    def validate(self):
        max_rows = 5
		