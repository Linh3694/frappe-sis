# Copyright (c) 2024, Digital Learning Team and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class SISSchoolYearTerm(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		first_day: DF.Date
		last_day: DF.Date
		school_year: DF.Link
		title: DF.Data
	# end: auto-generated types
	pass
