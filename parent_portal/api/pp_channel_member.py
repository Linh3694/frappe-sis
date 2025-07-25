import frappe


@frappe.whitelist()
def remove_channel_member(user_id, channel_id):
    # Get pp channel member name where user_id and channel_id match
    member = frappe.db.get_value("PP Channel Member", {
                                 "user_id": user_id, "channel_id": channel_id}, ["name"])
    # Delete pp channel member
    if member:
        frappe.delete_doc("PP Channel Member", member)
        frappe.db.commit()
    else:
        frappe.throw("User is not a member of this channel")

    return True
