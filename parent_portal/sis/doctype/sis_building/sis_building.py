# Copyright (c) 2024, Digital Learning Team and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class SISBuilding(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		country: DF.Data
		description: DF.SmallText | None
		district: DF.Data
		province: DF.Data
		title: DF.Data
		ward: DF.Data
	# end: auto-generated types

	pass
