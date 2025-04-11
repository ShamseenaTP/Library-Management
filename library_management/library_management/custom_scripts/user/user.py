import frappe
from frappe.model.document import Document

class User(Document):
    pass  # No need to define create_fullname inside the class

# Hook function defined at the module level
def create_fullname(doc, method):
    doc.full_name = f'{doc.first_name} {doc.middle_name or ""}'.strip()
