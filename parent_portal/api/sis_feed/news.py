import frappe


@frappe.whitelist()
def get_news(student_id):
    # Check if student exists
    student = frappe.get_doc("SIS Student", student_id)
    if not student or student.status != "Enabled":
        return frappe.throw("Student not found")

    return frappe.get_all("SIS School Feed", fields=["*"])
