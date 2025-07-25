# Copyright (c) 2024, Digital Learning Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta


class SISTimetableSchedulingTool(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        first_day: DF.Date
        last_day: DF.Date
        reschedule: DF.Check
        school_year_term: DF.Link | None
        timetable: DF.Link
    # end: auto-generated types

    @frappe.whitelist()
    def tie_days_to_dates(self):
        """
        Given self.first_day and self.last_day, return a list of dates between the two dates.
        The list must start with the first Monday before the first day and end with the fist Friday after the last day.
        """
        first_day = self.first_day
        last_day = self.last_day

        # Convert to datetime objects if they are not already
        if isinstance(first_day, str):
            first_day = datetime.strptime(first_day, "%Y-%m-%d")
        if isinstance(last_day, str):
            last_day = datetime.strptime(last_day, "%Y-%m-%d")

        # Get the first Monday before the first day
        if first_day.weekday() == 0:
            first_monday = first_day
        else:
            first_monday = first_day - timedelta(days=first_day.weekday())

        if last_day.weekday() == 4:
            last_friday = last_day
        else:
            last_friday = last_day + timedelta(days=(4 - last_day.weekday() + 7) % 7)
        print(first_day, last_day, first_monday, last_friday)

        # Get the dates between the two dates
        dates = []
        current_date = first_day
        while current_date <= last_day:
            dates.append(current_date)
            current_date += timedelta(days=1)

        # Get timetable days from the timetable
        timetable = frappe.get_doc("SIS Timetable", self.timetable)
        timetable_days = timetable.timetable_days

        if len(timetable_days) == 0:
            frappe.throw("No timetable days found in the timetable")

        # if reschedule is True, delete all existing records in the SIS Timetable Day Date table which has timetable day ids in the timetable_days
        if self.reschedule:
            frappe.db.sql(
                f"DELETE FROM `tabSIS Timetable Day Date` WHERE timetable_day IN ({','.join(['%s']*len(timetable_days))})",
                tuple([timetable_day.name for timetable_day in timetable_days]),
            )

        # Map timetable days to dates.
        # Each timetable day object has a weekday property which is within ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        # tie_days_to_dates is an array of object {"timetable_day": "timetable_day_id", "date": "date}
        # The weekday of the timetable day should match the weekday of the date
        tie_days_to_dates = []
        for timetable_day in timetable_days:
            for date in dates:
                if timetable_day.weekday == date.strftime("%a"):
                    tie_days_to_dates.append(
                        {
                            "timetable_day": timetable_day.name,
                            "timetable_day_title": timetable_day.title,
                            "date": date,
                            "weekday": date.strftime("%a"),
                        }
                    )

        # Save tie_days_to_dates to the SIS Timetable Day Date table
        schedule_errors = []
        scheduled_dates = []

        for tie_day_to_date in tie_days_to_dates:
            # Check if the record already exists
            if not frappe.db.exists(
                "SIS Timetable Day Date",
                {
                    "timetable_day": tie_day_to_date["timetable_day"],
                    "date": tie_day_to_date["date"],
                },
            ):
                frappe.get_doc(
                    {
                        "doctype": "SIS Timetable Day Date",
                        "timetable_day": tie_day_to_date["timetable_day"],
                        "date": tie_day_to_date["date"],
                    }
                ).insert()
                scheduled_dates.append(
                    f"{tie_day_to_date['timetable_day_title']} on {tie_day_to_date['weekday']} {tie_day_to_date['date']}"
                )
            else:
                schedule_errors.append(
                    f"Record already exists for {tie_day_to_date['timetable_day_title']} on {tie_day_to_date['weekday']} {tie_day_to_date['date']}"
                )
        # Convert the dates to string date only, not include time
        # dates = [date.strftime("%Y-%m-%d") for date in dates]

        return dict(scheduled_dates=scheduled_dates, schedule_errors=schedule_errors)
