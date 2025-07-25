// Copyright (c) 2024, Digital Learning Team and contributors
// For license information, please see license.txt

frappe.ui.form.on("SIS Course Class", {
  get_participants: function (frm) {
    if (frm.doc.get_from == "School Class") {
      if (!frm.doc.from_school_class) {
        frappe.msgprint("Please select School Class");
        return;
      }
    }
    if (frm.doc.get_from == "Grade Level") {
      if (!frm.doc.from_grade_level) {
        frappe.msgprint("Please select Grade Level");
        return;
      }
    }

    frappe.dom.freeze("Fetching Participants...");
    frm
      .call("get_participants")
      .then((r) => {
        frappe.dom.unfreeze();
        if (r.message) {
          let count = 0;
          $.each(r.message, function (i, d) {
            // add participants to the table if person id not exists
            if (!frm.doc.participants.find((p) => p.person == d.person)) {
              const row = frm.add_child("participants");
              row.person = d.person;
              row.role = d.role;
              count += 1;
            }
          });
          frm.refresh_field("participants");
          frappe.msgprint(`${count} Participants added`);
        }
      })
      .fail((r) => {
        frappe.dom.unfreeze();
        frappe.msgprint("Failed to fetch participants", r);
      });
  },
  onload: function (frm) {
    frm.fields_dict["timetable_day_row_class"].grid.get_field(
      "timetable_day"
    ).get_query = function (doc) {
      return {
        filters: {
          parent: doc.timetable,
        },
      };
    };
    frm.fields_dict["timetable_day_row_class"].grid.get_field(
      "timetable_column_row"
    ).get_query = function (doc, cdt, cdn) {
      const row = locals[cdt][cdn];
      return {
        filters: {
          parent: row.timetable_column,
        },
      };
    };
  },
});

frappe.ui.form.on("SIS Timetable Day Row Class", {
  timetable_day: function (frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    frm
      .call("get_timetable_column", {
        timetable_day: row.timetable_day,
      })
      .then((r) => {
        console.log("child table updated - timetable_column:", r.message);
        row.timetable_column = r.message;
        frm.refresh_field("timetable_day_row_class");
      });
  },
});
