import frappe
from pypika import JoinType, Order
from parent_portal.api.pp_users import get_list
from frappe import _

@frappe.whitelist(methods=['GET'])
def get_channel_members(channel_id):
    # Check if the user has permission to view the channel
    # fetch all channel members
    # get member details from user table, such as name, full_name, user_image, first_name

    if frappe.has_permission("PP Channel", doc=channel_id):
        member_array = []
        if frappe.db.exists("PP Channel", channel_id):
            channel_member = frappe.qb.DocType('PP Channel Member')
            user = frappe.qb.DocType('PP User')
            if frappe.get_cached_value("PP Channel", channel_id, "type") == "Open":
                member_array = get_list()
            else:
                member_query = (frappe.qb.from_(channel_member)
                                .join(user, JoinType.left)
                                .on(channel_member.user_id == user.name)
                                .select(user.name, user.full_name, user.user_image, user.first_name, channel_member.is_admin)
                                .where(channel_member.channel_id == channel_id)
                                .orderby(channel_member.creation, order=Order.desc))

                member_array = member_query.run(as_dict=True)

            member_object = {}
            for member in member_array:
                member_object[member.name] = member
            return member_object

        else:
            frappe.throw(_("Channel {} does not exist".format(channel_id)), frappe.DoesNotExistError)
    
    else:
        frappe.throw(_("You do not have permission to view this channel"), frappe.PermissionError)
