import frappe
from frappe.handler import upload_file
from parent_portal.sis.doctype.sis_school_year.sis_school_year import SISSchoolYear

from mimetypes import guess_type
from PIL import Image, ImageOps
import base64
import io
from datetime import datetime


@frappe.whitelist(allow_guest=True)
def get_all_class_feed(person_id="", limit=10, page=1, filters=None):
    # TODO
    # Verify person_id
    # Find list of school class and grade levels that person_id is associated with

    current_school_year = SISSchoolYear.get_current_school_year()

    if filters and isinstance(filters, str):
        filters = frappe.parse_json(filters)

    or_filters = None

    if person_id:
        # Verify person_id
        person = frappe.get_value("SIS Person", {"name": person_id}, ["name"])
        if not person:
            frappe.throw("Invalid person_id")

        or_filters = []

        # Find class feeds of all course class that person_id is associated with
        course_classes = frappe.db.sql(
            """
            SELECT `tabSIS Course Class`.name
            FROM `tabSIS Course Class Person`
            JOIN `tabSIS Course Class` ON `tabSIS Course Class`.name = `tabSIS Course Class Person`.parent
            WHERE `tabSIS Course Class Person`.person = %(person_id)s
            AND `tabSIS Course Class`.school_year = %(current_school_year)s;
            """,
            {"person_id": person_id, "current_school_year": current_school_year},
            as_dict=1,
        )
        course_classes = [course_class["name"] for course_class in course_classes]

        if len(course_classes) > 0:
            or_filters.append(["course_class", "in", course_classes])

        school_classes = frappe.db.sql(
            """
            SELECT `tabSIS School Class`.name
            FROM 
                `tabSIS School Class Person`
                JOIN `tabSIS School Class` ON `tabSIS School Class`.name = `tabSIS School Class Person`.parent
            WHERE 
                `tabSIS School Class Person`.person = %(person_id)s
                AND `tabSIS School Class`.school_year = %(current_school_year)s;
            """,
            {"person_id": person_id, "current_school_year": current_school_year},
            as_dict=1,
        )
        school_classes = [school_class["name"] for school_class in school_classes]

        if len(school_classes) > 0:
            or_filters.append(["school_class", "in", school_classes])

        if len(or_filters) == 0:
            return {
                "total_count": 0,
                "page": page,
                "limit": limit,
                "docs": [],
            }
        elif len(or_filters) == 1:
            filters = [or_filters[0]]
            or_filters = None
        else:
            filters = None

    # pagination
    limit = int(limit)
    page = int(page)
    start = (page - 1) * limit
    
    # count number of class feeds
    if not or_filters:
        total_count = frappe.db.count("SIS Class Feed", filters=filters)

    else:
        total_count = frappe.db.count(
            "SIS Class Feed", filters=[or_filters[0]]
        ) + frappe.db.count("SIS Class Feed", filters=[or_filters[1]])

    class_feeds = frappe.get_all(
        "SIS Class Feed",
        fields=["*"],
        filters=filters,
        or_filters=or_filters,
        limit=limit,
        start=start,
        order_by="creation desc",
    )

    # return filters, or_filters

    if class_feeds and len(class_feeds) > 0:
        for feed in class_feeds:
            feed["attachments"] = frappe.get_all(
                "File",
                filters={
                    "attached_to_name": feed["name"],
                    "attached_to_doctype": "SIS Class Feed",
                },
                fields=["name", "file_url"],
            )
            owner = feed.get("owner")
            if owner:
                feed["owner"] = frappe.get_value(
                    "PP User",
                    {"user": owner},
                    ["full_name", "user_image", "user", "person"],
                    as_dict=1,
                )
            if feed["school_class"]:
                feed["school_class"] = frappe.get_value(
                    "SIS School Class",
                    feed["school_class"],
                    ["name", "title", "short_title"],
                    as_dict=True,
                )
            if feed["course_class"]:
                feed["course_class"] = frappe.get_value(
                    "SIS Course Class",
                    feed["course_class"],
                    ["name", "title", "short_title"],
                    as_dict=True,
                )

    return {
        "total_count": total_count,
        "page": page,
        "limit": limit,
        "docs": class_feeds,
    }


@frappe.whitelist(allow_guest=True)
def get_class_feed_by_id(class_feed_id):
    class_feed = frappe.get_doc("SIS Class Feed", class_feed_id).as_dict()

    if not class_feed:
        frappe.throw("Class feed not found")

    owner = class_feed["owner"]
    if owner:
        class_feed["owner"] = frappe.get_value(
            "PP User",
            {"user": owner},
            ["full_name", "user_image", "user", "person"],
            as_dict=1,
        )
    class_feed["attachments"] = frappe.get_all(
        "File",
        filters={
            "attached_to_name": class_feed_id,
            "attached_to_doctype": "SIS Class Feed",
        },
        fields=["name", "file_url"],
    )

    return class_feed


