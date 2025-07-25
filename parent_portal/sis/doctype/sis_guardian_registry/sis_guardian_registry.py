# Copyright (c) 2024, Digital Learning Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now
import parent_portal.utils.pp_const as PP_CONST
from parent_portal.utils.utility import split_fullname_by_firstname, build_address
from frappe.utils.password import update_password

STS_NEW = "New"
STS_DENY = "Deny"
STS_ACCEPT = "Accepted"
NEW_USER_DEFAULT_PASS = "wellspring@2024"


class SISGuardianRegistry(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        address: DF.Data | None
        amended_from: DF.Link | None
        company: DF.Data | None
        date_of_birth: DF.Date | None
        district: DF.Data | None
        email: DF.Data
        family: DF.Link | None
        family_info: DF.SmallText | None
        first_name: DF.Data | None
        full_name: DF.Data
        gender: DF.Literal["Male", "Female"]
        job_title: DF.Data | None
        nationality: DF.Data | None
        note: DF.SmallText | None
        person: DF.Link | None
        phone_number: DF.Data | None
        processed_by: DF.Data | None
        processed_date: DF.Datetime | None
        province: DF.Data | None
        reason: DF.SmallText | None
        relationship_with_student: DF.Data
        status: DF.Literal["New", "Accepted", "Deny"]
        ward: DF.Data | None
    # end: auto-generated types
    pass

    def get_addition_info(self):
        doc_family = frappe.get_doc("SIS Family", self.family)
        self.family_info = doc_family.family_description

    def on_update(self):
        if self.has_value_changed("status"):
            self.processed_by = frappe.session.user
            self.processed_date = now()


def load_family_info(doc, method):
    if not doc.family:
        return
    doc_family = frappe.get_doc("SIS Family", doc.family)
    doc.family_info = doc_family.get_family_description()


@frappe.whitelist()
def process_accept(name):
    doc_regis = frappe.get_doc("SIS Guardian Registry", name)

    first_name, last_name = split_fullname_by_firstname(
        doc_regis.full_name, doc_regis.first_name
    )
    # address = build_address(doc_regis.address, doc_regis.ward, doc_regis.district, doc_regis.province)
    # update or create SIS Person
    regis_person = frappe.db.get_value(
        "SIS Person",
        {"email": doc_regis.email, "primary_role": PP_CONST.SIS_PERSON_ROLE_GUARDIAN},
    )
    doc_person = None
    if regis_person:
        doc_person = frappe.get_doc("SIS Person", regis_person)
        doc_person.update(
            {
                "first_name": first_name,
                "last_name": last_name,
                "gender": doc_regis.gender,
                "date_of_birth": doc_regis.date_of_birth,
                "nationality": doc_regis.nationality,
                "email": doc_regis.email,
                "phone_number": doc_regis.phone_number,
                "primary_role": PP_CONST.SIS_PERSON_ROLE_GUARDIAN,
                "address": doc_regis.address,
                "province": doc_regis.province,
                "district": doc_regis.district,
                "ward": doc_regis.ward,
                "company": doc_regis.company,
                "job_title": doc_regis.job_title,
            }
        )
        doc_person.save()

    else:
        doc_person = frappe.get_doc(
            {
                "doctype": "SIS Person",
                "first_name": first_name,
                "last_name": last_name,
                "common_name": doc_regis.common_name,
                "gender": doc_regis.gender,
                "date_of_birth": doc_regis.date_of_birth,
                "nationality": doc_regis.nationality,
                "email": doc_regis.email,
                "phone_number": doc_regis.phone_number,
                "primary_role": PP_CONST.SIS_PERSON_ROLE_GUARDIAN,
                "address": doc_regis.address,
                "province": doc_regis.province,
                "district": doc_regis.district,
                "ward": doc_regis.ward,
                "company": doc_regis.company,
                "job_title": doc_regis.job_title,
            }
        )
        doc_person.insert(ignore_permissions=True)
    # create User by name
    doc_user = None
    is_sendmail = False
    if not frappe.db.exists("User", doc_regis.email):
        doc_user = frappe.get_doc(
            {
                "doctype": "User",
                "email": doc_regis.email,
                "first_name": first_name,
                "last_name": last_name,
                "full_name": doc_regis.full_name,
                "roles": [{"role": PP_CONST.PP_USER_ROLE}],
                "new_password": NEW_USER_DEFAULT_PASS,
                "send_welcome_email": 0,
            }
        )
        doc_user.insert(ignore_permissions=True)
        is_sendmail = True
        # Update the password for the newly created user
        # update_password(doc_regis.email, NEW_USER_DEFAULT_PASS)
    else:
        doc_user = frappe.get_doc("User", doc_regis.email)
    # Check if the role already exists for the user
    if not any(d.role == PP_CONST.PP_USER_ROLE for d in doc_user.roles):
        doc_user.append("roles", {"role": PP_CONST.PP_USER_ROLE})

    # create PP User
    if not frappe.db.exists("PP User", {"person": doc_person.name}):
        doc_pp_user = frappe.get_doc(
            {"doctype": "PP User", "person": doc_person.name, "user": doc_user.name}
        )
        doc_pp_user.insert(ignore_permissions=True)
    # update relationship for family
    doc_family = frappe.get_doc("SIS Family", doc_regis.family)
    if doc_family:
        person_guardian = frappe.db.get_value(
            "SIS Family Guardian",
            {"parent": doc_family.name, "person": doc_person.name},
        )
        if not person_guardian:
            doc_family.append(
                "guardians",
                {
                    "person": doc_person.name,
                    "relationship_with_student": doc_regis.relationship_with_student,
                },
            )
            doc_family.save()
    # send email
    if is_sendmail:
        doc_person.send_welcome_email_to_guardian(doc_user.name)
    # update registry information
    doc_regis.status = STS_ACCEPT
    doc_regis.save()
    doc_regis.submit()


@frappe.whitelist()
def process_deny(name, in_reason):
    doc_regis = frappe.get_cached_doc("SIS Guardian Registry", name)

    doc_regis.status = STS_DENY
    doc_regis.reason = in_reason

    doc_regis.save()
    doc_regis.submit()
