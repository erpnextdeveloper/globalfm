from __future__ import unicode_literals
import frappe
from frappe.utils import cint, get_gravatar, format_datetime, now_datetime,add_days,today,formatdate,date_diff,getdate,get_last_day,flt
from frappe import throw, msgprint, _
from frappe.desk.reportview import get_match_cond, get_filters_cond
from frappe.utils.password import update_password as _update_password
from erpnext.controllers.accounts_controller import get_taxes_and_charges
from frappe.desk.notifications import clear_notifications
from frappe.utils.user import get_system_managers
import frappe.permissions
import frappe.share
import re
import string
import random
import json
import time
from datetime import datetime
from datetime import date
from datetime import timedelta
import collections
import math
import logging
from frappe.client import delete
import traceback
import urllib
import urllib2
from erpnext.accounts.utils import get_fiscal_year
from collections import defaultdict



@frappe.whitelist()
def app_error_log(title,error):
	d = frappe.get_doc({
			"doctype": "Custom Error Log",
			"title":str("User:")+str(title),
			"error":traceback.format_exc()
		})
	d = d.insert(ignore_permissions=True)
	return d


@frappe.whitelist()
def employee_sync(name):
	import requests
	from requests.auth import HTTPBasicAuth
	company_sync(name)
	url = 'http://178.128.176.191/gfm/api/employee/get_all_employees'
	payload = {}
	params = {
	  'x-api-key': 'CODEX@123',
	  'Content-Type': 'application/x-www-form-urlencoded'
	}
	user_details=validate_login(name)
	#frappe.errprint(user_details[1])
	response = requests.get(url, headers = params,auth=HTTPBasicAuth(str(user_details[0]),user_details[1]))
	result=response.json()
	if result["status"]==False:
		frappe.throw("Invalid Login Details")
	else:
		if len(result["data"]):
			frappe.errprint(result["data"])
			add_employee(result["data"])

@frappe.whitelist()
def company_sync(name):
	import requests
	from requests.auth import HTTPBasicAuth
	url = 'http://178.128.176.191/gfm/api/company/get_all_companies'
	payload = {}
	params = {
	  'x-api-key': 'CODEX@123',
	  'Content-Type': 'application/x-www-form-urlencoded'
	}
	user_details=validate_login(name)
	#frappe.errprint(user_details[1])
	response = requests.get(url, headers = params,auth=HTTPBasicAuth(str(user_details[0]),user_details[1]))
	result=response.json()
	if result["status"]==False:
		frappe.throw("Invalid Login Details")
	else:
		if len(result["data"]):
			add_company(name,result["data"])
			
		

def validate_login(name):
	usr=frappe.db.get_value("Employee Synchronization Setting",name,"user_id")
	pwd=frappe.db.get_value("Employee Synchronization Setting",name,"password")
	if not usr:
		frappe.throw("Uses id is mandatory")

	if not pwd:
		frappe.throw("Password is mandatory")
	return (usr,pwd)

@frappe.whitelist()
def add_employee(data):
	for row in data:
		if row["Department"]:
			frappe.msgprint(str(row["Department"]))
			make_department(row["Department"])
		if row["Designation"]:
			make_designation(row["Designation"])
		if row["Branch_Name"]:
			make_branch(row["Branch_Name"])
		make_employee(row)
	frappe.msgprint("Employee Sync Succefully")

