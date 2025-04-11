
import frappe
from frappe.model.document import Document
from frappe.model.docstatus import DocStatus
from frappe.utils import date_diff, today

class LibraryTransaction(Document):

    def before_submit(self):
        if self.type == "Issue":
            self.validate_issue()
            self.validate_maximum_limit()
            article = frappe.get_doc("Article", self.article)
            article.status = "Issued"
            article.save()

        elif self.type == "Return":
            self.validate_return()
            self.mark_article_as_available()
            self.calculate_fine()


    def validate(self):
        if self.shelf_location:
            shelf = frappe.get_doc("Shelf", self.shelf_location)

            if not shelf.row_number:
                shelf.row_number = 1

            if not shelf.column_number:
                shelf.column_number = 1

            max_rows = 5
            max_column = 5

            if shelf.column_number < max_column:
                shelf.column_number = shelf.column_number + 1

            else:
                shelf.column_number = 1
                shelf.row_number = shelf.row_number + 1

                if shelf.row_number > max_rows:
                    frappe.throw("Shelf is full. No more space available")

            self.row_name = shelf.row_number
            self.column_name = shelf.column_number


            shelf.save()



    def on_submit(self):
        if self.type == "Issue":
            self.update_article_status("Issued")
            self.populate_borrowed_books()

        if self.type == "Return":
            self.update_article_status("Available")
            self.remove_from_borrowed_books()
            self.display_fine_amount()




    def calculate_fine(self):
        settings = frappe.get_single("Library Settings")
        fine_days = settings.fine_days
        fine_per_day = settings.amount

        issued_transaction = frappe.get_value(
            "Library Transaction",
            {
                "library_member": self.library_member,
                "article": self.article,
                "type": "Issue",
                "docstatus": 1
            },
            ["date"]
        )


        if issued_transaction:
            overdue_days = max(0, date_diff(self.date, issued_transaction) - fine_days)
            self.fine_amount = overdue_days * fine_per_day

            if self.fine_amount < 0:
                self.fine_amount = 0
        else:
            self.fine_amount = 0




    def remove_from_borrowed_books(self):
        member = frappe.get_doc("Library Member", self.library_member)

        member.borrowed_books = [
            book for book in member.borrowed_books if book.book != self.article
        ]

        member.flags.ignore_permissions = True
        member.flags.ignore_validate = True
        member.flags.update_after_submit = True
        member.save()



    def validate(self):
        member = frappe.get_doc("Library Member", self.library_member)
        total_fine = sum([fine.fine_amount for fine in member.fine_log])
        self.total_fine = total_fine
        member.save()


    def validate_issue(self):
        self.validate_membership()

        member = frappe.get_doc("Library Member", self.library_member)

        if any(book.book == self.article for book in member.borrowed_books):
            frappe.throw("This book is already issued to the member")

        article = frappe.get_doc("Article", self.article)

        if article.status == "Issued":
            frappe.throw("Article is already issued by another member")


    def validate_return(self):
        book_exists = frappe.db.exists(
            "Borrowed Books",
            {
                "parent": self.library_member,
                "book": self.article
            }
        )

        if not book_exists:
            frappe.throw("This book has already been returned or was never issued.")


    def mark_article_as_available(self):
        article = frappe.get_doc("Article", self.article)
        article.status = "Available"
        article.save()


    def validate_maximum_limit(self):
        max_articles = frappe.db.get_single_value("Library Settings", "max_articles")
        count = frappe.db.count(
            "Borrowed Books",
            {
                "book": self.article,
            },
        )
        if count >= max_articles:
            frappe.throw("Maximum limit reached for issuing articles")


    def validate_membership(self):
        valid_membership = frappe.db.exists(
            "Library Membership",
            {
                "library_member": self.library_member,
                "docstatus": DocStatus.submitted(),
                "from_date": ("<", self.date),
                "to_date": (">", self.date),
            },
        )
        if not valid_membership:
            frappe.throw("The member does not have a valid membership")


    def populate_borrowed_books(self):
        member = frappe.get_doc("Library Member", self.library_member)

        already_issued = any(book.book == self.article for book in member.borrowed_books)

        if already_issued:
            frappe.throw(f"The book '{self.article}' is already issued to this member.")
        else:
            child = member.append("borrowed_books", {})
            child.book = self.article
            child.borrow_date = self.date
            child.status = "Issued"

            member.save()



    def display_fine_amount(self):
        member = frappe.get_doc("Library Member", self.library_member)

        child = member.append("fine_log", {})
        child.article = self.article
        child.transaction_date = self.date
        child.fine_amount = self.fine_amount

        member.save()


    def update_article_status(self, status):
        article = frappe.get_doc("Article", self.article)
        article.status = status

        article.flags.ignore_permissions = True
        article.flags.ignore_validate = True
        article.flags.update_after_submit = True

        article.save()
