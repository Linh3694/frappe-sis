import frappe
def after_install():
    create_general_channel()


def create_general_channel():
    if not frappe.db.exists("PP Channel", "general"):
        channel = frappe.new_doc("PP Channel")
        channel.channel_name = "General"
        channel.name = "general"
        channel.save(ignore_permissions=True)
        frappe.db.commit()
