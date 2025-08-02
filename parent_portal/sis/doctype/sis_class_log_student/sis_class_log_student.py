# Copyright (c) 2024, Your Organization and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SISClassLogStudent(Document):
	def before_insert(self):
		# Tự động set thông tin audit khi tạo mới
		if hasattr(self, 'created_at'):
			self.created_at = frappe.utils.now()
		if hasattr(self, 'created_by'):
			self.created_by = frappe.session.user
	
	def before_save(self):
		# Tự động set thông tin audit khi cập nhật
		if hasattr(self, 'update_at'):
			self.update_at = frappe.utils.now()
		if hasattr(self, 'update_by'):
			self.update_by = frappe.session.user