# Copyright (c) 2024, Digital Learning Team and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class SISTimetableColumnRow(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		short_title: DF.Data
		time_end: DF.Time
		time_start: DF.Time
		title: DF.Data
		type: DF.Literal["Lesson", "Break", "Lunch", "Snack", "Other"]
	# end: auto-generated types

	pass
