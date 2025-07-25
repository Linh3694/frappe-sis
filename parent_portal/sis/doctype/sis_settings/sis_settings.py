# Copyright (c) 2024, Digital Learning Team and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class SISSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		current_school_year: DF.Link
		founding_year: DF.Int
		welcome_guardian_email_template: DF.Link | None
	# end: auto-generated types
	pass