def make_employee(data):
	emp_data=frappe.get_all("Employee",filters={"employee_number":data["Employee_ID"]},fields=["name"])
	if emp_data:
		employee=frappe.get_doc("Employee",data["Employee_ID"])
		employee.first_name=data["first_name"] if not data["first_name"]==None else ''
		employee.last_name=data["last_name"] if not data["last_name"]==None else ''
		employee.gender=data["Gender"] if not data["Gender"]==None else ''
		employee.date_of_joining=data["Date_of_Joining"] if not data["Date_of_Joining"]==None else ''
		employee.date_of_birth=data["Date_of_Birth"] if not data["Date_of_Birth"]==None else ''
		employee.employee_number=data["Employee_ID"] if not data["Employee_ID"]==None else ''
		employee.custom_user_id=data["user_id"] if not data["user_id"]==None else ''
		employee.personal_email=data["Email"] if not data["Email"]==None else ''
		employee.cell_number=data["Contact_Number"] if not data["Contact_Number"]==None else ''
		employee.permanent_address=data["Address"] if not data["Address"]==None else ''
		employee.marital_status=data["Marital_Status"] if not data["Marital_Status"]==None else ''
		employee.department=get_erp_dept_name(data["Department"]) if not data["Department"]==None else ''
		employee.designation=data["Designation"] if not data["Designation"]==None else ''
		employee.office_shift=data["Office_Shift"] if not data["Office_Shift"]==None else ''
		employee.shoun_file_no=data["Shoun_File_No"] if not data["Shoun_File_No"]==None else ''
		employee.arabic_name=data["Arabic_Name"] if not data["Arabic_Name"]==None else ''
		employee.reference_no=data["Reference_No"] if not data["Reference_No"]==None else ''
		employee.file_no=data["File_No"] if not data["File_No"]==None else ''
		employee.religion=data["Religion"] if not data["Religion"]==None else ''
		employee.nationality=data["Nationality"] if not data["Nationality"]==None else ''
		employee.passport_type=data["Passport_Type"] if not data["Passport_Type"]==None else ''
		employee.passport_nationality=data["Passport_Nationality"] if not data["Passport_Nationality"]==None else ''
		employee.branch=data["Branch_Name"] if not data["Branch_Name"]==None else ''
		employee.place_of_issue=data["Place_Of_Issue"] if not data["Place_Of_Issue"]==None else ''
		employee.first_time_in_kuwait=data["First_time_in_Kuwait"] if not data["First_time_in_Kuwait"]==None else ''
		employee.blood_group=data["Blood_Group"] if not data["Blood_Group"]==None else ''
		employee.visa_type=data["Visa_Type"] if not data["Visa_Type"]==None else ''
		employee.contract_years=data["Contract_Years"] if not data["Contract_Years"]==None else ''
		employee.driving_license_type=data["Driving_License_Type"] if not data["Driving_License_Type"]==None else ''
		employee.allowance_type=data["Allowance_Type"] if not data["Allowance_Type"]==None else ''
		employee.allowance=data["Allowance"] if not data["Allowance"]==None else ''
		employee.save(ignore_permissions=True)
	else:	
		employee=frappe.get_doc(dict(
			doctype="Employee",
			company=data["Company"] if not data["Company"]==None else '',
			first_name=data["first_name"] if not data["first_name"]==None else '',
			last_name=data["last_name"] if not data["last_name"]==None else '',
			gender=data["Gender"] if not data["Gender"]==None else '',
			date_of_joining=data["Date_of_Joining"] if not data["Date_of_Joining"]==None else '',
			date_of_birth=data["Date_of_Birth"] if not data["Date_of_Birth"]==None else '',
			employee_number=data["Employee_ID"] if not data["Employee_ID"]==None else '',
			custom_user_id=data["user_id"] if not data["user_id"]==None else '',
			personal_email=data["Email"] if not data["Email"]==None else '',
			cell_number=data["Contact_Number"] if not data["Contact_Number"]==None else '',
			permanent_address=data["Address"] if not data["Address"]==None else '',
			marital_status=data["Marital_Status"] if not data["Marital_Status"]==None else '',
			department=get_erp_dept_name(data["Department"]) if not data["Department"]==None else '',
			designation=data["Designation"] if not data["Designation"]==None else '',
			office_shift=data["Office_Shift"] if not data["Office_Shift"]==None else '',
			shoun_file_no=data["Shoun_File_No"] if not data["Shoun_File_No"]==None else '',
			arabic_name=data["Arabic_Name"] if not data["Arabic_Name"]==None else '',
			reference_no=data["Reference_No"] if not data["Reference_No"]==None else '',
			file_no=data["File_No"] if not data["File_No"]==None else '',
			religion=data["Religion"] if not data["Religion"]==None else '',
			nationality=data["Nationality"] if not data["Nationality"]==None else '',
			passport_type=data["Passport_Type"] if not data["Passport_Type"]==None else '',
			passport_nationality=data["Passport_Nationality"] if not data["Passport_Nationality"]==None else '',
			branch=data["Branch_Name"] if not data["Branch_Name"]==None else '',
			place_of_issue=data["Place_Of_Issue"] if not data["Place_Of_Issue"]==None else '',
			first_time_in_kuwait=data["First_time_in_Kuwait"] if not data["First_time_in_Kuwait"]==None else '',
			blood_group=data["Blood_Group"] if not data["Blood_Group"]==None else '',
			visa_type=data["Visa_Type"] if not data["Visa_Type"]==None else '',
			contract_years=data["Contract_Years"] if not data["Contract_Years"]==None else '',
			driving_license_type=data["Driving_License_Type"] if not data["Driving_License_Type"]==None else '',
			allowance_type=data["Allowance_Type"] if not data["Allowance_Type"]==None else '',
			allowance=data["Allowance"] if not data["Allowance"]==None else ''
		)).insert(ignore_permissions=True)


