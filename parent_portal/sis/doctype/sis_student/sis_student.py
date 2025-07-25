# Copyright (c) 2024, Digital Learning Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from parent_portal.sis.doctype.sis_school_year.sis_school_year import SISSchoolYear
from parent_portal.utils.utility import get_short_name


class SISStudent(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		avatar: DF.AttachImage | None
		current_school_class: DF.Data | None
		full_name: DF.Data
		moet_student_code: DF.Data | None
		person: DF.Link
		status: DF.Literal["Enabled", "Disabled"]
		wellspring_student_code: DF.Data
	# end: auto-generated types

	pass

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._current_class = None
	
	@property
	def current_class_code(self):
		doc_current_class = self.get_current_class()
		return doc_current_class.short_title if doc_current_class else None
	
	@property
	def current_class_title(self):
		doc_current_class = self.get_current_class()
		return doc_current_class.title if doc_current_class else None

	
	def get_current_class(self):
		if self._current_class == None:
			current_school_year = SISSchoolYear.get_current_school_year()
			if not current_school_year:
				return None
			
			query = ("""
						SELECT parent as current_class FROM `tabSIS School Class Person` 
							WHERE person = %(person)s 
							AND parent in (SELECT name FROM `tabSIS School Class` WHERE school_year = %(current_year)s)
					""")
			data = frappe.db.sql(query, {'person': self.person, 'current_year':current_school_year}, as_dict=1)
			
			if data and len(data) > 0:
				self._current_class = data[0].current_class
		doc_class = None
		if self._current_class:
			doc_class = frappe.get_doc('SIS School Class', self._current_class)
		return doc_class
	

def set_current_school_class(doc, method):
	if doc.current_school_class != None:
		return
	doc_current_class = doc.get_current_class()
	doc.current_school_class = doc_current_class.title if doc_current_class else None