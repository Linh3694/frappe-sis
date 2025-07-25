import frappe


def redirect_user():
    pass


#     frappe.local.response["type"] = "redirect"
#     frappe.local.response["location"] = "/parent_portal"

# current_user = frappe.get_doc("User", frappe.session.user)
# # Get PP User
# pp_user = frappe.get_value(
#     "PP User", {"user": frappe.session.user}, ["name", "sis_role"], as_dict=True
# )
# if not pp_user:
#     return

# if pp_user.sis_role == "Guardian":
#     frappe.local.response["type"] = "redirect"
#     frappe.local.response["location"] = "/parent-portal"
