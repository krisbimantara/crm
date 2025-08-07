# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CRMSales(Document):
	def before_save(self):
		if not self.nama:
			user = frappe.get_doc("User", self.user_id)
			self.nama = user.full_name

	@staticmethod
	def default_list_data():
		columns = [
			{
				"label": "Name",
				"type": "Data",
				"key": "nama",
				"width": "12rem",
			},
			{
				"label": "User ID",
				"type": "Link",
				"key": "user_id",
				"options": "User",
				"width": "12rem",
			},
			{
				"label": "Cabang",
				"type": "Data",
				"key": "cabang",
				"width": "12rem",
			},
			{
				"label": "Pincab",
				"type": "Link",
				"key": "pincab",
				"options": "CRM Sales",
				"width": "12rem",
			},
			{
				"label": "Last Modified",
				"type": "Datetime",
				"key": "modified",
				"width": "8rem",
			},
		]
		rows = [
			"name",
			"nama",
			"user_id",
			"cabang",
			"pincab",
			"modified",
		]
		return {"columns": columns, "rows": rows}
