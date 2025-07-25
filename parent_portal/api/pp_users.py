import frappe
from frappe import _
import json


@frappe.whitelist()
def get_list():
    """
    Fetches list of all users who have the role: PP User
    """

    # Check if the user is a PP User and has he "PP User" role
    # If not, then throw an error
    if "PP User" not in frappe.get_roles():
        frappe.throw(
            _(
                "You do not have a <b>PP User</b> role. Please contact your administrator to add your user profile as a <b>PP User</b>."
            ),
            title="Insufficient permissions. Please contact your administrator.",
        )

    if not frappe.db.exists("PP User", {"user": frappe.session.user}):
        frappe.throw(
            _(
                "You do not have a <b>PP User</b> profile. Please contact your administrator to add your user profile as a <b>PP User</b>."
            ),
            title="Insufficient permissions. Please contact your administrator.",
        )

    users = frappe.db.get_all(
        "PP User",
        fields=["full_name", "user_image", "name", "first_name", "enabled"],
        order_by="full_name",
    )
    return users


@frappe.whitelist(methods=["POST"])
def add_users_to_pp(users):

    if isinstance(users, str):
        users = json.loads(users)

    failed_users = []
    success_users = []

    for user in users:
        user_doc = frappe.get_doc("User", user)

        if user_doc.role_profile_name:
            failed_users.append(user_doc)

        elif hasattr(user_doc, "role_profiles") and len(user_doc.role_profiles) > 0:
            failed_users.append(user_doc)
        else:
            user_doc.append("roles", {"role": "PP User"})
            user_doc.save()
            success_users.append(user_doc)

    return {"success_users": success_users, "failed_users": failed_users}


@frappe.whitelist(methods=["POST"])
def create_user_account(person_id, new_password, sis_role):
    """
    Create a new user account for the person

    sis_role: The role to assign to the PP User, one of the following:
    Parent
    Teacher
    Admin
    """
    if not frappe.db.exists("SIS Person", person_id):
        return {
            "success": False,
            "message": "Person does not exist",
        }

    doc_person = frappe.get_doc("SIS Person", person_id)

    # Check if the user already exists
    if frappe.db.exists("User", doc_person.email):
        return {
            "success": False,
            "message": "User account already exists",
        }

    # Create a new user account
    doc_user = frappe.get_doc(
        {
            "doctype": "User",
            "email": doc_person.email,
            "first_name": doc_person.first_name,
            "last_name": doc_person.last_name,
            "full_name": doc_person.full_name,
            "roles": [{"role": "PP User"}],
            "send_welcome_email": 0,
            "enabled": 1,
            # "new_password": frappe.generate_hash()
        }
    )
    if new_password:
        doc_user.new_password = new_password
    frappe.flags.in_import = True
    doc_user.insert(ignore_permissions=True)

    if not frappe.db.exists("PP User", {"name": doc_user.name}):
        doc_pp_user = frappe.get_doc(
            {
                "doctype": "PP User",
                "user": doc_user.name,
                "person": person_id,
                "sis_role": sis_role,
                "enabled": 1,
            }
        )
        doc_pp_user.insert(ignore_permissions=True)

    frappe.flags.in_import = False

    return {
        "success": True,
        "message": "User account created successfully",
        "user": doc_user.name,
    }
