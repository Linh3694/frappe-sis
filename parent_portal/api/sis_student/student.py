import frappe
from parent_portal.sis.doctype.sis_school_year.sis_school_year import SISSchoolYear
from frappe import _


@frappe.whitelist()
def get_children():
    current_school_year = SISSchoolYear.get_current_school_year()

    current_user = frappe.session.user

    # Check in SIS Person if the user exists
    pp_user = frappe.db.get_value("PP User", {"user": current_user}, ["*"], as_dict=1)
    if not pp_user:
        frappe.throw("User not found in PP User")

    # Check if current user is a guardian
    sis_person = frappe.db.get_value(
        "SIS Person", {"name": pp_user.person}, ["*"], as_dict=1
    )
    if not sis_person:
        frappe.throw("User not found in SIS Person")
    if sis_person.primary_role != "Guardian":
        frappe.throw("User is not a guardian")

    # Check if current user is a guardian
    guardian = frappe.db.get_value(
        "SIS Family Guardian", {"person": pp_user.person}, ["*"], as_dict=1
    )
    if not guardian:
        frappe.throw("User is not a guardian")

    # Join with SIS Family Child on parent field to get list of children
    children = frappe.db.sql(
        """
        SELECT 
            person.name as person_id, 
            person.full_name, 
            person.avatar, 
            person.email,
            student.wellspring_student_code,
            school_class.title as school_class_title, 
            school_class.short_title as school_class_short_title, 
            school_class.name as school_class_id
        FROM
            `tabSIS Family Child` child
            JOIN `tabSIS Person` person ON child.person = person.name
            JOIN `tabSIS School Class Person` class_person ON person.name = class_person.person
            JOIN `tabSIS School Class` school_class ON class_person.parent = school_class.name
            JOIN `tabSIS Student` student ON person.name = student.person
        WHERE 
            child.parent = %(parent)s
            AND school_class.school_year = %(current_school_year)s
        """,
        {"parent": guardian.parent, "current_school_year": current_school_year},
        as_dict=1,
    )

    return children


# ==================================================================================================
# Get Student information
# param: wssg student code
# outpout: {
# 			success : true/ false
# 			message(optional):
# 			data: {
# 				person [SIS Person] : name, full_name, email, date_of_birth
# 				family_members: {
# 							person_name, full_name, relationship_with_student
# 						}
#
# 			}
# ==================================================================================================
@frappe.whitelist()
def get_student_info(person_id):
    is_succ = True
    message = None
    data = []
    # find person with student code => email & DOB

    per_info = frappe.get_doc("SIS Person", person_id)
    if not per_info:
        is_succ = False
        message = _("Does not exist any information for Person {0}".format(person_id))
    else:
        doc_std = frappe.get_all(
            "SIS Student",
            fields=["name", "wellspring_student_code"],
            filters={"person": per_info.name},
            limit=1,
        )
        doc_std = doc_std[0]
        # find class
        class_name = frappe.db.get_value(
            "SIS School Class Person", {"person": per_info.name}, "parent"
        )
        doc_class = frappe.get_doc("SIS School Class", class_name)
        doc_school_year = frappe.get_doc("SIS School Year", doc_class.school_year)
        doc_school_grade_level = frappe.get_doc(
            "SIS School Grade Level", doc_class.school_grade_level
        )
        # find family
        family_name = frappe.db.get_value(
            "SIS Family Child", {"person": per_info.name}, "parent"
        )
        query = """
            SELECT
                tabRel.person, person.full_name, person.avatar, tabRel.relationship_with_student
            FROM (
                SELECT 
                    name, parent, person, null as relationship_with_student
                FROM `tabSIS Family Child` WHERE parent =  %(parent)s AND person != %(per_name)s
                UNION ALL
                SELECT 
                    name, parent, person, relationship_with_student
                FROM `tabSIS Family Guardian` WHERE parent =  %(parent)s
                ) as tabRel
            JOIN `tabSIS Person` person ON tabRel.person = person.name
        """
        family_members = frappe.db.sql(
            query, {"parent": family_name, "per_name": per_info.name}, as_dict=1
        )
        data = {
            "person": {
                "name": per_info.name,
                "avatar": per_info.avatar,
                "full_name": per_info.full_name,
                "email": per_info.email,
                "date_of_birth": per_info.date_of_birth,
                "gender": per_info.gender,
                "wellspring_student_code": doc_std.wellspring_student_code,
                "family": family_name,
            },
            "class": (
                {
                    "name:": doc_class.name,
                    "title": doc_class.title,
                    "short_title": doc_class.short_title,
                    "school_year": (
                        {
                            "name": doc_school_year.name,
                            "title": doc_school_year.title,
                            "status": doc_school_year.status,
                            "first_day": doc_school_year.first_day,
                            "last_day": doc_school_year.last_day,
                            "sequence_number": doc_school_year.sequence_number,
                        }
                        if doc_school_year
                        else None
                    ),
                    "school_grade_level": (
                        {
                            "name": doc_school_grade_level.name,
                            "title": doc_school_grade_level.title,
                            "short_title": doc_school_grade_level.short_title,
                            "sequence_number": doc_school_grade_level.sequence_number,
                        }
                        if doc_school_grade_level
                        else None
                    ),
                }
                if doc_class
                else None
            ),
            "family_members": family_members,
        }
    result = {"success": is_succ, "message": message, "data": data}
    return result


