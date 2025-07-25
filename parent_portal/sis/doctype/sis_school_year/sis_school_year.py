# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SISSchoolYear(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        first_day: DF.Date
        last_day: DF.Date
        sequence_number: DF.Int
        status: DF.Literal["Past", "Current", "Upcoming"]
        title: DF.Data
    # end: auto-generated types

    def before_save(self):
        # convert string first_day to date and get year value
        current_year = frappe.utils.getdate(self.first_day).year
        settings = frappe.get_doc("SIS Settings")
        self.sequence_number = current_year - settings.founding_year
        self.title = self.title.strip()

    # def after_save(self):
    #     if self.status == "Current":
    #         frappe.get_single("SIS Settings").update(
    #             {"current_school_year": self.name}
    #         ).save()
    #         frappe.clear_cache()

    @staticmethod
    def get_current_school_year():
        current_school_year = frappe.get_single("SIS Settings").current_school_year
        if not current_school_year:
            frappe.throw("Current School Year not set in SIS Settings")
        return current_school_year
