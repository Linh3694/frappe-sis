# Copyright (c) 2024, Digital Learning Team and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class SISAcademicYearEvent(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		description: DF.SmallText | None
		enable: DF.Check
		end_date: DF.Date
		school_year: DF.Link
		start_date: DF.Date
		title: DF.SmallText
	# end: auto-generated types
	pass
