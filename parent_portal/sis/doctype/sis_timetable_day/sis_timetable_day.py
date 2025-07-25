# Copyright (c) 2024, Digital Learning Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SISTimetableDay(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        short_title: DF.Data
        timetable_column: DF.Link
        title: DF.Data
        weekday: DF.Literal["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    # end: auto-generated types

    pass
