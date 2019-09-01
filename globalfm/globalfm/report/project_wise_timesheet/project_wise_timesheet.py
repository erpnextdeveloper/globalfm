# Copyright (c) 2013, BJJ and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import formatdate, getdate

def execute(filters=None):
	columns = [
		_("Project") + ":Link/Project:120",
		_("Timesheet") + ":Link/Timesheet:120",
		_("Employee") + ":Link/Employee:120",
		_("Employee Name") + ":Data:120",
		_("Activity") + ":Link/Activity Type:100",
		_("Hours") + ":Float:120",
		_("From Time") + ":Datetime:120",
		_("To Time") + ":Datetime:120"
	]
	if getdate(filters.get("from_date"))>getdate(filters.get("to_date")):
		frappe.throw(_("From Date Must Less Than To Date"))
	cond=' and p.docstatus=1'
	if filters.get("project"):
		cond += " and pd.project='%s'"%(filters.get("project"))
	if filters.get("employee"):
		cond += " and p.employee='%s'"%(filters.get("employee"))
	
	data = frappe.db.sql("""SELECT pd.project,
       p.name,
       p.employee,
       p.employee_name,
       pd.activity_type,
       pd.hours,
       pd.from_time,
       pd.to_time
FROM   `tabTimesheet` AS p
       INNER JOIN `tabTimesheet Detail` AS pd
               ON p.name = pd.parent where p.end_date between '%s' and '%s'%s  
		"""%(filters.get('from_date'), filters.get("to_date"),cond), as_list=True)

	return columns, data
