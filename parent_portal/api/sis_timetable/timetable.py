import frappe
from parent_portal.sis.doctype.sis_school_year.sis_school_year import SISSchoolYear

from datetime import datetime, timedelta


@frappe.whitelist()
def get_individual_timetable(person_id: str, type: str, start_date=None):
    """
    Get individual timetable for a person.
    - person_id: str: The person ID.
    - type: str: The type of the request:
      - CHILD: The current user is a guardian and want to see the timetable of their child.
      - SELF: The current user is a student/teacher and want to see their timetable.
      - ADMIN: The current user is an administrator and want to see the timetable of a person.
    - start_date: str: The start monday date of the timetable (format e.g. 2024-10-24). Default is None then it will be monday of the current week.
    """
    if type.upper() == "CHILD":
        # Get the child's timetable
        return get_child_timetable(person_id, start_date)
    elif type.upper() == "SELF":
        # Get the current user's timetable
        return get_self_timetable(person_id, start_date)
    elif type.upper() == "ADMIN":
        # Get the person's timetable
        return get_timetable_by_person_id(person_id, start_date)
    else:
        frappe.throw("Invalid type")


def get_child_timetable(person_id: str, start_date=None):
    """
    Get the child's timetable.
    - person_id: str: The child's person ID.
    """
    # TODO
    # Check if the current user is the guardian of the child

    # Get the child's timetable
    get_timetable_by_person_id(person_id, start_date)


def get_self_timetable(person_id: str, start_date=None):
    """
    Get the current user's timetable.
    """
    # TODO
    # Check if the current user has the same person ID

    # Get the current user's timetable
    get_timetable_by_person_id(person_id, start_date)


