// Copyright (c) 2024, Digital Learning Team and contributors
// For license information, please see license.txt

frappe.ui.form.on("SIS Attendance Log School Class", {
  school_year(frm) {
    frm.set_query("school_class", function () {
      return {
        filters: {
          school_year: frm.doc.school_year,
        },
      };
    });
  },
  school_class(frm) {
    if (!frm.doc.school_class) return;

    frappe.db.get_doc("SIS School Class", frm.doc.school_class).then((res) => {
      const students = res.participants
        .filter((person) => person.role === "Student")
        .map((person) => ({
          person: person.person,
          attendance_code: "Present",
        }));

      frm.set_value("student_list", students);
      frm.set_value("school_year", res.school_year);

      frm.trigger("hide_features");
      frm.refresh();
    });
  },
  onload(frm) {
    frappe.db
      .get_value("PP User", { user: frappe.session.user }, ["*"])
      .then((r) => {
        if (r.message && r.message.person) {
          frappe.utils.add_link_title(
            "SIS Person",
            r.message.person,
            r.message.full_name
          );
          frm.set_value("person_taker", r.message.person);
        } else {
          frappe.msgprint(
            __("User {0} is not linked to a person", [frappe.session.user])
          );
          frm.disable_save();
        }
      });
  },
  refresh(frm) {
    frm.set_df_property("student_list", "cannot_add_rows", true);
    frm.set_df_property("student_list", "cannot_delete_rows", true);
    frm.set_df_property("student_list", "cannot_delete_all_rows", true);
  },
});
