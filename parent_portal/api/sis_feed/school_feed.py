import frappe
from frappe.handler import upload_file
from parent_portal.sis.doctype.sis_school_year.sis_school_year import SISSchoolYear
from mimetypes import guess_type
from PIL import Image, ImageOps
import base64
import io


@frappe.whitelist(allow_guest=True)
def get_all_school_feed(
    person_id="", type="All Schools", limit=10, page=1, filters=None
):
    """
    Get all school feeds based on a person id or grade levels.

    Person ID must have primary role as Student. Person ID is prioritized over grade levels.

    `type` can be "All Schools", "High School", "Middle School", "Primary School".
    """
    # Get current academic year
    current_school_year = SISSchoolYear.get_current_school_year()

    # Verify person_id
    if person_id:
        person = frappe.get_value(
            "SIS Person", {"name": person_id}, ["name", "primary_role"], as_dict=1
        )
        if not person:
            frappe.throw("Invalid person_id")
        if person.primary_role != "Student":
            frappe.throw("Person is not a student")

        # Find grade levels that person_id is associated with
        grade_levels = frappe.db.sql(
            """
            SELECT 
                DISTINCT grade_level.sequence_number
            FROM
                `tabSIS School Class Person` class_person
                JOIN `tabSIS School Class` school_class ON class_person.parent = school_class.name
                JOIN `tabSIS School Grade Level` grade_level ON school_class.school_grade_level = grade_level.name
            WHERE class_person.person = %s
            """,
            (person_id),
            as_dict=True,
        )

        if len(grade_levels) == 0:
            frappe.throw("No grade levels found for person_id")

        # sort grade levels
        grade_levels = [grade_level.sequence_number for grade_level in grade_levels]
        grade_levels.sort()
        grade_levels = ",".join([str(grade_level) for grade_level in grade_levels])

    else:
        # Verify type
        if type not in [
            "All Schools",
            "High School",
            "Middle School",
            "Primary School",
        ]:
            frappe.throw("Invalid type")

        if type == "All Schools":
            grade_levels = ""
        elif type == "High School":
            grade_levels = "10,11,12"
        elif type == "Middle School":
            grade_levels = "6,7,8,9"
        elif type == "Primary School":
            grade_levels = "1,2,3,4,5"

    # Find list of school class and grade levels that person_id is associated with

    if filters and isinstance(filters, str):
        filters = frappe.parse_json(filters)
    else:
        filters = {}

    filters["grade_levels"] = ["like", f"%{grade_levels}%"]
    filters["school_year"] = current_school_year

    # count number of school feeds
    total_count = frappe.db.count("SIS School Feed", filters=filters)

    # pagination
    limit = int(limit)
    page = int(page)
    start = (page - 1) * limit

    school_feeds = frappe.get_all(
        "SIS School Feed",
        fields=["*"],
        filters=filters,
        limit=limit,
        start=start,
        order_by="creation desc",
    )

    if school_feeds and len(school_feeds) > 0:
        for feed in school_feeds:
            owner = feed.get("owner")
            if owner:
                feed["owner"] = frappe.get_value(
                    "PP User",
                    {"user": owner},
                    ["full_name", "user_image", "user", "person"],
                    as_dict=1,
                )

    return {
        "total_count": total_count,
        "page": page,
        "limit": limit,
        "docs": school_feeds,
    }


@frappe.whitelist(allow_guest=True)
def get_school_feed_by_id(school_feed_id):
    # TODO
    # Verify school feed exists & user permission
    current_user = frappe.session.user

    school_feed = frappe.get_doc("SIS School Feed", school_feed_id).as_dict()

    if not school_feed:
        frappe.throw("School feed not found")

    owner = school_feed["owner"]
    if owner:
        school_feed["owner"] = frappe.get_value(
            "PP User",
            {"user": owner},
            ["full_name", "user_image", "user", "person"],
            as_dict=1,
        )

    return school_feed
