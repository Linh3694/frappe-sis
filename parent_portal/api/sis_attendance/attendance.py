import frappe
from datetime import datetime


@frappe.whitelist()
def create_attendance_log_school_class(doc):
    """
    Create a new attendance log for a school class.

    Args: doc has the following fields:
    - school_year: str if empty, will use the current school year
    - school_class: str
    - person_taker: str if empty, will use the current user person id
    - student_list: list of student dict with the following fields:
        - person: str
        - attendance_code: str (Present, Late, Authorized Absent, Unauthorized Absent)

    Example:
    {
        "doc": {
            "school_year": "15af1fa3b3",
            "school_class": "61532ec002",
            "person_taker": "9b7c79dcdd",
            "student_list": [
            {
                "person": "afd44d1e30",
                "attendance_code": "Late"
            },
            ]
        }
    }
    """
    doc = frappe.parse_json(doc)

    # Check if doc has school_year
    if not doc.get("school_year"):
        school_year = frappe.get_doc("SIS School Year", {"status": "Current"})
        doc["school_year"] = school_year.name

    # Check if doc has person_taker
    if not doc.get("person_taker"):
        doc["person_taker"] = frappe.get_value(
            "PP User", {"user": frappe.session.user}, "person"
        )

    attendance_log = frappe.new_doc("SIS Attendance Log School Class")
    attendance_log.update(doc)
    attendance_log.save(ignore_permissions=True)
    return attendance_log


@frappe.whitelist()
def create_attendance_log_course_class(doc):
    """
    Create a new attendance log for a course class.

    Args: doc has the following fields:
    - course_class: str
    - person_taker: str if empty, will use the current user person id
    - student_list: list of student dict with the following fields:
        - person: str
        - attendance_code: str (Present, Late, Authorized Absent, Unauthorized Absent)

    Example:
    {
        "doc": {
            "school_year": "15af1fa3b3",
            "course":"6d49aa7391",
            "course_class": "4f3b18a439",
            "timetable_day_row_class": "e44e409630",
            "person_taker": "9b7c79dcdd",
            "student_list": [
            {
                "person": "fdc560f608",
                "attendance_code": "Late"
            }
            ]
        }
    }
    """
    doc = frappe.parse_json(doc)

    course_class = frappe.get_doc("SIS Course Class", doc["course_class"])
    doc["course"] = course_class.course
    doc["school_year"] = course_class.school_year

    # Check if doc has person_taker
    if not doc.get("person_taker"):
        doc["person_taker"] = frappe.get_value(
            "PP User", {"user": frappe.session.user}, "person"
        )

    attendance_log = frappe.new_doc("SIS Attendance Log Course Class")
    attendance_log.update(doc)
    attendance_log.save(ignore_permissions=True)
    return attendance_log


@frappe.whitelist()
def get_attendance_log_school_class_by_date(school_class_id, date=None):
    """
    Get all attendance logs for a school class by date
    """
    # if date Verify whether date has format YYYY-MM-DD, otherwise take today's date
    if not date:
        date = frappe.utils.nowdate()
    else:
        try:
            date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            frappe.throw("Invalid date format. Please use YYYY-MM-DD")

    attendance_logs = frappe.get_all(
        "SIS Attendance Log School Class",
        fields=["*"],
        filters={"school_class": school_class_id, "date": date},
    )

    if attendance_logs and len(attendance_logs) > 0:
        for attendance_log in attendance_logs:
            # attendance_log["student_list"] = frappe.get_all(
            #     "SIS Attendance Log Person",
            #     filters={"parent": attendance_log["name"]},
            #     fields=["*"],
            # )
            attendance_log["student_list"] = frappe.db.sql(
                """
                SELECT
                    `tabSIS Attendance Log Person`.person,
                    `tabSIS Attendance Log Person`.attendance_code,
                    `tabSIS Attendance Log Person`.reason,
                    `tabSIS Person`.full_name,
                    `tabSIS Person`.date_of_birth,
                    `tabSIS School Class`.title AS school_class_title,
                    `tabSIS School Class`.short_title AS school_class_short_title
                FROM
                    `tabSIS Attendance Log Person`
                    JOIN `tabSIS Person` ON `tabSIS Attendance Log Person`.person = `tabSIS Person`.name
                    JOIN `tabSIS School Class Person` ON `tabSIS Attendance Log Person`.person = `tabSIS School Class Person`.person
                    JOIN `tabSIS School Class` ON `tabSIS School Class Person`.parent = `tabSIS School Class`.name
                WHERE
                    `tabSIS Attendance Log Person`.parent = %s;
                """,
                (attendance_log["name"]),
                as_dict=True,
            )
            attendance_log["school_year"] = frappe.get_doc(
                "SIS School Year",
                attendance_log["school_year"],
            )
            attendance_log["school_class"] = frappe.get_value(
                "SIS School Class",
                attendance_log["school_class"],
                ["name", "title", "short_title"],
                as_dict=True,
            )
            attendance_log["person_taker"] = frappe.get_value(
                "SIS Person",
                attendance_log["person_taker"],
                ["name", "full_name"],
                as_dict=True,
            )

    return attendance_logs


