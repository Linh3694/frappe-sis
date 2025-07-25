# Copyright (c) 2024, Digital Learning Team and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class SISStaff(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		avatar: DF.AttachImage | None
		department: DF.Data | None
		employee_code: DF.Data
		full_name: DF.Data | None
		person: DF.Link
	# end: auto-generated types
	pass
