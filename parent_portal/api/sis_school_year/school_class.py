import frappe
from parent_portal.sis.doctype.sis_school_year.sis_school_year import SISSchoolYear


def get_person_info_for_participants(school_class_name):
    """
    SQL Query to expand participants information
    """
    if not school_class_name:
        return []

    participants = frappe.db.sql(
        """
            SELECT
                DISTINCT `tabSIS School Class Person`.name AS name,
                `tabSIS School Class Person`.parent,
                `tabSIS School Class Person`.parenttype,
                `tabSIS School Class Person`.person AS person,
                `tabSIS School Class Person`.role AS role,
                `tabSIS Person`.full_name AS full_name,
                `tabSIS Person`.date_of_birth AS date_of_birth,
                `tabSIS Person`.avatar AS avatar
            FROM
                `tabSIS School Class Person`
                JOIN `tabSIS Person` ON `tabSIS School Class Person`.person = `tabSIS Person`.name
            WHERE
                `tabSIS School Class Person`.parent = %s
                AND `tabSIS School Class Person`.role = "Student"
            ORDER BY `tabSIS Person`.full_name ASC;
        """,
        (school_class_name,),
        as_dict=True,
    )
    return participants


@frappe.whitelist()
def get_all_school_class(limit=10, page=1, filters=None):
    # TODO
    # Verify person_id
    # Find list of school class and grade levels that person_id is associated with

    current_school_year = SISSchoolYear.get_current_school_year()

    if filters and isinstance(filters, str):
        filters = frappe.parse_json(filters)
    else:
        filters = {}

    filters["school_year"] = current_school_year

    # count number of class feeds
    total_count = frappe.db.count("SIS School Class", filters=filters)

    # pagination
    limit = int(limit)
    page = int(page)
    start = (page - 1) * limit

    school_classes = frappe.get_all(
        "SIS School Class",
        fields=["*"],
        filters=filters,
        limit=limit,
        start=start,
        order_by="creation desc",
    )
    if school_classes and len(school_classes) > 0:
        for school_class in school_classes:
            # participants = frappe.get_all(
            #     "SIS School Class Person",
            #     filters={"parent": school_class["name"]},
            #     fields=["*"],
            # )
            school_class["participants"] = get_person_info_for_participants(
                school_class["name"]
            )

    return {
        "total_count": total_count,
        "page": page,
        "limit": limit,
        "docs": school_classes,
    }


@frappe.whitelist()
def get_school_class_by_id(school_class_id):
    school_class = frappe.get_doc("SIS School Class", school_class_id).as_dict()

    if not school_class:
        frappe.throw("School class not found")

    school_class["participants"] = get_person_info_for_participants(school_class_id)

    return school_class


@frappe.whitelist()
def get_all_school_class_of_current_user():
    current_school_year = SISSchoolYear.get_current_school_year()

    pp_user = frappe.get_value(
        "PP User", {"user": frappe.session.user}, ["person", "sis_role"], as_dict=True
    )
    # Don't allow parents to get this information
    if pp_user.sis_role == "Parent":
        frappe.throw("Permission denied")

    # Find in `SIS SChool Class Person` where person_id is in the `person` field, then get all the school classes
    school_classes = frappe.get_all(
        "SIS School Class",
        filters={
            "name": [
                "in",
                [
                    person.parent
                    for person in frappe.get_all(
                        "SIS School Class Person",
                        filters={"person": pp_user.person},
                        fields=["parent"],
                    )
                ],
            ],
            "school_year": current_school_year,
        },
        fields=["*"],
    )

    return school_classes