@frappe.whitelist()
def get_attendance_log_course_class_by_date(course_class_id, date=None):
    """
    Get all attendance logs for a course class by date
    """
    # if date Verify whether date has format YYYY-MM-DD, otherwise take today's date
    if not date:
        date = frappe.utils.nowdate()
    else:
        try:
            date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            frappe.throw("Invalid date format. Please use YYYY-MM-DD")

    attendance_logs = frappe.get_all(
        "SIS Attendance Log Course Class",
        fields=["*"],
        filters={"course_class": course_class_id, "date": date},
    )

    if attendance_logs and len(attendance_logs) > 0:
        for attendance_log in attendance_logs:
            # attendance_log["student_list"] = frappe.get_all(
            #     "SIS Attendance Log Person",
            #     filters={"parent": attendance_log["name"]},
            #     fields=["*"],
            # )
            attendance_log["student_list"] = frappe.db.sql(
                """
                SELECT
                    `tabSIS Attendance Log Person`.person,
                    `tabSIS Attendance Log Person`.attendance_code,
                    `tabSIS Attendance Log Person`.reason,
                    `tabSIS Person`.full_name,
                    `tabSIS Person`.date_of_birth,
                    `tabSIS School Class`.title AS school_class_title,
                    `tabSIS School Class`.short_title AS school_class_short_title
                FROM
                    `tabSIS Attendance Log Person`
                    JOIN `tabSIS Person` ON `tabSIS Attendance Log Person`.person = `tabSIS Person`.name
                    JOIN `tabSIS School Class Person` ON `tabSIS Attendance Log Person`.person = `tabSIS School Class Person`.person
                    JOIN `tabSIS School Class` ON `tabSIS School Class Person`.parent = `tabSIS School Class`.name
                WHERE
                    `tabSIS Attendance Log Person`.parent = %s;
                """,
                (attendance_log["name"]),
                as_dict=True,
            )

            attendance_log["school_year"] = frappe.get_doc(
                "SIS School Year",
                attendance_log["school_year"],
            )
            attendance_log["course"] = frappe.get_doc(
                "SIS Course",
                attendance_log["course"],
            )
            attendance_log["course_class"] = frappe.get_value(
                "SIS Course Class",
                attendance_log["course_class"],
                ["name", "title", "short_title"],
                as_dict=True,
            )
            attendance_log["person_taker"] = frappe.get_value(
                "SIS Person",
                attendance_log["person_taker"],
                ["name", "full_name"],
                as_dict=True,
            )

    return attendance_logs


