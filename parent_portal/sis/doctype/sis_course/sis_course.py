# Copyright (c) 2024, Digital Learning Team and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class SISCourse(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		description: DF.SmallText | None
		program_type: DF.Literal["VP", "IP", "SSC", "Other"]
		short_title: DF.Data
		title: DF.Data
	# end: auto-generated types

	pass
