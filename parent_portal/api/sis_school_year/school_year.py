import frappe
from parent_portal.sis.doctype.sis_school_year.sis_school_year import SISSchoolYear


@frappe.whitelist()
def get_current_school_year():
    current_school_year = SISSchoolYear.get_current_school_year()
    current_school_year = frappe.get_doc("SIS School Year", current_school_year)
    return current_school_year.as_dict()


@frappe.whitelist()
def get_all_academic_year_events(limit=10, page=1, filters=None):
    # Get current academic year
    current_school_year = SISSchoolYear.get_current_school_year()

    if filters and isinstance(filters, str):
        filters = frappe.parse_json(filters)
    else:
        filters = {}

    filters["school_year"] = current_school_year

    # count number of class feeds
    total_count = frappe.db.count("SIS Academic Year Event", filters=filters)

    # pagination
    limit = int(limit)
    page = int(page)
    start = (page - 1) * limit

    events = frappe.get_all(
        "SIS Academic Year Event",
        fields=["*"],
        filters=filters,
        limit=limit,
        start=start,
        order_by="start_date asc",
    )
    return {
        "total_count": total_count,
        "page": page,
        "limit": limit,
        "docs": events,
    }