def get_timetable_by_person_id(person_id: str, start_date=None):
    """
    Get the timetable of a person.
    - person_id: str: The person ID.
    - start_date: str: The start monday date of the timetable (format e.g. 2024-10-24). Default is None then it will be monday of the current week.
    """
    # Get current School Year
    current_school_year = SISSchoolYear.get_current_school_year()

    # Determine the start monday date of the timetable
    if not start_date:
        start_date = datetime.now().date()
        start_date = start_date - timedelta(days=start_date.weekday())
    else:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        start_date = start_date - timedelta(days=start_date.weekday())

    # Determine the end friday date of the timetable
    end_date = start_date + timedelta(days=4)

    # Determine date range from start_date to end_date to use in SQL query
    date_range = [start_date + timedelta(days=i) for i in range(5)]
    date_range = [date.strftime("%Y-%m-%d") for date in date_range]

    # Fetch the timetable the person is involved in
    involved_timetables = frappe.db.sql(
        """
        SELECT DISTINCT `tabSIS Timetable`.name, `tabSIS Timetable`.title, `tabSIS Timetable`.short_title 
        FROM `tabSIS Timetable` 
        JOIN `tabSIS Timetable Day` ON (`tabSIS Timetable`.name=`tabSIS Timetable Day`.parent) 
        JOIN `tabSIS Timetable Day Row Class` ON (`tabSIS Timetable Day Row Class`.timetable_day=`tabSIS Timetable Day`.name) 
        JOIN `tabSIS Course Class` ON (`tabSIS Timetable Day Row Class`.parent=`tabSIS Course Class`.name) 
        JOIN `tabSIS Course Class Person` ON (`tabSIS Course Class Person`.parent=`tabSIS Course Class`.name) 
        WHERE `tabSIS Course Class Person`.person=%s 
        AND `tabSIS Timetable`.school_year=%s;
    """,
        (person_id, current_school_year),
    )

    rowPeriods = frappe.db.sql(
        """
    SELECT 
        `tabSIS Timetable Day`.name AS ttDayID,
        `tabSIS Timetable Day`.title AS ttDayTitle,
        `tabSIS Timetable Day`.weekday AS ttDayWeekday,
        `tabSIS Timetable Column Row`.name AS ttColumnRowID,
        `tabSIS Timetable Column Row`.type AS ttColumnRowType,
        `tabSIS Timetable Day Row Class`.name AS ttDayRowClassID, 
        `tabSIS Timetable Column Row`.title AS rowTitle, 
        `tabSIS Timetable Column Row`.short_title AS rowShortTitle, 
        `tabSIS Timetable Column Row`.time_start AS timeStart, 
        `tabSIS Timetable Column Row`.time_end AS timeEnd,
        `tabSIS Timetable Day Date`.date AS date,
        `tabSIS Course Class`.name AS courseClassID, 
        `tabSIS Course`.name AS courseID, 
        `tabSIS Course`.title AS courseTitle, 
        `tabSIS Course`.short_title AS courseShortTitle, 
        `tabSIS Course Class`.title AS courseClassTitle, 
        `tabSIS Course Class`.short_title AS courseClassShorTitle
    FROM 
        `tabSIS Course` 
        JOIN `tabSIS Course Class` ON (`tabSIS Course`.name = `tabSIS Course Class`.course) 
        JOIN `tabSIS Course Class Person` ON (`tabSIS Course Class`.name = `tabSIS Course Class Person`.parent) 
        JOIN `tabSIS Timetable Day Row Class` ON (`tabSIS Course Class`.name = `tabSIS Timetable Day Row Class`.parent) 
        JOIN `tabSIS Timetable Column Row` ON (`tabSIS Timetable Day Row Class`.timetable_column_row = `tabSIS Timetable Column Row`.name)
        JOIN `tabSIS Timetable Day` ON (`tabSIS Timetable Day Row Class`.timetable_day = `tabSIS Timetable Day`.name)
        JOIN `tabSIS Timetable Day Date` ON (`tabSIS Timetable Day`.name = `tabSIS Timetable Day Date`.timetable_day)
        JOIN `tabSIS Timetable` ON (`tabSIS Timetable Day`.parent = `tabSIS Timetable`.name)
    WHERE 
        `tabSIS Course Class Person`.person = %s AND
        `tabSIS Timetable Day Date`.date IN %s AND
        `tabSIS Timetable`.school_year = %s
    GROUP BY `tabSIS Timetable Day Row Class`.name 
    ORDER BY `tabSIS Timetable Column Row`.time_start, `tabSIS Timetable Column Row`.time_end, FIND_IN_SET(`tabSIS Course Class Person`.role, 'Teacher,Assistant,Student') DESC
    """,
        (person_id, date_range, current_school_year),
        as_dict=True,
    )
    return {
        "periods": rowPeriods,
        "timetables": involved_timetables,
        "date_range": date_range,
    }

    # # Get the person's timetable by execute a SQL query
    # timetable = frappe.db.sql(
    #     """
    #     SELECT
    #         gibbonTTDayRowClass.gibbonTTDayID,
    #         gibbonTTDayRowClass.gibbonTTDayRowClassID,
    #         gibbonTTColumnRow.gibbonTTColumnRowID,
    #         gibbonCourseClass.gibbonCourseClassID,
    #         gibbonTTColumnRow.name,
    #         gibbonTTColumnRow.nameShort,
    #         gibbonCourse.gibbonCourseID,
    #         gibbonCourse.nameShort AS course,
    #         gibbonCourseClass.nameShort AS class,
    #         gibbonCourse.gibbonYearGroupIDList,
    #         gibbonTTColumnRow.timeStart,
    #         gibbonTTColumnRow.timeEnd
    #     FROM
    #         gibbonCourse
    #         JOIN gibbonCourseClass ON (gibbonCourse.gibbonCourseID=gibbonCourseClass.gibbonCourseID)
    #         JOIN gibbonCourseClassPerson ON (gibbonCourseClass.gibbonCourseClassID=gibbonCourseClassPerson.gibbonCourseClassID)
    #         JOIN gibbonTTDayRowClass ON (gibbonCourseClass.gibbonCourseClassID=gibbonTTDayRowClass.gibbonCourseClassID)
    #         JOIN gibbonTTColumnRow ON (gibbonTTDayRowClass.gibbonTTColumnRowID=gibbonTTColumnRow.gibbonTTColumnRowID)
    #         LEFT JOIN gibbonSpace ON (gibbonTTDayRowClass.gibbonSpaceID=gibbonSpace.gibbonSpaceID)
    #         LEFT JOIN gibbonStaffCoverageDate ON (gibbonStaffCoverageDate.foreignTableID=gibbonTTDayRowClass.gibbonTTDayRowClassID AND gibbonStaffCoverageDate.foreignTable='gibbonTTDayRowClass' AND gibbonStaffCoverageDate.date=:date)
    #         LEFT JOIN gibbonStaffCoverage ON (gibbonStaffCoverageDate.gibbonStaffCoverageID=gibbonStaffCoverage.gibbonStaffCoverageID)
    #     WHERE
    #         gibbonTTDayID=:gibbonTTDayID
    #         AND gibbonCourseClassPerson.gibbonPersonID=:gibbonPersonID
    #     GROUP BY gibbonTTDayRowClass.gibbonTTDayRowClassID
    #     ORDER BY timeStart, timeEnd, FIND_IN_SET(gibbonCourseClassPerson.role, 'Teacher,Assistant,Student') DESC
    #     """,
    #     person_id,
    #     as_dict=True,
    # )
