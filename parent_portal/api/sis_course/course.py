import frappe


@frappe.whitelist()
def get_all_course(limit=10, page=1, filters=None):
    # TODO
    # Verify person_id
    # Find list of school class and grade levels that person_id is associated with

    if filters and isinstance(filters, str):
        filters = frappe.parse_json(filters)

    # count number of class feeds
    total_count = frappe.db.count("SIS Course", filters=filters)

    # pagination
    limit = int(limit)
    page = int(page)
    start = (page - 1) * limit

    courses = frappe.get_all(
        "SIS Course",
        fields=["*"],
        filters=filters,
        limit=limit,
        start=start,
        order_by="creation desc",
    )

    return {
        "total_count": total_count,
        "page": page,
        "limit": limit,
        "docs": courses,
    }


@frappe.whitelist()
def get_course_by_id(course_id):
    course = frappe.get_doc("SIS Course", course_id)

    if not course:
        frappe.throw("Course not found")

    return course
