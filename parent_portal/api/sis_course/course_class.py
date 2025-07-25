import frappe
from datetime import datetime
from parent_portal.sis.doctype.sis_school_year.sis_school_year import SISSchoolYear


def filter_period_by_date(course_class_name, date):
    """
    Extract information of timetable_day_row_class and filter by date.

    Date has to be in the format "YYYY-MM-DD".
    """
    return frappe.db.sql(
        """
        SELECT
            DISTINCT `tabSIS Timetable Day Row Class`.name AS timetable_day_row_class,
            `tabSIS Timetable Day Date`.date AS date,
            `tabSIS Timetable Day`.name AS timetable_day,
            `tabSIS Timetable Day`.title AS timetable_day_title,
            `tabSIS Timetable Column Row`.name AS timetable_column_row,
            `tabSIS Timetable Column Row`.title AS timetable_column_row_title,
            `tabSIS Timetable Column Row`.time_start AS time_start,
            `tabSIS Timetable Column Row`.time_end AS time_end

        FROM
            `tabSIS Timetable Day Row Class`
            JOIN `tabSIS Timetable Day` ON `tabSIS Timetable Day Row Class`.timetable_day = `tabSIS Timetable Day`.name
            JOIN `tabSIS Timetable Day Date` ON `tabSIS Timetable Day`.name = `tabSIS Timetable Day Date`.timetable_day      
            JOIN `tabSIS Timetable Column Row` ON `tabSIS Timetable Day Row Class`.timetable_column_row = `tabSIS Timetable Column Row`.name
        WHERE
            `tabSIS Timetable Day Row Class`.parent = %s
            AND `tabSIS Timetable Day Date`.date = %s
        ORDER BY `tabSIS Timetable Column Row`.time_start ASC;               
    """,
        (course_class_name, date),
        as_dict=True,
    )


def get_person_info_for_participants(course_class_name):
    """
    SQL Query to expand participants information
    """
    if not course_class_name:
        return []

    current_school_year = SISSchoolYear.get_current_school_year()

    participants = frappe.db.sql(
        """
            SELECT
                DISTINCT `tabSIS Course Class Person`.name AS name,
                `tabSIS Course Class Person`.parent,
                `tabSIS Course Class Person`.parenttype,
                `tabSIS Course Class Person`.person AS person,
                `tabSIS Person`.full_name AS full_name,
                `tabSIS Course Class Person`.role AS role,
                `tabSIS Person`.date_of_birth AS date_of_birth,
                `tabSIS Person`.avatar AS avatar,
                `tabSIS School Class`.title AS school_class_title,
                `tabSIS School Class`.short_title AS school_class_short_title
            FROM
                `tabSIS Course Class Person`
                JOIN `tabSIS Person` ON `tabSIS Course Class Person`.person = `tabSIS Person`.name
                JOIN `tabSIS School Class Person` ON `tabSIS Course Class Person`.person = `tabSIS School Class Person`.person
                JOIN `tabSIS School Class` ON `tabSIS School Class Person`.parent = `tabSIS School Class`.name
            WHERE
                `tabSIS Course Class Person`.parent = %s
                AND `tabSIS School Class`.school_year = %s
                AND `tabSIS Course Class Person`.role = "Student"
            ORDER BY `tabSIS Person`.full_name ASC;
        """,
        (course_class_name, current_school_year),
        as_dict=True,
    )
    return participants


@frappe.whitelist()
def get_all_course_class(limit=10, page=1, filters=None):
    # TODO
    # Verify person_id
    # Find list of school class and grade levels that person_id is associated with

    if filters and isinstance(filters, str):
        filters = frappe.parse_json(filters)
    else:
        filters = {}

    # Get current academic year
    current_school_year = SISSchoolYear.get_current_school_year()
    filters['school_year'] = current_school_year

    # count number of class feeds
    total_count = frappe.db.count("SIS Course Class", filters=filters)

    # pagination
    limit = int(limit)
    page = int(page)
    start = (page - 1) * limit

    course_classes = frappe.get_all(
        "SIS Course Class",
        fields=["*"],
        filters=filters,
        limit=limit,
        start=start,
        order_by="creation desc",
    )
    if course_classes and len(course_classes) > 0:
        for course_class in course_classes:
            # participants = frappe.get_all(
            #     "SIS Course Class Person",
            #     filters={"parent": course_class["name"]},
            #     fields=["*"],
            # )
            course_class["participants"] = get_person_info_for_participants(
                course_class["name"]
            )

    return {
        "total_count": total_count,
        "page": page,
        "limit": limit,
        "docs": course_classes,
    }


@frappe.whitelist()
def get_course_class_by_id(
    course_class_id, attendance_check=False, attendance_date=None
):
    course_class = frappe.get_doc("SIS Course Class", course_class_id).as_dict()

    if not course_class:
        frappe.throw("Course Class not found")

    course_class["participants"] = get_person_info_for_participants(course_class_id)

    if attendance_check:
        # Validate attendance_date
        if not attendance_date:
            attendance_date = datetime.now().strftime("%Y-%m-%d")

        try:
            datetime.strptime(attendance_date, "%Y-%m-%d")
        except ValueError:
            frappe.throw("Invalid date format for checking attendance")

        # Filter timetable_day_row_class based on attendance_date
        course_class["timetable_day_row_class"] = filter_period_by_date(
            course_class_id, attendance_date
        )

    return course_class


@frappe.whitelist()
def get_all_course_class_of_current_user():
    pp_user = frappe.get_value(
        "PP User", {"user": frappe.session.user}, ["person", "sis_role"], as_dict=True
    )
    # Don't allow parents to get this information
    if pp_user.sis_role == "Parent":
        frappe.throw("Permission denied")

    # Get current academic year
    current_school_year = SISSchoolYear.get_current_school_year()

    # Find in `SIS SChool Class Person` where person_id is in the `person` field, then get all the school classes
    course_classes = frappe.get_all(
        "SIS Course Class",
        filters={
            "name": [
                "in",
                [
                    person.parent
                    for person in frappe.get_all(
                        "SIS Course Class Person",
                        filters={"person": pp_user.person},
                        fields=["parent"],
                    )
                ],
            ],
            "school_year": current_school_year
        },
        fields=["*"],
    )

    return course_classes
