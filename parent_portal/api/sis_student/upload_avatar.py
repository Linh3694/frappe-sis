import frappe
from frappe.utils.file_manager import save_file
import re


@frappe.whitelist()
def upload_avatar():
    file = frappe.request.files.get("avatar")
    if not file:
        frappe.throw("No file found")
    replace = frappe.form_dict.get("replace")

    # Save the file
    filename = file.filename
    file_content = file.read()

    # extract student code from filename, example WS12345678
    student_code = re.search(r"WS\d{8}", filename)
    if not student_code:
        frappe.throw("Invalid filename format: No student code found")
    student_code = student_code.group()

    student = frappe.get_doc(
        "SIS Student",
        {"wellspring_student_code": student_code},
        ["name", "person"],
    )
    school_class_title = student.get_current_class().title

    student_person = frappe.get_doc("SIS Person", student.person)
    if student_person.avatar:
        if not (replace.lower() == "y"):
            return {
                "success": False,
                "message": "Avatar already exists.",
                "url": student_person.avatar,
                "student_code": student_code,
                "student_name": student_person.full_name,
                "school_class": school_class_title,
            }
        # Delete the old avatar
        file_obj_id = frappe.get_value(
            "File",
            {
                "file_url": student_person.avatar,
                "attached_to_doctype": "SIS Person",
                "attached_to_name": student.person,
            },
            "name",
        )
        if file_obj_id:
            frappe.delete_doc("File", file_obj_id, ignore_permissions=True)

    # Save the file
    file_doc = save_file(
        filename, file_content, "SIS Person", student.person, is_private=1
    )

    # Update the student's avatar in SIS Person
    frappe.db.set_value("SIS Person", student.person, "avatar", file_doc.file_url)

    return {
        "success": True,
        "message": "Avatar uploaded successfully",
        "url": file_doc.file_url,
        "student_code": student_code,
        "student_name": student_person.full_name,
        "school_class": school_class_title,
    }
