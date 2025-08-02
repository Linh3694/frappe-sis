# Copyright (c) 2024, Your Organization and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SISScoreBoard(Document):
	def before_insert(self):
		# Tự động set thông tin audit khi tạo mới
		if hasattr(self, 'create_at'):
			self.create_at = frappe.utils.now()
		if hasattr(self, 'create_date'):
			self.create_date = frappe.utils.now()
		if hasattr(self, 'submitted_at') and not self.submitted_at:
			self.submitted_at = frappe.utils.now()
	
	def before_save(self):
		# Tự động set thông tin audit khi cập nhật
		if hasattr(self, 'update_at'):
			self.update_at = frappe.utils.now()
		if hasattr(self, 'update_by'):
			self.update_by = frappe.session.user
		if hasattr(self, 'last_update'):
			self.last_update = frappe.utils.now()
		if hasattr(self, 'last_updated'):
			self.last_updated = frappe.utils.now()