@frappe.whitelist()
def get_student_attendance_report(person_id, first_day, last_day):
    """
    Get first SIS Attendance Log Person of a student everyday from a date range.
    first_day and last_day must have the format YYYY-MM-DD, and first_day must be less than last_day.
    person_id must be a valid student.

    Output Example:
    [{
        "person": "fdc560f608",
        "full_name": "John Doe",
        "attendance_code": "Late",
        "reason": "Late because of traffic",
        "date": "2021-10-01",
        "school_class": "4f3b18a439",
        "school_class_title": "Class 1.1",
        "school_class_short_title": "C1.1"
    },...
    ]
    """
    # Check if person_id is a student
    try:
        student = frappe.get_doc("SIS Student", {"person": person_id})
    except frappe.exceptions.DoesNotExistError:
        frappe.throw("Not a student")

    # Verify first_day and last_day format (YYYY-MM-DD)
    try:
        datetime.strptime(first_day, "%Y-%m-%d")
        datetime.strptime(last_day, "%Y-%m-%d")
    except ValueError:
        frappe.throw("Invalid date format. Please use YYYY-MM-DD")

    # first_day must be less than last_day
    if first_day > last_day:
        frappe.throw("first_day must be less than last_day")

    # Get the first SIS Attendance Log Person of a student everyday from a date range
    attendance_logs = frappe.db.sql(
        """
        SELECT
            `tabSIS Attendance Log Person`.person,
            `tabSIS Person`.full_name,
            `tabSIS Attendance Log Person`.attendance_code,
            `tabSIS Attendance Log Person`.reason,
            `tabSIS Attendance Log School Class`.date,
            `tabSIS Attendance Log School Class`.timestamp_taken,
            `tabSIS School Class`.name AS school_class,
            `tabSIS School Class`.title AS school_class_title,
            `tabSIS School Class`.short_title AS school_class_short_title
        FROM
            `tabSIS Attendance Log Person`
            JOIN `tabSIS Person` ON `tabSIS Attendance Log Person`.person = `tabSIS Person`.name
            JOIN `tabSIS Attendance Log School Class` ON `tabSIS Attendance Log Person`.parent = `tabSIS Attendance Log School Class`.name
            JOIN `tabSIS School Class` ON `tabSIS Attendance Log School Class`.school_class = `tabSIS School Class`.name
        WHERE
            `tabSIS Attendance Log Person`.person = %s
            AND `tabSIS Attendance Log School Class`.date BETWEEN %s AND %s
        GROUP BY
            `tabSIS Attendance Log School Class`.date
        ORDER BY
            `tabSIS Attendance Log School Class`.date ASC;
        """,
        (person_id, first_day, last_day),
        as_dict=True,
    )

    return attendance_logs


@frappe.whitelist()
def get_attendance_student_summary(
    person_id, school_year_term_id=None, first_day=None, last_day=None
):
    """
    Get attendance summary for a student in a school term.

    Summary info:
    - Total number of days present
    - Total number of days late
    - Total number of days authorized absent
    - Total number of days unauthorized absent
    """
    # Check if person_id is a student
    try:
        student = frappe.get_doc("SIS Student", {"person": person_id})
    except frappe.exceptions.DoesNotExistError:
        frappe.throw("Not a student")

    # Get current school term, if not provided get the term with first_day <= today and last_day >= today
    if not school_year_term_id:
        if (not first_day) or (not last_day):
            try:
                school_year_term = frappe.get_doc(
                    "SIS School Year Term",
                    {
                        "first_day": ["<=", frappe.utils.nowdate()],
                        "last_day": [">=", frappe.utils.nowdate()],
                    },
                )
            except frappe.exceptions.DoesNotExistError:
                frappe.throw("Today is not in a school term")

            first_day = school_year_term.first_day.strftime("%Y-%m-%d")
            last_day = school_year_term.last_day.strftime("%Y-%m-%d")
            school_year_term_title = school_year_term.title
        else:
            # verify first_day and last_day format (YYYY-MM-DD)
            try:
                datetime.strptime(first_day, "%Y-%m-%d")
                datetime.strptime(last_day, "%Y-%m-%d")
                school_year_term_title = ""
            except ValueError:
                frappe.throw("Invalid date format. Please use YYYY-MM-DD")
    else:
        try:
            school_year_term = frappe.get_doc(
                "SIS School Year Term", school_year_term_id
            )
            first_day = school_year_term.first_day.strftime("%Y-%m-%d")
            last_day = school_year_term.last_day.strftime("%Y-%m-%d")
            school_year_term_title = school_year_term.title
        except frappe.exceptions.DoesNotExistError:
            frappe.throw("School year term not found")

    # Get all attendance logs for the student in the school term
    # attendance_logs = frappe.db.sql(
    #     """
    #     SELECT
    #         DISTINCT `tabSIS Attendance Log School Class`.date,
    #         `tabSIS Attendance Log Person`.person,
    #         `tabSIS Attendance Log Person`.attendance_code
    #     FROM
    #         `tabSIS Attendance Log Person`
    #         JOIN `tabSIS Attendance Log School Class` ON `tabSIS Attendance Log School Class`.name = `tabSIS Attendance Log Person`.parent
    #     WHERE
    #         `tabSIS Attendance Log Person`.person = "{person_id}"
    #         AND `tabSIS Attendance Log School Class`.date BETWEEN "{first_day}" AND "{last_day}";
    # """,
    #     {"person_id": person_id, "first_day": first_day, "last_day": last_day},
    #     as_dict=True,
    # )

    attendance_logs = frappe.get_all(
        "SIS Attendance Log Person",
        fields=["attendance_code", "person"],
        filters={
            "person": person_id,
            "creation": ["between", [first_day, last_day]],
            "parenttype": "SIS Attendance Log School Class",
        },
    )

    total_days_present = 0
    total_days_late = 0
    total_days_authorized_absent = 0
    total_days_unauthorized_absent = 0
    for attendance_log in attendance_logs:
        if attendance_log.attendance_code == "Present":
            total_days_present += 1
        elif attendance_log.attendance_code == "Late":
            total_days_late += 1
        elif attendance_log.attendance_code == "Authorized Absent":
            total_days_authorized_absent += 1
        elif attendance_log.attendance_code == "Unauthorized Absent":
            total_days_unauthorized_absent += 1

    return {
        "school_year_term": school_year_term_title,
        "first_day": first_day,
        "last_day": last_day,
        "person": person_id,
        "full_name": student.full_name,
        "present": total_days_present,
        "late": total_days_late,
        "authorized_absent": total_days_authorized_absent,
        "unauthorized_absent": total_days_unauthorized_absent,
    }


