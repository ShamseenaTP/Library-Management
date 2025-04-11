import frappe
from frappe import auth
from frappe import _

@frappe.whitelist(allow_guest=True)
def response(message, data, success, status_code):
	'''
		method to generates responses of an API
		args:
			message : response message string
			data : json object of the data
			success : True or False depending on the API response
			status_code : status of the request
	'''
	frappe.clear_messages()
	frappe.local.response["message"] = message
	frappe.local.response["data"] = data
	frappe.local.response["success"] = success
	frappe.local.response["http_status_code"] = status_code
	return


@frappe.whitelist(allow_guest=True)
def get_logged_user():
    return frappe.session.user

@frappe.whitelist(allow_guest=True)
def login(usr, pwd):
    try:
        login_manager = frappe.auth.LoginManager()
        login_manager.authenticate(usr, pwd)
        login_manager.post_login()
    except frappe.exceptions.AuthenticationError:
        frappe.clear_messages()
        frappe.local.response["message"] = {
            "success_key":0,
            "message":"Authentication Error!"
        }

        return

    api_generate = generate_keys(frappe.session.user)
    user = frappe.get_doc('User', frappe.session.user)

    frappe.response["message"] = {
        "success_key":1,
        "message":"Authentication success",
        "sid":frappe.session.sid,
        "api_key":user.api_key,
        "api_secret":api_generate,
        "username":user.username,
        "email":user.email
    }


def generate_keys(user):
    user_details = frappe.get_doc('User', user)
    api_secret = frappe.generate_hash(length=15)

    if not user_details.api_key:
        api_key = frappe.generate_hash(length=15)
        user_details.api_key = api_key
    
    user_details.api_secret = api_secret
    user_details.save()

    return api_secret



@frappe.whitelist()
def get_article():
    articles = frappe.get_all("Article", fields=["name"])
    full_data = []
    for article in articles:
        doc = frappe.get_doc("Article", article.name)
        full_data.append(doc.as_dict())

    return full_data



@frappe.whitelist()
def create_article(name,author=None,status="Issued",isbn=None,publisher=None,image=None,description=None,published=0):
    try:
        if frappe.db.exists("Article", name):
            return response(f"Article '{name}' already exists", None, False, 400)
        doc = frappe.get_doc({
            "doctype": "Article",
            "article_name": name,
            "author": author,
            "status": status,
            "isbn": isbn,
            "publisher": publisher,
            "image": image,
            "description": description,
            "published": published,
        })
        doc.insert()
        return response(f"Article {doc.name} created", doc, True, 200)
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Create Item Error")
        return response("Something went wrong", e, False, 400)



@frappe.whitelist()
def update_article_details(name,author=None,status="Issued",isbn=None,publisher=None,image=None,description=None,published=0):
    try:
        if not frappe.db.exists("Article", name):
            return response(f"Article '{name}' not found", None, False, 400)
        
        doc = frappe.get_doc("Article", name)

        if author is not None:
            doc.author = author
        if status is not None:
            doc.status = status
        if isbn is not None:
            doc.isbn = isbn
        if publisher is not None:
            doc.publisher = publisher
        if image is not None:
            doc.image = image
        if description is not None:
            doc.description = description
        if published is not None:
            doc.published = published
        
        doc.save()
        return response(f"Article '{doc.name}' updated", doc, True, 200)

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Update item error")
        return response("Something went wrong while updating",e,False,400)




@frappe.whitelist()
def delete_article(name):
    try:
        if not frappe.db.exists("Article", name):
            return response(f"Article '{name}' not found", None, False, 400)

        frappe.delete_doc("Article", name)
        return response(f"Article '{name}' deleted successfully", None, True, 200)

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Delete item error")
        return response(f"Something went wrong while deleting",e,False,400)




@frappe.whitelist()
def get_member():
    members = frappe.get_all("Library Member", fields=["name"])
    full_data = []
    for member in members:
        doc = frappe.get_doc("Library Member", member.name)
        full_data.append(doc.as_dict())

    return full_data



@frappe.whitelist()
def create_member(first_name,last_name=None,full_name=None,email_address=None,phone=None):
    try:
        if frappe.db.exists("Library Member", first_name):
            return response(f"Library Member '{first_name}' already exists", None, False, 400)
        doc = frappe.get_doc({
            "doctype": "Library Member",
            "first_name": first_name,
            "last_name": last_name,
            "full_name": full_name,
            "email_address": email_address,
            "phone": phone,
        })
        doc.insert()
        return response(f"Library Member '{doc.full_name}' created", doc, True, 200)
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Create item error")
        return response("Something went wrong",e,False,400)