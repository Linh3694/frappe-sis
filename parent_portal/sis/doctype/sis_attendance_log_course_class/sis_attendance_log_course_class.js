// Copyright (c) 2024, Digital Learning Team and contributors
// For license information, please see license.txt

function extractID(str) {
  const match = str.match(/\(([^)]+)\)$/);
  if (match && match.length > 1) {
    return match[1]; // Returns the ID inside the parentheses
  }
  return null; // Return null if no match is found
}

function getPeriodsOptions(frm) {
  if (!frm.doc.course_class) return;

  frappe.db.get_doc("SIS Course Class", frm.doc.course_class).then((res) => {
    const students = res.participants
      .filter((person) => person.role === "Student")
      .map((person) => ({
        person: person.person,
        attendance_code: "Present",
      }));
    frm.set_value("student_list", students);

    const periods = res.timetable_day_row_class.map((row) => ({
      name: row.name,
      timetable_day: row.timetable_day,
      timetable_column_row: row.timetable_column_row,
      title: row.title,
    }));
    // frm.set_value("timetable", periods);
    frm.set_df_property(
      "period",
      "options",
      periods.map((p) => `${p.title} (${p.name})`)
    );

    frm.set_value("school_year", res.school_year);
    frm.set_value("course", res.course);

    frm.trigger("hide_features");
    frm.refresh();
  });
}

frappe.ui.form.on("SIS Attendance Log Course Class", {
  school_year(frm) {
    frm.set_query("course_class", function () {
      return {
        filters: {
          school_year: frm.doc.school_year,
          course: frm.doc.course,
        },
      };
    });
  },
  course(frm) {
    frm.set_query("course_class", function () {
      return {
        filters: {
          school_year: frm.doc.school_year,
          course: frm.doc.course,
        },
      };
    });
  },
  course_class(frm) {
    getPeriodsOptions(frm);
  },
  period(frm) {
    if (!frm.doc.period) return;
    // read the id inside parenthesis at the end of the string
    const period_id = extractID(frm.doc.period);
    if (!period_id) return;
    frm.set_value("timetable_day_row_class", period_id);
    frm.refresh();
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

    // frm.fields_dict["timetable"].grid.wrapper.on(
    //   "click",
    //   ".grid-row-check",
    //   function () {
    //     var selected_rows = frm.fields_dict["timetable"].grid.get_selected();
    //     if (selected_rows.length > 1) {
    //       frappe.msgprint(__("Only one row can be selected at a time."));
    //       $(this).prop("checked", false);
    //     } else {
    //       frm.set_value("timetable_day_row_class", selected_rows[0].name);
    //     }
    //   }
    // );
  },
});
