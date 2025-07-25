# Copyright (c) 2024, Digital Learning Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SISTimetableDayRowClass(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        description: DF.Data | None
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        timetable_column: DF.Data | None
        timetable_column_row: DF.Link
        timetable_day: DF.Link
        title: DF.Data | None
    # end: auto-generated types

    def get_title(self):
        timetable_day_title = frappe.get_value(
            "SIS Timetable Day", self.timetable_day, "short_title"
        )
        timetable_column_row = frappe.get_value(
            "SIS Timetable Column Row",
            self.timetable_column_row,
            ["short_title", "time_start", "time_end"],
            as_dict=1,
        )
        self.title = f"{timetable_day_title} - {timetable_column_row.short_title} {timetable_column_row.time_start} - {timetable_column_row.time_end}"
