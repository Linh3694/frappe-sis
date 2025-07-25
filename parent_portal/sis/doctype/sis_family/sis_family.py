# Copyright (c) 2024, Digital Learning Team and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class SISFamily(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from parent_portal.sis.doctype.sis_family_child.sis_family_child import SISFamilyChild
		from parent_portal.sis.doctype.sis_family_guardian.sis_family_guardian import SISFamilyGuardian

		children: DF.Table[SISFamilyChild]
		family_key: DF.Data | None
		guardians: DF.Table[SISFamilyGuardian]
		home_address: DF.Data
		status: DF.Literal["Married", "Separated", "Divorced", "De Facto", "Other", "Single"]
	# end: auto-generated types
	# pass


	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._family_info = None


	@property
	def family_description(self):
		return self._family_info

	def get_family_description(self):
		if self._family_info == None:
			array_child = []
			array_guardian = []
			for child in self.children:
				doc_person = frappe.get_doc('SIS Person', child.person)
				std_name = frappe.db.get_value('SIS Student', {'person': child.person})
				doc_student = frappe.get_doc('SIS Student', std_name)
				str_child = "	- {0}: {1}".format(doc_person.full_name, doc_student.current_class_title if doc_student else "Class NAN")
				array_child.append(str_child)

			for guard in self.guardians:
				doc_person = frappe.get_doc('SIS Person', guard.person)
				str_guard = "	- {0}:{1}".format(guard.relationship_with_student, doc_person.full_name)
				array_guardian.append(str_guard)

			self._family_info = _("Family members:\n") + "\n".join(array_child) + "\n" + "\n".join(array_guardian)
		return self._family_info