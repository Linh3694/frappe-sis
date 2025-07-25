// Copyright (c) 2024, Digital Learning Team and contributors
// For license information, please see license.txt

// frappe.ui.form.on("SIS Guardian Registry", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("SIS Guardian Registry",  {
    refresh: function (frm) {
		if (!frm.is_new() && frm.doc.status == 'New') {
            frm.add_custom_button(__("Accept"),
                function () {
                    frm.trigger("action_accept_registry");
                },
                // __("Actions")
            );
            frm.add_custom_button(
                __("Deny"),
                function () {
                    frm.trigger("action_deny_registry");
                },
                // __("Actions")
            );
        }
    },

	action_accept_registry: function (frm) {
		frappe.call({
			method: "parent_portal.sis.doctype.sis_guardian_registry.sis_guardian_registry.process_accept",
			args: {
				name: frm.doc.name,
			},
			callback: function (r) {
				if (!r.exc) {
					if (r.message) {
						frappe.msgprint(r.message);
					}
				}
			},
		});
	},

    action_deny_registry: function (frm) {
		var d = new frappe.ui.Dialog({
			title: __("Deny registration"),
			fields: [
				{
					label: "Reason",
					fieldname: "reason",
					fieldtype: "Small Text",
					reqd: 1,
				},
			],
			primary_action: function () {
				var data = d.get_values();
				frappe.call({
					method: "parent_portal.sis.doctype.sis_guardian_registry.sis_guardian_registry.process_deny",
					args: {
						in_reason: data.reason,
						name: frm.doc.name,
					},
					callback: function (r) {
						if (!r.exc) {
							if (r.message) {
								frappe.msgprint(r.message);
							}
							d.hide();
						}
					},
				});
			},
			primary_action_label: __("Submit"),
		});
		d.show();
	},
})