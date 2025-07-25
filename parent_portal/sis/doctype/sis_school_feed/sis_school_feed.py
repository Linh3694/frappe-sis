# Copyright (c) 2024, Digital Learning Team and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class SISSchoolFeed(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		content: DF.TextEditor | None
		description: DF.SmallText | None
		display_image: DF.AttachImage | None
		display_pdf: DF.Attach | None
		grade_levels: DF.Data
		public_time: DF.Datetime | None
		school_year: DF.Link
		status: DF.Literal["Draft", "Waiting Approval", "Public"]
		thumbnail: DF.AttachImage
		title: DF.Data
		to_all_schools: DF.Check
		to_high_school: DF.Check
		to_middle_school: DF.Check
		to_primary_school: DF.Check
	# end: auto-generated types

	pass
