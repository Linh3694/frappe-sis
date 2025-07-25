# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SISClassFeed(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        class_type: DF.Literal["School Class", "Course Class"]
        content: DF.TextEditor | None
        course_class: DF.Link | None
        description: DF.SmallText | None
        public_time: DF.Datetime | None
        school_class: DF.Link | None
        school_year: DF.Data | None
        status: DF.Literal["Draft", "Waiting Approval", "Public"]
        title: DF.Data
    # end: auto-generated types

    def before_save(self):
        if self.class_type == "Course Class":
            school_year = frappe.get_value(
                "SIS Course Class", self.course_class, "school_year"
            )
            self.school_year = school_year
        else:
            school_year = frappe.get_value(
                "SIS School Class", self.school_class, "school_year"
            )
            self.school_year = school_year
