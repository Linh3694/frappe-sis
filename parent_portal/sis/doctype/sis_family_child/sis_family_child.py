# Copyright (c) 2024, Digital Learning Team and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class SISFamilyChild(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		notes: DF.SmallText | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		person: DF.Link
	# end: auto-generated types
	pass
