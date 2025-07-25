# Copyright (c) 2024, Digital Learning Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.core.utils import html2text
import datetime



class PPMessage(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		channel_id: DF.Link
		content: DF.LongText | None
		is_edited: DF.Check
		message_type: DF.Literal["Text", "Image", "File"]
		text: DF.LongText | None
	# end: auto-generated types

	def before_validate(self):
		try:
			if self.text:
				content = html2text(self.text)
				# Remove trailing new line characters and white spaces
				self.content = content.rstrip()
		except Exception:
			pass

	def after_insert(self):
		frappe.publish_realtime(
			'pp:unread_channel_count_updated', {
				'channel_id': self.channel_id,
				'sent_by': self.owner,
			})

	def after_delete(self):
		self.send_update_event(type="delete")

	def on_update(self):
		self.send_update_event(type="update")

	def send_update_event(self, type):
		frappe.publish_realtime('message_updated', {
			'channel_id': self.channel_id,
			'sender': frappe.session.user,
			'message_id': self.name,
			'type': type,
			},
			doctype='PP Channel',
			# Adding this to automatically add the room for the event via Frappe
			docname=self.channel_id,
			after_commit=True
		)
		frappe.db.commit()

	pass

def on_doctype_update():
	'''
	Add indexes to PP Message table
	'''
	# Index the selector (channel or message type) first for faster queries (less rows to sort in the next step)
	frappe.db.add_index("PP Message", ["channel_id", "creation"])
	frappe.db.add_index("PP Message", ["message_type", "creation"])


# @frappe.whitelist(methods=['POST'])
# def send_message(channel_id, user_id, text):
#     doc = frappe.get_doc({
#         'doctype': 'PP Message',
#         'channel_id': channel_id,
#         'text': text,
#         'user_id': user_id
#     })
#     doc.insert()
#     frappe.publish_realtime('message_received', {
# 				'channel_id': channel_id
# 		}, after_commit=True)
#     frappe.db.commit()
#     return "message sent"
