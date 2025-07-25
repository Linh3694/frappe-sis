# Copyright (c) 2024, Digital Learning Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PPUser(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        enabled: DF.Check
        first_name: DF.Data | None
        full_name: DF.Data
        person: DF.Link
        sis_role: DF.Literal["Parent", "Teacher", "Admin"]
        user: DF.Link
        user_image: DF.AttachImage | None
    # end: auto-generated types

    # def before_validate(self):
    # 	if not self.full_name:
    # 		self.full_name = self.first_name

    # def before_save(self):
    # 	self.update_photo_from_user()

    def after_delete(self):
        """
        Remove the PP User role from the user.
        """
        user = frappe.get_doc("User", self.user)
        user.flags.ignore_permissions = True
        user.flags.deleting_pp_user = True
        user.remove_roles("PP User")
        user.save()

    def update_photo_from_user(self):
        """
        We need to create a new File record for the user image and attach it to the PP User record.
        Why not just copy the URL from the User record? Because the URL is not accessible to the PP User,
        and Frappe creates a duplicate file in the system (that is public) but does not update the URL in the field.
        """
        user_image = frappe.db.get_value("User", self.user, "user_image")
        if user_image and not self.user_image:
            image_file = frappe.get_doc(
                {
                    "doctype": "File",
                    "file_url": user_image,
                    "attached_to_doctype": "PP User",
                    "attached_to_name": self.name,
                    "attached_to_field": "user_image",
                    "is_private": 1,
                }
            ).insert()
            self.user_image = image_file.file_url

    pass


def add_user_to_pp(doc, method):
    # called when the user is inserted or updated
    # If the auto-create setting is set to True, check if the user is a System user. If yes, then create a PP User record for the user.
    # Else, check if the user has a PP User role. If yes, then create a PP User record for the user if not already created.
    return
    # If the user is already added to PP, do nothing.
    if not doc.flags.deleting_pp_user:
        if frappe.db.exists("PP User", {"user": doc.name}):
            # Check if the role is still present. If not, then inactivate the PP User record.
            has_pp_role = False
            for role in doc.get("roles"):
                if role.role == "PP User":
                    has_pp_role = True
                    break

            if has_pp_role:
                pp_user = frappe.get_doc("PP User", {"user": doc.name})
                pp_user.enabled = 1
                pp_user.save(ignore_permissions=True)
            else:
                pp_user = frappe.get_doc("PP User", {"user": doc.name})
                pp_user.enabled = 0
                pp_user.save(ignore_permissions=True)
        else:
            # PP user does not exist.
            # Only create pp user if it exists in the system.
            if frappe.db.exists("User", doc.name):
                # Check if the user is a system user.
                if doc.user_type == "System User":
                    doc.append("roles", {"role": "PP User"})
                    # Create a PP User record for the user.
                    pp_user = frappe.new_doc("PP User")
                    pp_user.user = doc.name
                    if not doc.full_name:
                        pp_user.full_name = doc.first_name
                    pp_user.enabled = 1
                    pp_user.insert(ignore_permissions=True)
                else:
                    if "PP User" in [d.role for d in doc.get("roles")]:
                        # Create a PP User record for the user.
                        pp_user = frappe.new_doc("PP User")
                        pp_user.user = doc.name
                        if not doc.full_name:
                            pp_user.full_name = doc.first_name
                        pp_user.enabled = 1
                        pp_user.insert(ignore_permissions=True)


def remove_user_from_pp(doc, method):
    # called when the user is deleted
    # If the user is deleted, then delete the PP User record for the user.
    if frappe.db.exists("PP User", {"user": doc.name}):
        pp_user = frappe.get_doc("PP User", {"user": doc.name})
        pp_user.delete(ignore_permissions=True)
