# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class SISSchoolClass(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from parent_portal.sis.doctype.sis_school_class_person.sis_school_class_person import (
            SISSchoolClassPerson,
        )

        participants: DF.Table[SISSchoolClassPerson]
        school_grade_level: DF.Link
        school_year: DF.Link
        short_title: DF.Data
        title: DF.Data
        total_students: DF.Int
    # end: auto-generated types

    def before_save(self):
        count_students = 0
        for participant in self.participants:
            if participant.role == "Student":
                count_students += 1
        self.total_students = count_students