def add_company(name,data):
	p_company=frappe.db.get_value("Employee Synchronization Setting",name,"parent_company")
	currency=frappe.db.get_value("Company",p_company,"default_currency")
	for row in data:
		make_company(row,p_company,currency)
	frappe.msgprint("Company Sync Successfully")

def make_company(data,p_company,currency):
	cmp_data=frappe.get_all("Company",filters={"company_id":data["Company_Id"]},fields=["name"])
	if cmp_data:
		company=frappe.get_doc("Company",cmp_data[0].name)
		company.company_id=data["Company_Id"] if not data["Company_Id"]==None else ''
		company.company_name=data["Company_Name"] if not data["Company_Name"]==None else ''
		company.legal_trading_name=data["Legal/Trading_Name"] if not data["Legal/Trading_Name"]==None else ''
		company.registration_details=data["Registration_Number"] if not data["Registration_Number"]==None else ''
		company.phone_no=data["Contact_Number"] if not data["Contact_Number"]==None else ''
		company.email=data["Email"] if not data["Email"]==None else ''
		company.website=data["Website"] if not data["Website"]==None else ''
		company.tax_id=data["Tax_Number/EIN"] if not data["Tax_Number/EIN"]==None else ''
		company.file_no=data["File_No"] if not data["File_No"]==None else ''
		company.arabic_name=data["Arabic_Name"] if not data["Arabic_Name"]==None else ''
		company.social_insurance_no=data["Social_Insurance_No"] if not data["Social_Insurance_No"]==None else ''
		company.reference_no=data["Reference_No"] if not data["Reference_No"]==None else ''
		company.business_activity=data["Business_Activity"] if not data["Business_Activity"]==None else ''
		company.ministry_agreement_no=data["Ministry/Agreement_No"] if not data["Ministry/Agreement_No"]==None else ''
		company.sponsor_name=data["Sponsor_Name"] if not data["Sponsor_Name"]==None else ''
		company.sponsor_designation=data["Sponsor_Designation"] if not data["Sponsor_Designation"]==None else ''
		company.english_desired_activity=data["English_Desired_Activity"] if not data["English_Desired_Activity"]==None else ''
		company.arabic_desired_activity=data["Arabic_Desired_Activity"] if not data["Arabic_Desired_Activity"]==None else ''
		company.english_contract_name=data["English_Contract_Name"] if not data["English_Contract_Name"]==None else ''
		company.arabic_contract_name=data["Arabic_Contract_Name"] if not data["Arabic_Contract_Name"]==None else ''
		company.contract_civilid_no=data["Contract_CivilId_No"] if not data["Contract_CivilId_No"]==None else ''
		company.save(ignore_permissions=True)
	else:
		cmp_doc=frappe.get_doc(dict(
			doctype="Company",
			company_id=data["Company_Id"] if not data["Company_Id"]==None else '',
			company_name=data["Company_Name"] if not data["Company_Name"]==None else '',
			legal_trading_name=data["Legal/Trading_Name"] if not data["Legal/Trading_Name"]==None else '',
			abbr=data["Company_Id"] if not data["Company_Id"]==None else '',
			registration_details=data["Registration_Number"] if not data["Registration_Number"]==None else '',
			phone_no=data["Contact_Number"] if not data["Contact_Number"]==None else '',
			email=data["Email"] if not data["Email"]==None else '',
			website=data["Website"] if not data["Website"]==None else '',
			tax_id=data["Tax_Number/EIN"] if not data["Tax_Number/EIN"]==None else '',
			file_no=data["File_No"] if not data["File_No"]==None else '',
			arabic_name=data["Arabic_Name"] if not data["Arabic_Name"]==None else '',
			social_insurance_no=data["Social_Insurance_No"] if not data["Social_Insurance_No"]==None else '',
			reference_no=data["Reference_No"] if not data["Reference_No"]==None else '',
			business_activity=data["Business_Activity"] if not data["Business_Activity"]==None else '',
			ministry_agreement_no=data["Ministry/Agreement_No"] if not data["Ministry/Agreement_No"]==None else '',
			sponsor_name=data["Sponsor_Name"] if not data["Sponsor_Name"]==None else '',
			sponsor_designation=data["Sponsor_Designation"] if not data["Sponsor_Designation"]==None else '',
			english_desired_activity=data["English_Desired_Activity"] if not data["English_Desired_Activity"]==None else '',
			arabic_desired_activity=data["Arabic_Desired_Activity"] if not data["Arabic_Desired_Activity"]==None else '',
			english_contract_name=data["English_Contract_Name"] if not data["English_Contract_Name"]==None else '',
			arabic_contract_name=data["Arabic_Contract_Name"] if not data["Arabic_Contract_Name"]==None else '',
			contract_civilid_no=data["Contract_CivilId_No"] if not data["Contract_CivilId_No"]==None else '',
			parent_company=p_company,
			default_currency=currency		
		)).insert(ignore_permissions=True)		
		



