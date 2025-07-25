# Copyright (c) 2024, Digital Learning Team and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class SISRoom(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		active: DF.Check
		bulding: DF.Link
		capacity: DF.Int
		code: DF.Data
		comment: DF.SmallText | None
		floor: DF.Link
		short_title: DF.Data
		title: DF.Data
		type: DF.Literal["Classroom", "Hall", "Library", "Stadium"]
	# end: auto-generated types

	pass
