// Copyright (c) 2024, Digital Learning Team and contributors
// For license information, please see license.txt

frappe.ui.form.on("SIS Timetable Scheduling Tool", {
  setup(frm) {
    // fetch timetable days on changing value of timetable
    frm.add_fetch("timetable", "timetable_days", "timetable_days");
    frm.add_fetch("timetable", "title", "timetable_title");
  },
  refresh(frm) {
    frm.disable_save();

    frm.page.set_primary_action(__("Schedule Timetable"), () => {
      if (!frm.doc.first_day || !frm.doc.last_day) {
        frappe.msgprint(__("Please select date range for scheduling"));
        return;
      }

      frappe.dom.freeze(__("Scheduling..."));
      frm
        .call("tie_days_to_dates")
        .then((r) => {
          frappe.dom.unfreeze();
          if (r.message) {
            const { schedule_errors, scheduled_dates } = r.message;
            const scheduled_dates_html = scheduled_dates
              .map((d) => `<tr><td>${d}</td></tr>`)
              .join("");
            const schedule_errors_html = schedule_errors
              .map((d) => `<tr><td>${d}</td></tr>`)
              .join("");

            const result_html = `
            <h3>${scheduled_dates.length} Scheduled Dates - ${schedule_errors.length} Errors</h3>
            <table class="table table-bordered">
              <thead>
                <tr>
                  <th>Scheduled Dates</th>
                </tr>
              </thead>
              <tbody>
                ${scheduled_dates_html}
              </tbody>
            </table>

            <table class="table table-bordered">
              <thead>
                <tr>
                  <th>Errors</th>
                </tr>
              </thead>
              <tbody>
                ${schedule_errors_html}
              </tbody>
            </table>
            `;

            frappe.msgprint(result_html, __("Scheduling Result"));
          }
          // frappe.msgprint("Hello", __("Scheduling Result"));
        })
        .fail(() => {
          frappe.dom.unfreeze();
          frappe.msgprint(__("Scheduling failed"));
        });
    });
  },
});
