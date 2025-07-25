import frappe
import random


def generate_grade_level(grade_number):
    return {
        "doctype": "SIS School Grade Level",
        "title": f"Grade {grade_number}",
        "short_title": f"G{grade_number}",
        "sequence_number": grade_number,
    }


def generate_school_class(grade_number, class_number, school_year):
    return {
        "doctype": "SIS School Class",
        "title": f"Class {grade_number}.{class_number}",
        "short_title": f"{grade_number}.{class_number}",
        "school_grade_level": f"Grade {grade_number}",
        "school_year": school_year,
    }


def generate_person(
    person_type: str,
    sequence_number: int,
    family_number: int,
):
    return {
        "doctype": f"SIS Person",
        "first_name": f"{person_type} {sequence_number}",
        "last_name": f"{family_number}",
        "email": f"{person_type.lower()}{sequence_number}@yupmail.com",
        "gender": "Male" if random.random() > 0.5 else "Female",
        "date_of_birth": frappe.utils.datetime.datetime.strptime(
            f"{random.randint(1, 28)}-{random.randint(1, 12)}-{random.randint(1980, 2005)}",
            "%d-%m-%Y",
        ),
        "nationality": "Vietnam",
    }


school_year = {
    "doctype": "SIS School Year",
    "title": "2024-2025",
    "first_day": frappe.utils.datetime.datetime.strptime("19-08-2024", "%d-%m-%Y"),
    "last_day": frappe.utils.datetime.datetime.strptime("31-05-2025", "%d-%m-%Y"),
    "status": "Current",
}
grade_levels = [generate_grade_level(x) for x in range(1, 13)]
school_classes = [
    generate_school_class(grade_number, class_number, school_year["title"])
    for grade_number in range(1, 13)
    for class_number in range(1, 4)
]
person = []


def execute():
    print("PARENT PORTAL: Seeding data...")
    if not frappe.conf.developer_mode:
        print("Can only seed data in developer mode.")
        return
    school_year["name"] = insert_school_year(school_year).name
    for grade_level in grade_levels:
        grade_level["name"] = insert_grade_level(grade_level).name
    for school_class in school_classes:
        school_class["name"] = insert_school_class(school_class).name


def delete_all(doctype):
    if frappe.conf.developer_mode:
        frappe.db.sql(f"DELETE FROM `tab{doctype}`")
    else:
        print(f"Can only delete {doctype} records in developer mode.")


def save_doc(doctype, data, filters):
    docs = frappe.get_all(doctype, filters=filters)
    if docs:
        doc = frappe.get_doc(doctype, docs[0].name)
        for key, value in data.items():
            if key != "doctype":
                doc.set(key, value)
        doc.save()
        frappe.db.commit()
        return doc
    else:
        return frappe.get_doc(data).insert(ignore_permissions=True)


def insert_school_year(data):
    return save_doc("SIS School Year", data, {"title": data["title"]})


def insert_grade_level(data):
    return save_doc("SIS School Grade Level", data, {"title": data["title"]})


def insert_school_class(data):
    data["school_year"] = school_year["name"]
    data["school_grade_level"] = frappe.db.get_value(
        "SIS School Grade Level", {"title": data["school_grade_level"]}, "name"
    )
    return save_doc("SIS School Class", data, {"title": data["title"]})


def main():
    print("Hello, world!")