@frappe.whitelist()
def make_department(name):
	department=frappe.db.get_all("Department",filters={'custom_department_id':name},fields=["name"])
	if department:
		return True
	else:
		department_doc=frappe.get_doc(dict(
			doctype="Department",
			department_name=name,
			custom_department_id=name,
			parent_department='All Departments'
		)).insert(ignore_permissions=True)
		return department_doc


def get_erp_dept_name(name):
	department=frappe.db.get_all("Department",filters={'custom_department_id':name},fields=["name"])
	if department:
		return department[0].name
	else:
		return False




def make_designation(name):
	designation=frappe.db.get_value("Designation",name,"name")
	if designation:
		return True
	else:
		designation_doc=frappe.get_doc(dict(
			doctype="Designation",
			designation_name=name
		)).insert(ignore_permissions=True)
		return designation_doc



def make_branch(name):
	branch=frappe.db.get_value("Branch",name,"name")
	if branch:
		return True
	else:
		if name=="Branch":
			branch_doc=frappe.get_doc(dict(
				doctype="Branch",
				branch="Branch1"
			)).insert(ignore_permissions=True)
			return branch_doc
		else:
			branch_doc=frappe.get_doc(dict(
				doctype="Branch",
				branch=name
			)).insert(ignore_permissions=True)
			return branch_doc
	

@frappe.whitelist()
def update_employee_sync(name):
	emp_data=frappe.get_all("Employee",filters={"status":"Active"},fields=["name"])
	if emp_data:
		for row in emp_data:
			update_employee(name,row.name)
		frappe.msgprint("Employee Updated Successfully")
	