@frappe.whitelist()
def get_individual_attendance_history_by_date(person_id, date=None):
    """
    Get individual attendance history for a student by date.
    """
    # Check if person_id is a student
    try:
        student = frappe.get_doc("SIS Student", {"person": person_id})
    except frappe.exceptions.DoesNotExistError:
        frappe.throw("Not a student")

    if not date:
        date = frappe.utils.nowdate()
    else:
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            frappe.throw("Invalid date format. Please use YYYY-MM-DD")

    # Get all attendance logs for the student
    attendance_logs = frappe.get_all(
        "SIS Attendance Log Person",
        fields=["*"],
        filters={"person": person_id, "creation": ["between", [date, date]]},
        order_by="creation asc",
    )

    # attendance_logs = frappe.db.sql(
    #     """
    #     SELECT * FROM `tabSIS Attendance Log Person`
    #     WHERE
    #         `tabSIS Attendance Log Person`.person = "{person_id}"

    #     ORDER BY `tabSIS Attendance Log Person`.creation ASC;
    # """,
    #     {"person_id": person_id, "date": date},
    #     as_dict=True,
    # )

    # return attendance_logs

    if attendance_logs and len(attendance_logs) > 0:
        for attendance_log in attendance_logs:

            if attendance_log["parenttype"] == "SIS Attendance Log School Class":
                attendance_log["parent"] = frappe.get_value(
                    attendance_log["parenttype"],
                    attendance_log["parent"],
                    ["name", "school_class"],
                    as_dict=True,
                )
                attendance_log["parent"]["school_class"] = frappe.get_value(
                    "SIS School Class",
                    attendance_log["parent"]["school_class"],
                    ["name", "title", "short_title"],
                    as_dict=True,
                )
            else:
                attendance_log["parent"] = frappe.get_value(
                    attendance_log["parenttype"],
                    attendance_log["parent"],
                    ["name", "course_class", "course"],
                    as_dict=True,
                )
                attendance_log["parent"]["course_class"] = frappe.get_value(
                    "SIS Course Class",
                    attendance_log["parent"]["course_class"],
                    ["name", "title", "short_title"],
                    as_dict=True,
                )
                attendance_log["parent"]["course"] = frappe.get_doc(
                    "SIS Course", attendance_log["parent"]["course"]
                )
            attendance_log["person"] = frappe.get_doc(
                "SIS Person", attendance_log["person"]
            )

    return attendance_logs
