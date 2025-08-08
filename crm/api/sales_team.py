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
            "creation",
            "modified",
        ],
    )

    return leads
@frappe.whitelist()
def get_fid():
    """
    Proxy backend untuk mengambil data List FID dari endpoint eksternal
    Menghindari CORS dengan melakukan request dari server Frappe.
    """
    import requests

    EXTERNAL_URL = "https://waha-n8n.0zvhbs.easypanel.host/webhook/get-fid"
    timeout = frappe.conf.get("fid_proxy_timeout", 10)

    try:
        resp = requests.get(EXTERNAL_URL, timeout=timeout)
        resp.raise_for_status()
        try:
            data = resp.json()
        except Exception:
            frappe.throw(_("Respon FID bukan JSON yang valid"))
        # Normalisasi payload: jika ada key "nasabah" (array), kembalikan list tersebut
        if isinstance(data, dict) and "nasabah" in data and isinstance(data["nasabah"], list):
            return data["nasabah"]
        # Jika yang dikembalikan langsung berupa list, kembalikan apa adanya
        if isinstance(data, list):
            return data
        # Jika bukan list, kembalikan list kosong agar konsisten dengan ekspektasi frontend
        return []
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "FID Proxy Error")
        frappe.throw(_("Gagal mengambil data FID melalui proxy backend: {0}").format(str(e)))