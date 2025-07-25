import frappe
from frappe import _
from frappe.utils import (getdate, validate_phone_number, validate_email_address)
from parent_portal.utils.utility import (is_valid_email_exclude, build_address)

@frappe.whitelist(allow_guest=True)
def check_exists_email(in_email):
    """
    Validate email format with exclude wellspring email
    If email exist in User => throw exception
    If email exist in SIS Person => return doc_person
    If not exist return True
    """
    is_valid_email_exclude(in_email)
    if frappe.db.exists("User", in_email):
        frappe.throw(_('Account {0} already exists.').format(in_email), frappe.DuplicateEntryError)

    if not frappe.db.exists("SIS Person", {"email": in_email}):
        return True #allow submit
    person_info = frappe.db.get_value('SIS Person', {'email' : in_email})
    doc_person = frappe.get_doc('SIS Person', person_info)
    return doc_person

@frappe.whitelist(allow_guest=True, methods=["POST"])
def input_guardian_registration(doc):
    """
    Create a new guardian registration.
    Args: doc has the following fields:
    - first_name: str not empty
    - last_name: str not empty
    - date_of_birth: date_string (DD-MM-YYYY)
    - gender: str not empty (Male/Female)
    - relationship_with_student: str not empty (Uppercase the first character)
    - family: str (family_name)
    - nationality : str
    - email: str (exclude @wellspringsaigon.edu.vn)
    - phone_number: str
    - address : str
    - province : str
    - district: str
    - ward : str
    - company: str
    - job_title : str
    """
    input_data = doc
    
    #==============Validate:=======================
    # required field: first_name, last_name, gender, relationship_with_student, family
    empty_data = []
    if not input_data['full_name']:
        empty_data.append(_("full_name"))
    if not input_data['relationship_with_student']:
        empty_data.append(_("Relationship with student"))
    if not input_data['family']:
        empty_data.append(_("Family"))
    if len(empty_data) > 0 :    
        frappe.throw(_('{0} is not empty').format(','.join(empty_data)))
    # date_of_birth format
    if input_data['date_of_birth']:
        dob = getdate(input_data['date_of_birth'])
        
    """Validate input data"""
    # email format (not @wellspringsaigon.edu.vn)
    if input_data['email']:
        check_exists_email(input_data['email'])    
        
    #phone format
    if input_data['phone_number']:
        validate_phone_number(input_data['phone_number'], throw=True)

    str_fullname = input_data['full_name'].title()
    str_firstname = input_data['first_name'].title()
    if not str_firstname in str_fullname:
        frappe.throw('First name {0} not in Full name {1}'.format(input_data['first_name'], input_data['full_name']), frappe.InvalidNameError)

    #Preprocess data: uppercase the first character of relationship, Address, Province, District, Ward
    relationship = input_data['relationship_with_student'].capitalize() if input_data['relationship_with_student'] else None
    str_gender = None
    if relationship:
        str_gender = 'Male' if relationship == "Father" else 'Female'
    str_province = input_data['province'].title() if input_data['province'] else None
    str_district = input_data['district'].title() if input_data['district'] else None
    str_ward = input_data['ward'].title() if input_data['ward'] else None
    str_street = input_data['address'].title() if input_data['address'] else None
    str_address = build_address(str_street, str_ward, str_district, str_province)
    doc_guardian_regis  = frappe.get_doc({
                                        'doctype' : 'SIS Guardian Registry',
                                          'full_name': str_fullname,
                                          'first_name' : str_firstname,
                                          'date_of_birth' : getdate(input_data['date_of_birth']) if input_data['date_of_birth'] else None,
                                          'gender' : str_gender,
                                          'nationality' : input_data['nationality'],
                                          'email' : input_data['email'],
                                          'phone_number' : input_data['phone_number'],
                                          'address' : str_address,
                                          'province' : str_province,
                                          'district' :  str_district,
                                          'ward' : str_ward,
                                          'company' : input_data['company'],
                                          'job_title' : input_data['job_title'],
                                          'relationship_with_student' : relationship,
                                          'family' : input_data['family'],
                                          'person' : input_data['person']
                                          })
    doc_guardian_regis.insert(ignore_permissions=True)
    frappe.db.commit()
    return True