# ==================================================================================================
# Get All Student in Family
# param: wssg student code
# outpout: {
# 			success : true/ false
# 			message(optional):
# 			data: {
# 				 family_name:
# 				 children[SIS Person] : person_name, full_name, avatar, date_of_birth
# 										class [SIS SChool Class] : {name, title, short_title}
# 				}
# Notes: public API
#
# ==================================================================================================
@frappe.whitelist(allow_guest=True)
def get_student_infamily(std_code):
    is_success = True
    message = None
    data = []
    # find person with student code => email & DOB
    std_info = frappe.get_value(
        "SIS Student", {"wellspring_student_code": std_code}, ["name", "person"]
    )
    if not std_info:
        message = _("Does not exist any information for Student {0}".format(std_code))
        frappe.throw(message)
    std_person = std_info[1]
    # Check current class of student (for current school year)
    doc_student = frappe.get_doc("SIS Student", std_info[0])
    if not doc_student:
        frappe.throw(_("No have student for this code {0}".format(std_code)))
    std_current_class = doc_student.get_current_class()
    if not std_current_class:
        frappe.throw(_("Student {0} is not have current class".format(std_code)))
    # find family
    family_name = frappe.db.get_value(
        "SIS Family Child", {"person": std_person}, "parent"
    )
    doc_family = frappe.get_doc("SIS Family", family_name)
    child_data = []
    for child in doc_family.children:
        doc_child_person = frappe.get_doc("SIS Person", child.person)
        student_code = frappe.db.get_value(
            "SIS Student", {"person": doc_child_person.name}, "wellspring_student_code"
        )
        class_name = frappe.db.get_value(
            "SIS School Class Person", {"person": doc_child_person.name}, "parent"
        )
        doc_class = frappe.get_doc("SIS School Class", class_name)

        child_data.append(
            {
                "name": doc_child_person.name,
                "avatar": doc_child_person.avatar,
                "full_name": doc_child_person.full_name,
                "date_of_birth": doc_child_person.date_of_birth,
                "wellspring_student_code": student_code,
                "class": (
                    {
                        "name": doc_class.name,
                        "title": doc_class.title,
                        "short_title": doc_class.short_title,
                    }
                    if doc_class
                    else None
                ),
            }
        )
    data = {"family": family_name, "children": child_data}
    result = {"success": is_success, "message": message, "data": data}
    return result
