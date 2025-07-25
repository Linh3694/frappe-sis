# Copyright (c) 2024, Digital Learning Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from parent_portal.utils import pp_const as PP_CONST


class SISPerson(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        address: DF.Data | None
        avatar: DF.AttachImage | None
        common_name: DF.Data | None
        company: DF.Data | None
        date_of_birth: DF.Date | None
        district: DF.Data | None
        email: DF.Data | None
        english_name: DF.Data | None
        first_name: DF.Data
        full_name: DF.Data | None
        gender: DF.Literal["Male", "Female"]
        job_title: DF.Data | None
        last_name: DF.Data
        middle_name: DF.Data | None
        nationality: DF.Data | None
        phone_number: DF.Data | None
        primary_role: DF.Literal["Student", "Guardian", "Teacher", "TA", "Nanny", "Staff"]
        province: DF.Data | None
        ward: DF.Data | None
    # end: auto-generated types

    def before_save(self):
        self.first_name = self.first_name.strip() if self.first_name else ""
        self.middle_name = (
            (" " + self.middle_name.strip() + " ") if self.middle_name else " "
        )
        self.last_name = self.last_name.strip() if self.last_name else ""
        self.full_name = self.last_name + self.middle_name + self.first_name
        

    def send_welcome_email_to_guardian(self, username):
        from frappe.utils import get_url

        if self.primary_role != PP_CONST.SIS_PERSON_ROLE_GUARDIAN:
            frappe.throw(_('Can not execute this function for role {0}'.format(self.primary_role)))
        
        doc_user = frappe.get_doc('User', username)
        pp_welcome_email_template = frappe.get_single('SIS Settings').welcome_guardian_email_template
        
        subject = _("Complete Registration")

        doc_user.send_login_mail(subject, 
                                template="welcome_new_guardian", 
                                add_args = dict(
                                            site_url=get_url(),
                                            link=get_url() + "/parent_portal",
                                            ),
                                custom_template=pp_welcome_email_template,)
        
