# Copyright (c) 2024, Digital Learning Team and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from frappe.utils.data import nowdate, nowtime


class SISAttendanceLogCourseClass(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from parent_portal.sis.doctype.sis_attendance_log_person.sis_attendance_log_person import (
            SISAttendanceLogPerson,
        )

        course: DF.Link
        course_class: DF.Link
        date: DF.Date | None
        direction: DF.Literal["In", "Out"]
        period: DF.Literal[None]
        person_taker: DF.Link
        school_year: DF.Link
        student_list: DF.Table[SISAttendanceLogPerson]
        timestamp_taken: DF.Time | None
        timetable_day_row_class: DF.Link
    # end: auto-generated types

    def before_insert(self):
        self.date = nowdate()
        self.timestamp_taken = nowtime()
