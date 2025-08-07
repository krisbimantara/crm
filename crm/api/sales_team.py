import frappe
from frappe import _

@frappe.whitelist()
def get_linked_leads(sales_team):
    """Get linked leads for a sales team member"""

    if not frappe.has_permission("CRM Sales", "read", sales_team):
        frappe.throw("Not permitted", frappe.PermissionError)

    # Get leads linked to this sales team member
    leads = frappe.get_all(
        "CRM Lead",
        filters={"sales_id": sales_team},
        fields=[
            "name",
            "lead_name",
            "organization",
            "status",
            "email",
            "mobile_no",
            "lead_owner",
            "image",
            "first_name",
            "modified",
        ],
    )

    return leads