@frappe.whitelist(methods=["POST"])
def create_class_feed(doc):
    # TODO
    # Check permission of current user

    # Verify public_time
    if "public_time" not in doc:
        doc["public_time"] = frappe.utils.now()
    else:
        try:
            doc["public_time"] = datetime.strptime(
                doc["public_time"], "%Y-%m-%d %H:%M:%S"
            )
        except ValueError:
            frappe.throw(
                "Invalid date format for public_time. Please use YYYY-MM-DD HH:MM:SS"
            )

    doc = frappe.parse_json(doc)

    class_feed = frappe.new_doc("SIS Class Feed")
    class_feed.update(doc)
    class_feed.save(ignore_permissions=True)

    return class_feed


def upload_JPEG_wrt_EXIF(content, filename):
    """
    When a user uploads a JPEG file, we need to transpose the image based on the EXIF data.
    This is because the image is rotated when it is uploaded to the server.
    """
    content_type = guess_type(filename)[0]

    # if file format is JPEG, we need to transpose the image
    if content_type.startswith("image/jpeg"):
        with Image.open(io.BytesIO(content)) as image:
            # transpose the image
            transposed_image = ImageOps.exif_transpose(image)
            #  convert the image to bytes
            buffer = io.BytesIO()
            # save the image to the buffer
            transposed_image.save(buffer, format="JPEG")
            # get the value of the buffer
            buffer = buffer.getvalue()
    else:
        buffer = base64.b64decode(content)

    return frappe.get_doc(
        {
            "doctype": "File",
            "file_name": filename,
            "content": buffer,
            "attached_to_doctype": "SIS Class Feed",
            "attached_to_name": frappe.form_dict.docname,
            "is_private": 0,
            # "attached_to_field": "photo",
        }
    ).insert()


@frappe.whitelist(methods=["POST"])
def upload_class_feed_photo():
    """
    Upload an image with class feed data.
    """
    fileExt = ["jpg", "JPG", "jpeg", "JPEG", "png", "PNG", "gif", "GIF", "webp", "WEBP"]

    frappe.form_dict.doctype = "SIS Class Feed"
    frappe.form_dict.fieldname = "file"
    frappe.form_dict.docname = frappe.form_dict.class_feed_id
    frappe.form_dict.is_private = 0

    files = frappe.request.files
    if "file" in files:
        file = files["file"]
        filename = file.filename
        """
        If the file is a JPEG, we need to transpose the image
        Else, we need to upload the file as is
        """
        if filename.endswith(".jpeg"):
            content = file.stream.read()
            file_doc = upload_JPEG_wrt_EXIF(content, filename)
        elif filename.endswith(tuple(fileExt)):
            file_doc = upload_file()

        else:
            frappe.throw("Invalid file format")
    else:
        return {"message": "No file uploaded"}

    return {"message": "success", "file_url": file_doc.file_url}


# Version 1 upload to child table
# @frappe.whitelist()
# def upload_class_feed_photo():
#     """
#     Upload an image with class feed data.
#     """
#     fileExt = ["jpg", "JPG", "jpeg", "JPEG", "png", "PNG", "gif", "GIF", "webp", "WEBP"]

#     frappe.form_dict.doctype = "SIS Class Feed Photo"
#     frappe.form_dict.fieldname = "photo"

#     class_feed_photo_doc = frappe.new_doc("SIS Class Feed Photo")
#     class_feed_photo_doc.parent = frappe.form_dict.class_feed_id
#     class_feed_photo_doc.parenttype = "SIS Class Feed"
#     class_feed_photo_doc.parentfield = "photos"
#     class_feed_photo_doc.photo = "_"
#     class_feed_photo_doc.insert()
#     frappe.form_dict.docname = class_feed_photo_doc.name

#     files = frappe.request.files
#     if "file" in files:
#         file = files["file"]
#         filename = file.filename
#         """
#         If the file is a JPEG, we need to transpose the image
#         Else, we need to upload the file as is
#         """
#         if filename.endswith(".jpeg"):
#             content = file.stream.read()
#             file_doc = upload_JPEG_wrt_EXIF(content, filename)
#         elif filename.endswith(tuple(fileExt)):
#             file_doc = upload_file()
#         else:
#             frappe.throw("Invalid file format")

#     class_feed_photo_doc.photo = file_doc.file_url
#     class_feed_photo_doc.save()

#     return class_feed_photo_doc
