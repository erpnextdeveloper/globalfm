// Copyright (c) 2016, BJJ and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Project Wise Timesheet"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": dateutil.add_days(dateutil.get_today(), -30),
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": dateutil.get_today(),
			"reqd": 1
		},
		{
			"fieldname":"project",
			"label": __("Project"),
			"fieldtype": "Link",
			"options":"Project"
		},
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options":"Employee"
		}

	]
}
