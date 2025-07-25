# Copyright (c) 2024, Digital Learning Team and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class SISTimetable(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from parent_portal.sis.doctype.sis_timetable_day.sis_timetable_day import (
            SISTimetableDay,
        )

        grade_level_list: DF.Data
        school_year: DF.Link
        short_title: DF.Data
        status: DF.Literal["Active", "Inactive"]
        timetable_days: DF.Table[SISTimetableDay]
        title: DF.Data
    # end: auto-generated types

    pass
