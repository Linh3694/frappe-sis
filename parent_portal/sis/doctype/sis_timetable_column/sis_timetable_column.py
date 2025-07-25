# Copyright (c) 2024, Digital Learning Team and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class SISTimetableColumn(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from parent_portal.sis.doctype.sis_timetable_column_row.sis_timetable_column_row import SISTimetableColumnRow

		short_title: DF.Data
		timetable_column_row: DF.Table[SISTimetableColumnRow]
		title: DF.Data
	# end: auto-generated types

	pass
