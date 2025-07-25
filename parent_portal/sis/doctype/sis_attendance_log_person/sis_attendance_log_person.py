# Copyright (c) 2024, Digital Learning Team and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class SISAttendanceLogPerson(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		attendance_code: DF.Literal["Present", "Late", "Authorized Absent", "Unauthorized Absent"]
		full_name: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		person: DF.Link
		reason: DF.Data | None
	# end: auto-generated types

	pass
