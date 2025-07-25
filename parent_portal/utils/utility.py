from frappe.utils import (validate_email_address)
import frappe
from frappe import _

def is_valid_email_exclude(in_email):
    exclude_email = frappe.db.get_single_value('PP Variable Setting', 'guar_regis_exclude') or 'wellspringsaigon.edu.vn'
    validate_email_address(in_email, throw=True)
    for ignore_email in exclude_email.split(';'):
        if in_email.endswith(ignore_email):
            frappe.throw(_('Email {0} is invalid. The "{1}" does not accepted').format(in_email, ignore_email), frappe.InvalidEmailAddressError)

def build_address(address, ward, district, province):
    items = [address,ward, district, province]
    # Remove None values using filter
    filtered_items = list(filter(lambda item: item is not None, items))
    return ', '.join(filtered_items) if len(filtered_items) > 0 else None

def split_fullname_by_firstname(full_name, first_name):
    if not first_name in full_name:
        frappe.throw(_('First Name must be a part of Full Name'), frappe.InvalidNameError)
    last_name = full_name.replace(first_name, "").strip()
    return first_name, last_name

		
def get_short_name(full_name):
    arr_str = full_name.split()
    count_item = len(arr_str)
    if count_item == 1:
        return full_name
    return ' '.join([arr_str[count_item-2], arr_str[count_item - 1]])