@frappe.whitelist()
def update_employee(name,emp_name):
	doc=frappe.get_doc("Employee",emp_name)
	if doc.custom_user_id:
		import requests
		from requests.auth import HTTPBasicAuth
		url = 'http://178.128.176.191/gfm/api/employee/update_employee'
		payload = {}
		params = {
		  'x-api-key': 'CODEX@123',
		  'Content-Type': 'application/x-www-form-urlencoded'
		}
		user_details=validate_login(name)
		data={}
		data["user_id"]=doc.custom_user_id
		data["first_name"]=doc.first_name
		data["last_name"]=doc.last_name
		data["employee_id"]=doc.employee_number
		data["email"]=doc.personal_email
		data["company_id"]=frappe.db.get_value("Company",doc.company,"company_id")
		data["date_of_birth"]=doc.date_of_birth
		data["date_of_joining"]=doc.date_of_joining
		data["gender"]=doc.gender
		data["marital_status"]=doc.marital_status
		data["contact_no"]=doc.cell_number
		data["address"]=doc.permanent_address
		data["erp_department"]=doc.department
		data["erp_designation"]=doc.designation
		data["erp_shift"]=doc.office_shift
		data["shoun_file_no"]=doc.shoun_file_no
		data["arabic_name"]=doc.arabic_name
		data["ref_no"]=doc.reference_no
		data["file_no"]=doc.file_no
		data["religion"]=doc.religion
		data["nationality"]=doc.nationality
		data["allowance_type"]=doc.allowance_type
		data["allowance"]=doc.allowance
		data["passport_type"]=doc.passport_type
		data["passport_nationality"]=doc.passport_nationality
		data["branch_name"]=doc.branch
		data["issue_place"]=doc.place_of_issue
		data["first_time_kuwait"]=doc.first_time_in_kuwait
		data["blood_group"]=doc.blood_group
		data["visa_type"]=doc.visa_type
		data["contract_years"]=doc.contract_years
		data["driving_license_type"]=doc.driving_license_type

		#frappe.errprint(user_details[1])
		response = requests.post(url, headers = params,data=data,auth=HTTPBasicAuth(user_details[0],user_details[1]))
		result=response.json()
		frappe.errprint(result)
		if result["status"]==False:
			frappe.throw("Invalid Login Details")

@frappe.whitelist()
def add_attendance(self,method):
	if self.time_logs:
		att_details=[]
		in_time=''
		out_time=''
		att_hour=''
		flag=False
		for row in self.time_logs:
			if self.designation==row.designation:
				flag=True
				in_time=row.from_time
				out_time=row.to_time
				if flt(row.hours)>=8 and flt(row.hours)<12:
					att_hour=8
				if flt(row.hours)>=12 and flt(row.hours)<16:
					att_hour=12
				if flt(row.hours)>=16:
					att_hour=16
		
			else:
				att_details_json={}
				att_details_json["activity_type"]=row.activity_type
				att_details_json["in_time"]=row.from_time
				att_details_json["out_time"]=row.to_time
				att_details_json["hour"]=row.hours
				if flt(row.hours)>=8 and flt(row.hours)<12:
					att_details_json["attendance_hour"]=8
				if flt(row.hours)>=12 and flt(row.hours)<16:
					att_details_json["attendance_hour"]=12
				if flt(row.hours)>=16:
					att_details_json["attendance_hour"]=16
				att_details.append(att_details_json)
		attendance_doc=frappe.get_doc(dict(
			doctype="Attendance",
			employee=self.employee,
			company=self.company,
			employee_name=self.employee_name,
			department=self.department,
			attendance_date=getdate(self.start_date),
			items=att_details,
			timesheet=self.name,
			in_time=in_time,
			out_time=out_time,
			attendance_hour=att_hour
		)).insert(ignore_permissions=True)

			
	

