// Copyright (c) 2024, Digital Learning Team and contributors
// For license information, please see license.txt

function generateGradeLevelsString(grade_levels_str, to_added_grade_levels) {
  if (!grade_levels_str) {
    return to_added_grade_levels.sort((a, b) => a - b).join(",");
  }

  grade_levels = grade_levels_str.split(",").map((x) => Number(x.trim()));
  // add school grades, remove duplicate and sort
  grade_levels = grade_levels.concat(to_added_grade_levels);
  grade_levels = grade_levels.filter((x, i, a) => a.indexOf(x) == i);

  // sort grade levels ascending
  grade_levels = grade_levels.sort((a, b) => a - b);

  return grade_levels.join(",");
}

function removeGradeLevelsString(grade_levels_str, to_removed_grade_levels) {
  grade_levels = grade_levels_str.split(",").map((x) => Number(x.trim()));
  // remove school grades and sort
  grade_levels = grade_levels.filter(
    (x) => !to_removed_grade_levels.includes(x)
  );
  return grade_levels.sort().join(",");
}

frappe.ui.form.on("SIS School Feed", {
  to_all_schools: function (frm) {
    if (frm.doc.to_all_schools == 1) {
      frm.set_value("to_primary_school", 1);
      frm.set_value("to_middle_school", 1);
      frm.set_value("to_high_school", 1);
      frm.set_df_property("grade_levels", "read_only", 1);
    } else {
      frm.set_value("to_primary_school", 0);
      frm.set_value("to_middle_school", 0);
      frm.set_value("to_high_school", 0);
      frm.set_df_property("grade_levels", "read_only", 0);
    }
  },
  to_primary_school: function (frm) {
    primary_grade_levels = [1, 2, 3, 4, 5];
    if (frm.doc.to_primary_school == 1) {
      grade_levels = generateGradeLevelsString(
        frm.doc.grade_levels,
        primary_grade_levels
      );
      frm.set_value("grade_levels", grade_levels);
    } else {
      grade_levels = removeGradeLevelsString(
        frm.doc.grade_levels,
        primary_grade_levels
      );
      frm.set_value("grade_levels", grade_levels);
    }
  },
  to_middle_school: function (frm) {
    middle_grade_levels = [6, 7, 8, 9];
    if (frm.doc.to_middle_school == 1) {
      grade_levels = generateGradeLevelsString(
        frm.doc.grade_levels,
        middle_grade_levels
      );
      frm.set_value("grade_levels", grade_levels);
    } else {
      grade_levels = removeGradeLevelsString(
        frm.doc.grade_levels,
        middle_grade_levels
      );
      frm.set_value("grade_levels", grade_levels);
    }
  },
  to_high_school: function (frm) {
    high_grade_levels = [10, 11, 12];
    if (frm.doc.to_high_school == 1) {
      grade_levels = generateGradeLevelsString(
        frm.doc.grade_levels,
        high_grade_levels
      );
      frm.set_value("grade_levels", grade_levels);
    } else {
      grade_levels = removeGradeLevelsString(
        frm.doc.grade_levels,
        high_grade_levels
      );
      frm.set_value("grade_levels", grade_levels);
    }
  },
});
