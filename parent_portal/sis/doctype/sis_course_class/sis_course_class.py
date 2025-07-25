# Copyright (c) 2024, Digital Learning Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SISCourseClass(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from parent_portal.sis.doctype.sis_course_class_person.sis_course_class_person import SISCourseClassPerson
        from parent_portal.sis.doctype.sis_timetable_day_row_class.sis_timetable_day_row_class import SISTimetableDayRowClass

        attendance: DF.Check
        class_type: DF.Literal["School Class", "Elective Class", "School Club", "Other"]
        course: DF.Link
        description: DF.SmallText | None
        enrollment_max: DF.Int
        enrollment_min: DF.Int
        from_grade_level: DF.Link | None
        from_school_class: DF.Link | None
        get_from: DF.Literal["School Class", "Grade Level"]
        participants: DF.Table[SISCourseClassPerson]
        school_year: DF.Link
        short_title: DF.Data
        timetable: DF.Link | None
        timetable_day_row_class: DF.Table[SISTimetableDayRowClass]
        title: DF.Data
        total_students: DF.Int
    # end: auto-generated types

    def before_save(self):
        for child in self.timetable_day_row_class:
            child.get_title()

        count_students = 0
        for participant in self.participants:
            if participant.role == "Student":
                count_students += 1
        self.total_students = count_students

    @frappe.whitelist()
    def get_timetable_column(self, timetable_day):
        return frappe.get_value("SIS Timetable Day", timetable_day, "timetable_column")

    @frappe.whitelist()
    def get_participants(self):
        """
        Fetch students from SIS School Class or Grade Level.

        self.get_from is either "School Class" or "Grade Level"
        self.from_school_class is the SIS School Class
        self.from_grade_level is the SIS Grade Level
        """
        participants = []
        if self.get_from == "School Class":
            if self.from_school_class:
                school_class = frappe.get_doc(
                    "SIS School Class", self.from_school_class
                )
                participants = school_class.participants
        else:
            if self.from_grade_level:
                grade_level = frappe.get_doc(
                    "SIS School Grade Level", self.from_grade_level
                )

                # Find all school class in this grade level
                school_classes = frappe.get_all(
                    "SIS School Class",
                    filters={"school_grade_level": grade_level.name},
                    fields=["name"],
                )

                # Get all participants in these school classes
                for school_class in school_classes:
                    participants.extend(
                        frappe.get_all(
                            "SIS School Class Person",
                            filters={"parent": school_class.name},
                            fields=["*"],
                        )
                    )

        # Fetch person info for each participant
        # for participant in participants:
        #     participant.person = frappe.get_doc("SIS Person", participant.person)

        return participants
