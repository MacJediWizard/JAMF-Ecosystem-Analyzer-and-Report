#!/usr/bin/env python3

##########################################################################################
# General Information
##########################################################################################
#
#	Script created By William Grzybowski March 3, 2022
#
#	Version 2.0	- Initial Creation of Script.
#
#	This script take User Imput and will call the JAMF API and get all Information 
#	related to a Policy.
#	It looks up all policies and then returns an Excel spreadsheet.
#
#	Fields returned in csv / Excel are as follows below:
#
#
#	Policy Record Type
#	
#	Policy ID
#	Policy Name
#	Policy Category ID
#	Policy Category Name
#	
#	Policy Target All Computers
#	
#	Policy Target Computer ID
#	Policy Target Computer Name
#	
#	Policy Target Group ID
#	Policy Target Group Name
#	Policy Target Group is Smart
#	
#	Policy Exclusion Computer ID
#	Policy Exclusion Computer Name
#	
#	Policy Exclusion Group id
#	Policy Exclusion Group Name
#	Policy Exclusion Group is Smart
#	
#	Policy Package ID
#	Policy Package Name
#	Policy Package Category Name
#	Policy Package Filename
#	
#	Policy Script ID
#	Policy Script Name
#	Policy Script Category Name
#	Policy Script Filename
#	
#	Configuration Profile ID
#	Configuration Profile Type
#	Configuration Profile Name
#	
#	Configuration Profile Category ID
#	Configuration Profile Category Name
#	
#	Configuration Profile Target Computer ID
#	Configuration Profile Target Computer Name
#	
#	Configuration Profile Target Group ID
#	Configuration Profile Target Group Name
#	Configuration Profile Target Group is Smart
#	
#	Configuration Profile Exclusion Computer id
#	Configuration Profile Exclusion Computer Name
#
#	Configuration Profile Exclusion Group id
#	Configuration Profile Exclusion Group Name
#	Configuration Profile Exclusion Group is Smart
#
#
#
#	The only requirement is that you have Python3 on the device. All other libraries
#	the script will look for them and download if they are not found.
#
#	Run from terminal and answer the 3 fields. URL, API Username, API Password.
#
#
##########################################################################################


##########################################################################################
# License information
##########################################################################################
#
#	Copyright (c) 2022 William Grzybowski
#
#	Permission is hereby granted, free of charge, to any person obtaining a copy
#	of this software and associated documentation files (the "Software"), to deal
#	in the Software without restriction, including without limitation the rights
#	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#	copies of the Software, and to permit persons to whom the Software is
#	furnished to do so, subject to the following conditions:
#
#	The above copyright notice and this permission notice shall be included in all
#	copies or substantial portions of the Software.
#
#	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#	OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#	SOFTWARE.
#
##########################################################################################


##########################################################################################
# Imports
##########################################################################################
import os, sys, time, getpass

from os.path import exists


# For Using the Requests Library with the API
try:
	import requests
except ImportError:
	os.system('pip3 install requests')
	time.sleep(3)
	import requests
	
from requests.auth import HTTPBasicAuth


#For CSV processing with Pandas Library
try:
	import pandas as pd
except ImportError:
	os.system('pip3 install pandas')
	time.sleep(3)
	import pandas as pd
	

#For xlsx processing with openpyxl Library
try:
	import openpyxl
except ImportError:
	os.system('pip3 install openpyxl')
	time.sleep(3)
	import openpyxl
	

#For xlsx processing with xlsxwriter Library
try:
	import xlsxwriter
except ImportError:
	os.system('pip3 install xlsxwriter')
	time.sleep(3)
	import xlsxwriter


##########################################################################################
# Variables
##########################################################################################
#Set Variable for the Data	
dataToCsvPolicy = []
dataToCsvConfigurationProfile = []


#To check User login in JAMF API
get_JAMF_URL_User_Test = "/JSSResource/accounts/username/"


##########################################################################################
# Functions
##########################################################################################
#Check for Yes or no answer from input
def getYesOrNoInput(prompt):
	while True:
		try:
			value = input(prompt)
		except ValueError:
			print("Sorry, I didn't understand that.")
			continue
		
		if value.lower() != 'yes' and value.lower() != 'no':
			print("Sorry, your response must be yes or no only.")
			continue
		else:
			break
	return value


#Merge Dictionaries
def MergePolicyInfo(dict1, dict2, dict3, dict4, dict5, dict6):
	result = dict1 | dict2 | dict3 | dict4 | dict5 | dict6
	return result


def MergeConfigProfileInfo(dict1, dict2, dict3):
	result = dict1 | dict2 | dict3
	return result


#Check User Input for URL, Username, and Password
def JAMFInfoCheck(url, username, password):
	try:
		response = requests.request("GET", url, headers={"accept": "application/json"}, auth = HTTPBasicAuth(username, password))
		if response.status_code == 200:
			return print(f"User Input is OK, we can connect to JAMF API, Moving on.\n\n")
		else:
			raise SystemExit(f"User Input is NOT OK, we cannot connect to JAMF API and now will EXIT! status_code: {response.status_code}\n\n")
			
	#Exception
	except requests.exceptions.RequestException as e:
		# print URL with Erors
		raise SystemExit(f"User Input is NOT OK, we cannot connect to JAMF API and now will EXIT! \nErr: {e}")



##########################################################################################
# Get User Input
##########################################################################################
#Get User input
get_JAMF_URL = input("Enter your JAMF Instance URL: ")
get_JAMF_API_Username = input("Enter your JAMF Instance API Username: ")
get_JAMF_API_Password = getpass.getpass("Enter your JAMF Instance API Password: ")

#Check User Input for URL, Username, and Password
JAMFInfoCheck((get_JAMF_URL+get_JAMF_URL_User_Test+get_JAMF_API_Username), get_JAMF_API_Username, get_JAMF_API_Password)


get_JAMF_Policy_Info = getYesOrNoInput("Do you want to include JAMF Policy Info in Report? (yes or no): ")
get_JAMF_Configuration_Profile_Info = getYesOrNoInput("Do you want to include JAMF Configuration Profile Info in Report? (yes or no): ")


##########################################################################################
# JAMF API information
##########################################################################################
JAMF_url = get_JAMF_URL
username = get_JAMF_API_Username
password = get_JAMF_API_Password


headers = {
	'accept': 'application/json',
}


##########################################################################################
# Core Script
##########################################################################################
# Get Jamf Policy Info
if get_JAMF_Policy_Info == ("yes"):
	
	#Get Policy Info
	print("Including JAMF Policy Info.\n\n")
	includePolicyInfo = "yes"
	
	
	#Get Policy Self Service Elements
	get_JAMF_Policy_Info_SelfService = getYesOrNoInput("Do you want to include JAMF Policy Self Service Info in Report? (yes or no): ")
	if get_JAMF_Policy_Info_SelfService == ("yes"):
		
		print("Including Self Service Data.\n\n")
		
		includeSelfServiceInfo = "yes"
		
	elif get_JAMF_Policy_Info_SelfService == ("no"):
		
		print("Not Including Self Service Data.\n\n")
		
		includeSelfServiceInfo = "no"
		
		
	#Get Policy Targets
	get_JAMF_Policy_Info_Targets = getYesOrNoInput("Do you want to include JAMF Policy Target Info in Report? (yes or no): ")
	if get_JAMF_Policy_Info_Targets == ("yes"):
		
		print("Including Target Data.\n\n")
		
		includeTargetsInfo = "yes"
		
	elif get_JAMF_Policy_Info_Targets == ("no"):
		
		print("Not Including Target Data.\n\n")
		
		includeTargetsInfo = "no"
		
		
	#Get Policy Exclusions
	get_JAMF_Policy_Info_Exclusions = getYesOrNoInput("Do you want to include JAMF Policy Exclusions Info in Report? (yes or no): ")
	if get_JAMF_Policy_Info_Exclusions == ("yes"):
		
		print("Including Exclusions Data.\n\n")
		
		includeExclusionsInfo = "yes"
		
	elif get_JAMF_Policy_Info_Exclusions == ("no"):
		
		print("Not Including Exclusions Data.\n\n")
		
		includeExclusionsInfo = "no"
		
		
	#Get Policy Package Elements
	get_JAMF_Policy_Info_Packages = getYesOrNoInput("Do you want to include JAMF Policy Packages Info in Report? (yes or no): ")
	if get_JAMF_Policy_Info_Packages == ("yes"):
		
		print("Including Package Data.\n\n")
		
		includePackagesInfo = "yes"
		
	elif get_JAMF_Policy_Info_Packages == ("no"):
		
		print("Not Including Package Data.\n\n")
		
		includePackagesInfo = "no"
		
		
	#Get Policy Script Elements
	get_JAMF_Policy_Info_Scripts = getYesOrNoInput("Do you want to include JAMF Policy Scripts Info in Report? (yes or no): ")
	if get_JAMF_Policy_Info_Scripts == ("yes"):
		
		print("Including Scripts Data.\n\n")
		
		includeScriptsInfo = "yes"
		
	elif get_JAMF_Policy_Info_Scripts == ("no"):
		
		print("Not Including Scripts Data.\n\n")
		
		includeScriptsInfo = "no"
		
		
elif get_JAMF_Policy_Info == ("no"):
	
	includePolicyInfo = "no"
	
	
# Get Configuration Profile Info
if get_JAMF_Configuration_Profile_Info == ("yes"):
	
	#Get Configuration Profile Info
	print("Including Configuration Profile Info.\n\n")
	
	includeConfigurationProfileInfo = "yes"
	
	#Get Policy Targets
	get_JAMF_Configuration_Profile_Info_Targets = getYesOrNoInput("Do you want to include JAMF Configuration Profile Target Info in Report? (yes or no): ")
	if get_JAMF_Configuration_Profile_Info_Targets == ("yes"):
		
		print("Including Target Data.\n\n")
		
		includeConfigurationProfileTargetsInfo = "yes"
		
	elif get_JAMF_Configuration_Profile_Info_Targets == ("no"):
		
		print("Not Including Target Data.\n\n")
		
		includeConfigurationProfileTargetsInfo = "no"
		
		
	#Get Policy Exclusions
	get_JAMF_Configuration_Profile_Info_Exclusions = getYesOrNoInput("Do you want to include JAMF Configuration Profile Exclusions Info in Report? (yes or no): ")
	if get_JAMF_Configuration_Profile_Info_Exclusions == ("yes"):
		
		print("Including Exclusions Data.\n\n")
		
		includeConfigurationProfileExclusionsInfo = "yes"
		
	elif get_JAMF_Configuration_Profile_Info_Exclusions == ("no"):
		
		print("Not Including Exclusions Data.\n\n")
		
		includeConfigurationProfileExclusionsInfo = "no"
		
		
elif get_JAMF_Configuration_Profile_Info == ("no"):
	
	includeConfigurationProfileInfo = "no"
	
	
#Check Options set and desplay message to user
if get_JAMF_Policy_Info == 'yes' or get_JAMF_Configuration_Profile_Info == 'yes':
	
	print("Running Request Report Now.\n\n")
	
	# Set Variables for Dict for Policy Info
	dataToCVS_JAMF_Policy_Info = "{'Type':'',\
	\
	'Policy ID':'',\
	\
	'Policy Name':'',\
	\
	'Policy Category ID':'',\
	\
	'Policy Category Name':''}"
	
	
	dataToCVS_JAMF_Policy_SelfService_Info = "{'Policy In SelfService':'',\
	\
	'Policy In SelfService Name':''}"
	
	
	dataToCVS_JAMF_Policy_Target_Info = "{'Policy Target All Computers':'',\
	\
	'Policy Target Computer ID':'',\
	\
	'Policy Target Computer Name':'',\
	\
	'Policy Target Group ID':'',\
	\
	'Policy Target Group Name':'',\
	\
	'Policy Target Group is Smart':''}"
	
	
	dataToCVS_JAMF_Policy_Exclusion_Info = "{'Policy Exclusion Computer ID':'',\
	\
	'Policy Exclusion Computer Name':'',\
	\
	'Policy Exclusion Group id':'',\
	\
	'Policy Exclusion Group Name':'',\
	\
	'Policy Exclusion Group is Smart':''}"
	
	
	dataToCVS_JAMF_Policy_Packages_Info = "{'Policy Package ID':'',\
	\
	'Policy Package Name':'',\
	\
	'Policy Package Category Name':'',\
	\
	'Policy Package Filename':''}"
	
	
	dataToCVS_JAMF_Policy_Scripts_Info = "{'Policy Script ID':'',\
	\
	'Policy Script Name':'',\
	\
	'Policy Script Category Name':'',\
	\
	'Policy Script Filename':''}"
	
	
	# Set Variables for Dict for Configuration Profile Info
	dataToCVS_JAMF_Configuration_Profile_Info = "{'Configuration Profile ID':'',\
	\
	'Configuration Profile Type':'',\
	\
	'Configuration Profile Name':'',\
	\
	'Configuration Profile Category ID':'',\
	\
	'Configuration Profile Category Name':''}"
	
	
	dataToCVS_JAMF_Configuration_Profile_Target_Info = "{'Configuration Profile Target Computer ID':'',\
	\
	'Configuration Profile Target Computer Name':'',\
	\
	'Configuration Profile Target Group ID':'',\
	\
	'Configuration Profile Target Group Name':'',\
	\
	'Configuration Profile Target Group is Smart':''}"
	
	
	dataToCVS_JAMF_Configuration_Profile_Exclusion_Info = "{'Configuration Profile Exclusion Computer id':'',\
	\
	'Configuration Profile Exclusion Computer Name':'',\
	\
	'Configuration Profile Exclusion Group id':'',\
	\
	'Configuration Profile Exclusion Group Name':'',\
	\
	'Configuration Profile Exclusion Group is Smart':''}"
	
	
	# Set Variables for Dict for Policy Info Empty
	dataToCVS_JAMF_Policy_Info_Empty = "{'Type':'',\
	\
	'Policy ID':'',\
	\
	'Policy Name':'',\
	\
	'Policy Category ID':'',\
	\
	'Policy Category Name':''}"
	
	
	dataToCVS_JAMF_Policy_SelfService_Info_Empty = "{'Policy In SelfService':'',\
	\
	'Policy In SelfService Name':''}"
	
	
	dataToCVS_JAMF_Policy_Target_Info_Empty = "{'Policy Target All Computers':'',\
	\
	'Policy Target Computer ID':'',\
	\
	'Policy Target Computer Name':'',\
	\
	'Policy Target Group ID':'',\
	\
	'Policy Target Group Name':'',\
	\
	'Policy Target Group is Smart':''}"
	
	
	dataToCVS_JAMF_Policy_Exclusion_Info_Empty = "{'Policy Exclusion Computer ID':'',\
	\
	'Policy Exclusion Computer Name':'',\
	\
	'Policy Exclusion Group id':'',\
	\
	'Policy Exclusion Group Name':'',\
	\
	'Policy Exclusion Group is Smart':''}"
	
	
	dataToCVS_JAMF_Policy_Packages_Info_Empty = "{'Policy Package ID':'',\
	\
	'Policy Package Name':'',\
	\
	'Policy Package Category Name':'',\
	\
	'Policy Package Filename':''}"
	
	
	dataToCVS_JAMF_Policy_Scripts_Info_Empty = "{'Policy Script ID':'',\
	\
	'Policy Script Name':'',\
	\
	'Policy Script Category Name':'',\
	\
	'Policy Script Filename':''}"
	
	
	# Set Variables for Dict for Configuration Profile Info
	dataToCVS_JAMF_Configuration_Profile_Info_Empty = "{'Configuration Profile ID':'',\
	\
	'Configuration Profile Type':'',\
	\
	'Configuration Profile Name':'',\
	\
	'Configuration Profile Category ID':'',\
	\
	'Configuration Profile Category Name':''}"
	
	
	dataToCVS_JAMF_Configuration_Profile_Target_Info_Empty = "{'Configuration Profile Target Computer ID':'',\
	\
	'Configuration Profile Target Computer Name':'',\
	\
	'Configuration Profile Target Group ID':'',\
	\
	'Configuration Profile Target Group Name':'',\
	\
	'Configuration Profile Target Group is Smart':''}"
	
	
	dataToCVS_JAMF_Configuration_Profile_Exclusion_Info_Empty = "{'Configuration Profile Exclusion Computer id':'',\
	\
	'Configuration Profile Exclusion Computer Name':'',\
	\
	'Configuration Profile Exclusion Group id':'',\
	\
	'Configuration Profile Exclusion Group Name':'',\
	\
	'Configuration Profile Exclusion Group is Smart':''}"
	
	
	
	# Take Variables and make them a Empty Dict
	JAMF_Policy_Info = eval(dataToCVS_JAMF_Policy_Info)
	JAMF_Policy_SelfService_Info = eval(dataToCVS_JAMF_Policy_SelfService_Info)
	JAMF_Policy_Target_Info = eval(dataToCVS_JAMF_Policy_Target_Info)
	JAMF_Policy_Exclusion_Info = eval(dataToCVS_JAMF_Policy_Exclusion_Info)
	JAMF_Policy_Packages_Info = eval(dataToCVS_JAMF_Policy_Packages_Info)
	JAMF_Policy_Scripts_Info = eval(dataToCVS_JAMF_Policy_Scripts_Info)
	JAMF_Configuration_Profile_Info = eval(dataToCVS_JAMF_Configuration_Profile_Info)
	JAMF_Configuration_Profile_Target_Info = eval(dataToCVS_JAMF_Configuration_Profile_Target_Info)
	JAMF_Configuration_Profile_Exclusion_Info = eval(dataToCVS_JAMF_Configuration_Profile_Exclusion_Info)
	
	
	# Take Variables and make them a Empty Dict
	JAMF_Policy_Info_Empty = eval(dataToCVS_JAMF_Policy_Info_Empty)
	JAMF_Policy_SelfService_Info_Empty = eval(dataToCVS_JAMF_Policy_SelfService_Info_Empty)
	JAMF_Policy_Target_Info_Empty = eval(dataToCVS_JAMF_Policy_Target_Info_Empty)
	JAMF_Policy_Exclusion_Info_Empty = eval(dataToCVS_JAMF_Policy_Exclusion_Info_Empty)
	JAMF_Policy_Packages_Info_Empty = eval(dataToCVS_JAMF_Policy_Packages_Info_Empty)
	JAMF_Policy_Scripts_Info_Empty = eval(dataToCVS_JAMF_Policy_Scripts_Info_Empty)
	JAMF_Configuration_Profile_Info_Empty = eval(dataToCVS_JAMF_Configuration_Profile_Info_Empty)
	JAMF_Configuration_Profile_Target_Info_Empty = eval(dataToCVS_JAMF_Configuration_Profile_Target_Info_Empty)
	JAMF_Configuration_Profile_Exclusion_Info_Empty = eval(dataToCVS_JAMF_Configuration_Profile_Exclusion_Info_Empty)
	
	
	# Build the dataToCsvPolicy
	if get_JAMF_Policy_Info == "yes":
		
		if includePolicyInfo == "yes":
			
			policyColumns = JAMF_Policy_Info
			
			
		if includeSelfServiceInfo == "yes":
			
			selfServiceColumns = JAMF_Policy_SelfService_Info
			
		elif includeSelfServiceInfo == "no":
			
			selfServiceColumns = JAMF_Policy_SelfService_Info_Empty
			
			
		if includeTargetsInfo == "yes":
			
			targetsColumns = JAMF_Policy_Target_Info
			
		elif includeTargetsInfo == "no":
			
			targetsColumns = JAMF_Policy_Target_Info_Empty
			
			
		if includeExclusionsInfo == "yes":
			
			exclusionColumns = JAMF_Policy_Exclusion_Info
			
		elif includeExclusionsInfo == "no":
			
			exclusionColumns = JAMF_Policy_Exclusion_Info_Empty	
			
			
		if includePackagesInfo == "yes":
			
			packageColumns = JAMF_Policy_Packages_Info
			
		elif includePackagesInfo == "no":
			
			packageColumns = JAMF_Policy_Packages_Info_Empty
			
			
		if includeScriptsInfo == "yes":
			
			scriptsColumns = JAMF_Policy_Scripts_Info
			
		elif includeScriptsInfo == "no":
			
			scriptsColumns = JAMF_Policy_Scripts_Info_Empty
			
	elif get_JAMF_Policy_Info == "no":
		
		policyColumns = JAMF_Policy_Info_Empty
		selfServiceColumns = JAMF_Policy_SelfService_Info_Empty
		targetsColumns = JAMF_Policy_Target_Info_Empty
		exclusionColumns = JAMF_Policy_Exclusion_Info_Empty
		packageColumns = JAMF_Policy_Packages_Info_Empty
		scriptsColumns = JAMF_Policy_Scripts_Info_Empty
		
		
	if get_JAMF_Configuration_Profile_Info == "yes":
		
		if includeConfigurationProfileInfo == "yes":
			
			configProfileColumns = JAMF_Configuration_Profile_Info
			
		elif includeConfigurationProfileInfo == "no":
			
			configProfileColumns = JAMF_Configuration_Profile_Info_Empty
			
			
		if includeConfigurationProfileTargetsInfo == "yes":
			
			configProfileTargetsColumns = JAMF_Configuration_Profile_Target_Info
			
		elif includeConfigurationProfileTargetsInfo == "no":
			
			configProfileTargetsColumns = JAMF_Configuration_Profile_Target_Info_Empty
			
			
		if includeConfigurationProfileExclusionsInfo == "yes":
			
			configProfileExclusionsColumns = JAMF_Configuration_Profile_Exclusion_Info
			
		elif includeConfigurationProfileExclusionsInfo == "no":
			
			configProfileExclusionsColumns = JAMF_Configuration_Profile_Exclusion_Info_Empty
			
			
	elif get_JAMF_Configuration_Profile_Info == "no":
		
		configProfileColumns = JAMF_Configuration_Profile_Info_Empty
		configProfileTargetsColumns = JAMF_Configuration_Profile_Target_Info_Empty
		configProfileExclusionsColumns = JAMF_Configuration_Profile_Exclusion_Info_Empty
		

if get_JAMF_Policy_Info == ("yes"):
	# Set up url for getting a list of all policies from JAMF API
	url = JAMF_url + "/JSSResource/policies"
	
	response = requests.request("GET", url, headers=headers, auth = HTTPBasicAuth(username, password))
	
	resp = response.json()
	
	# For Testing
	#print(response.json())
	
	policies = resp['policies']
	
	policies.sort(key=lambda item: item.get('id'), reverse=False)
	
	# Process Policy List and get information linked to policies
	for policy in policies:
		
		# Get Policy ID to do JAMF API lookup
		PolicyID = str(policy['id']) 
		
		#	For Testing
		#print(PolicyID)
		
		# Set up url for getting information from each policy ID from JAMF API
		url = JAMF_url + "/JSSResource/policies/id/" + PolicyID
		
		PolicyData = requests.request("GET", url, headers=headers, auth = HTTPBasicAuth(username, password))
		
		getPolicy = PolicyData.json()
		
		# For Testing
		#print(getPolicy)
		
		#General Element for ID and Catagory
		myPolicyGeneral = getPolicy['policy']['general']
		myPolicyGeneralCatagory = getPolicy['policy']['general']['category']
		
		#Scope Element for Computer Targets
		myPolicyScopeTargetsAllComputers = getPolicy['policy']['scope']['all_computers']
		myPolicyScopeTargetsComputers = getPolicy['policy']['scope']['computers']
		myPolicyScopeTargetsComputerGroups = getPolicy['policy']['scope']['computer_groups']
	
		#Scope Element For Limitation
		#myPolicyScopeLimitationsUsers = getPolicy['policy']['scope']['limitations']['users']
		#myPolicyScopeLimitationsUserGroups = getPolicy['policy']['scope']['limitations']['user_groups']
		
		#Scope Element For Exclusions
		myPolicyScopeExclusionsComputers = getPolicy['policy']['scope']['exclusions']['computers']
		myPolicyScopeExclusionsComputerGroups = getPolicy['policy']['scope']['exclusions']['computer_groups']
		
		
		#Package Element
		myPackagesInfo = getPolicy['policy']['package_configuration']['packages']
		
	
		#Script Elements
		myScriptInfo = getPolicy['policy']['scripts']
		
		#SelfService Element
		mySelfServiceInfo = getPolicy['policy']['self_service']
		useForSelfService = str(mySelfServiceInfo['use_for_self_service'])
		
		
		##########################################################################################
		# Process Policy information for csv / Excel
		##########################################################################################
		
		# Individual Policy Info for each record
		getMyPolicyID = (str(myPolicyGeneral['id']) + " - " + myPolicyGeneral['name'])
		getMyPolicyGeneralCatagory = (str(myPolicyGeneralCatagory['id']) + " - " + myPolicyGeneralCatagory['name'])
		
		# Get info for Policies
		print("Working on Policy ID: " + getMyPolicyID)
		
		#Get Catagory name and format for excel
		formatMyPolicyGeneralCatagory = f"\"{myPolicyGeneralCatagory['name']}\""
		
		# Set Variables for Dict for Policy Info
		appendDataToCVS_JAMF_Policy_Info = "{'Type':'Policy',\
			\
			'Policy ID':int(myPolicyGeneral['id']),\
			\
			'Policy Name':myPolicyGeneral['name'],\
			\
			'Policy Category ID':int(myPolicyGeneralCatagory['id']),\
			\
			'Policy Category Name':formatMyPolicyGeneralCatagory}"
		
		appendJAMF_Policy_Info = eval(appendDataToCVS_JAMF_Policy_Info)
		appendPolicyColumns = appendJAMF_Policy_Info
		
		#Set Columns	
		Combined = MergePolicyInfo(appendPolicyColumns, selfServiceColumns, targetsColumns, exclusionColumns, packageColumns, scriptsColumns)
		
		#Set CSV File
		dataToCsvPolicy.append(Combined)	
	
		if get_JAMF_Policy_Info_SelfService == ("yes"):
			if useForSelfService == 'True':
				##########################################################################################
				# Get Info for Self Service
				##########################################################################################
				# Set Variables for Dict for Policy Info
				appendDataToCVS_JAMF_Policy_SelfService_Info = "{'Type':'Policy Self Service Info',\
				\
				'Policy ID':int(myPolicyGeneral['id']),\
				\
				'Policy Name':myPolicyGeneral['name'],\
				\
				'Policy Category ID':int(myPolicyGeneralCatagory['id']),\
				\
				'Policy Category Name':formatMyPolicyGeneralCatagory,\
				\
				'Policy In SelfService':str(mySelfServiceInfo['use_for_self_service']),\
				\
				'Policy In SelfService Name':mySelfServiceInfo['self_service_display_name']}"
				
				appendJAMF_Policy_SelfService_Info = eval(appendDataToCVS_JAMF_Policy_SelfService_Info)
				appendSelfServiceColumns = appendJAMF_Policy_SelfService_Info
				
				#Set Columns	
				Combined = MergePolicyInfo(policyColumns, appendSelfServiceColumns, targetsColumns, exclusionColumns, packageColumns, scriptsColumns)
				
				#Set CSV File
				dataToCsvPolicy.append(Combined)	
	
		if get_JAMF_Policy_Info_Targets == ("yes"):
			##########################################################################################		
			# Get info for Target Computers	
			##########################################################################################
			for computer in myPolicyScopeTargetsComputers:
				
				appendDataToCVS_JAMF_Policy_Target_Info = "{'Type':'Policy Computer Targets',\
				\
				'Policy ID':int(myPolicyGeneral['id']),\
				\
				'Policy Name':myPolicyGeneral['name'],\
				\
				'Policy Category ID':int(myPolicyGeneralCatagory['id']),\
				\
				'Policy Category Name':formatMyPolicyGeneralCatagory,\
				\
				'Policy Target All Computers':str(myPolicyScopeTargetsAllComputers),\
				\
				'Policy Target Computer ID':int(computer['id']),\
				\
				'Policy Target Computer Name':computer['name']}"
				
				appendJAMF_Policy_Target_Info = eval(appendDataToCVS_JAMF_Policy_Target_Info)
				appendtargetsColumns = appendJAMF_Policy_Target_Info
				
				#Set Columns	
				Combined = MergePolicyInfo(policyColumns, selfServiceColumns, appendtargetsColumns, exclusionColumns, packageColumns, scriptsColumns)
				
				#Set CSV File
				dataToCsvPolicy.append(Combined)
			
			
			##########################################################################################
			# Get Info for Target Computer Groups
			##########################################################################################
			for target in myPolicyScopeTargetsComputerGroups:
				
				targetGroupID = str(target['id'])
				
				#Get Group Info from JAMF API
				url = JAMF_url + "/JSSResource/computergroups/id/" + targetGroupID
				
				targetGroupData = requests.request("GET", url, headers=headers, auth = HTTPBasicAuth(username, password))
				
				getTargetGroupData = targetGroupData.json()
				
				#Computer Group Element for Target Groups
				myTargetsComputerGroupInfo = getTargetGroupData['computer_group']
				
				appendDataToCVS_JAMF_Policy_Target_Group_Info = "{'Type':'Policy Computer Target Group',\
				\
				'Policy ID':int(myPolicyGeneral['id']),\
				\
				'Policy Name':myPolicyGeneral['name'],\
				\
				'Policy Category ID':int(myPolicyGeneralCatagory['id']),\
				\
				'Policy Category Name':formatMyPolicyGeneralCatagory,\
				\
				'Policy Target Group ID':int(myTargetsComputerGroupInfo['id']),\
				\
				'Policy Target Group Name':myTargetsComputerGroupInfo['name'],\
				\
				'Policy Target Group is Smart':str(myTargetsComputerGroupInfo['is_smart'])}"
				
				appendJAMF_Policy_Target_Group_Info = eval(appendDataToCVS_JAMF_Policy_Target_Group_Info)
				appendtargetsGroupsColumns = appendJAMF_Policy_Target_Group_Info
				
				#Set Columns	
				Combined = MergePolicyInfo(policyColumns, selfServiceColumns, appendtargetsGroupsColumns, exclusionColumns, packageColumns, scriptsColumns)
				
				#Set CSV File
				dataToCsvPolicy.append(Combined)
			
			
		if get_JAMF_Policy_Info_Exclusions == ("yes"):
			##########################################################################################
			# Get info for exclusion Computers
			##########################################################################################
			for exclusion in myPolicyScopeExclusionsComputers:
				
				appendDataToCVS_JAMF_Policy_Exclusion_Info = "{'Type':'Policy Computer Exclusions',\
				\
				'Policy ID':int(myPolicyGeneral['id']),\
				\
				'Policy Name':myPolicyGeneral['name'],\
				\
				'Policy Category ID':int(myPolicyGeneralCatagory['id']),\
				\
				'Policy Category Name':formatMyPolicyGeneralCatagory,\
				\
				'Policy Exclusion Computer ID':int(exclusion['id']),\
				\
				'Policy Exclusion Computer Name':exclusion['name']}"
				
				appendJAMF_Policy_Exclusion_Info = eval(appendDataToCVS_JAMF_Policy_Exclusion_Info)
				appendExclusionColumns = appendJAMF_Policy_Exclusion_Info
				
				#Set Columns	
				Combined = MergePolicyInfo(policyColumns, selfServiceColumns, targetsColumns, appendExclusionColumns, packageColumns, scriptsColumns)
				
				#Set CSV File
				dataToCsvPolicy.append(Combined)
				
				
			##########################################################################################
			# Get Info for Computer Exclusions groups
			##########################################################################################
			for exclusion in myPolicyScopeExclusionsComputerGroups:
				
				exclusionGroupID = str(exclusion['id'])
				
				#Get Group Info from JAMF API
				url = JAMF_url + "/JSSResource/computergroups/id/" + exclusionGroupID
				
				exclusionGroupData = requests.request("GET", url, headers=headers, auth = HTTPBasicAuth(username, password))
				
				getExclusionGroupData = exclusionGroupData.json()
				
				myExclusionsComputerGroupInfo = getExclusionGroupData['computer_group']
				
				appendDataToCVS_JAMF_Policy_Exclusion_Group_Info = "{'Type':'Policy Computer Exclusions Group',\
				\
				'Policy ID':int(myPolicyGeneral['id']),\
				\
				'Policy Name':myPolicyGeneral['name'],\
				\
				'Policy Category ID':int(myPolicyGeneralCatagory['id']),\
				\
				'Policy Category Name':formatMyPolicyGeneralCatagory,\
				\
				'Policy Exclusion Group id':int(myExclusionsComputerGroupInfo['id']),\
				\
				'Policy Exclusion Group Name':myExclusionsComputerGroupInfo['name'],\
				\
				'Policy Exclusion Group is Smart':str(myExclusionsComputerGroupInfo['is_smart'])}"
				
				appendJAMF_Policy_Exclusion_Info = eval(appendDataToCVS_JAMF_Policy_Exclusion_Group_Info)
				appendExclusionGroupsColumns = appendJAMF_Policy_Exclusion_Info
				
				#Set Columns	
				Combined = MergePolicyInfo(policyColumns, selfServiceColumns, targetsColumns, appendExclusionGroupsColumns, packageColumns, scriptsColumns)
				
				#Set CSV File
				dataToCsvPolicy.append(Combined)
				
				
		if get_JAMF_Policy_Info_Packages == ("yes"):		
			##########################################################################################
			#Get Info for Packages in Policy
			##########################################################################################
			for package in myPackagesInfo:
				
				packageID = str(package['id'])
				
				#Get Group Info from JAMF API
				url = JAMF_url + "/JSSResource/packages/id/" + packageID
				
				packageData = requests.request("GET", url, headers=headers, auth = HTTPBasicAuth(username, password))
				
				getPackageData = packageData.json()
				
				myPackageInfo = getPackageData['package']
				
				formatMyPackageInfoCatagory = f"\"{myPackageInfo['category']}\""
				
				appendDataToCVS_JAMF_Policy_Packages_Info = "{'Type':'Policy Package',\
				\
				'Policy ID':int(myPolicyGeneral['id']),\
				\
				'Policy Name':myPolicyGeneral['name'],\
				\
				'Policy Category ID':int(myPolicyGeneralCatagory['id']),\
				\
				'Policy Category Name':formatMyPolicyGeneralCatagory,\
				\
				'Policy Package ID':int(myPackageInfo['id']),\
				\
				'Policy Package Name':myPackageInfo['name'],\
				\
				'Policy Package Category Name':formatMyPackageInfoCatagory,\
				\
				'Policy Package Filename':myPackageInfo['filename']}"
				
				appendJAMF_Policy_Packages_Info = eval(appendDataToCVS_JAMF_Policy_Packages_Info)
				appendPackageColumns = appendJAMF_Policy_Packages_Info
				
				#Set Columns	
				Combined = MergePolicyInfo(policyColumns, selfServiceColumns, targetsColumns, exclusionColumns, appendPackageColumns, scriptsColumns)
				
				#Set CSV File
				dataToCsvPolicy.append(Combined)
				
				
		if get_JAMF_Policy_Info_Scripts == ("yes"):		
			##########################################################################################
			#Get Info for scripts in Policy
			##########################################################################################
			for script in myScriptInfo:
				
				scriptID = str(script['id'])
				
				#Get Group Info from JAMF API
				url = JAMF_url + "/JSSResource/scripts/id/" + scriptID
				
				scriptData = requests.request("GET", url, headers=headers, auth = HTTPBasicAuth(username, password))
				
				getScriptData = scriptData.json()
				
				myScriptInfo = getScriptData['script']
				
				formatMyScriptsinfoCatagory = f"\"{myScriptInfo['category']}\""
				
				appendDataToCVS_JAMF_Policy_Scripts_Info = "{'Type':'Policy Scripts',\
				\
				'Policy ID':int(myPolicyGeneral['id']),\
				\
				'Policy Name':myPolicyGeneral['name'],\
				\
				'Policy Category ID':int(myPolicyGeneralCatagory['id']),\
				\
				'Policy Category Name':formatMyPolicyGeneralCatagory,\
				\
				'Policy Script ID':int(myScriptInfo['id']),\
				\
				'Policy Script Name':myScriptInfo['name'],\
				\
				'Policy Script Category Name':formatMyScriptsinfoCatagory,\
				\
				'Policy Script Filename':myScriptInfo['filename']}"


				appendJAMF_Policy_Scripts_Info = eval(appendDataToCVS_JAMF_Policy_Scripts_Info)
				appendScriptsColumns = appendJAMF_Policy_Scripts_Info
				
				#Set Columns	
				Combined = MergePolicyInfo(policyColumns, selfServiceColumns, targetsColumns, exclusionColumns, packageColumns, appendScriptsColumns)
				
				#Set CSV File
				dataToCsvPolicy.append(Combined)


##########################################################################################
# Configuration Profiles Section
##########################################################################################			
if get_JAMF_Configuration_Profile_Info == ("yes"):
	
	##########################################################################################
	# Process Configuration Profilesinformation for csv / Excel
	##########################################################################################
	# Set up url for getting a list of all Configuration Profiles from JAMF API
	url = JAMF_url + "/JSSResource/osxconfigurationprofiles"
	
	response = requests.request("GET", url, headers=headers, auth = HTTPBasicAuth(username, password))
	
	resp = response.json()
	
	# For Testing
	#print(response.json())
	
	configurationProfiles = resp['os_x_configuration_profiles']
	
	configurationProfiles.sort(key=lambda item: item.get('id'), reverse=False)
	
	# Process Configuration Profile List and get information linked to Configuration Profiles
	for configurationProfile in configurationProfiles:
		
		# Get configurationProfile ID to do JAMF API lookup
		configurationProfileID = str(configurationProfile['id']) 
	
		#For Testing
		#print(configurationProfileID)
		
		# Set up url for getting information from each configurationProfile ID from JAMF API
		url = JAMF_url + "/JSSResource/osxconfigurationprofiles/id/" + configurationProfileID
		
		configurationProfileData = requests.request("GET", url, headers=headers, auth = HTTPBasicAuth(username, password))
		
		getConfigurationProfile = configurationProfileData.json()
		
		# For Testing
		#print(getConfigurationProfile)
		
		#General Element for ID and Catagory
		myConfigurationProfileGeneral = getConfigurationProfile['os_x_configuration_profile']['general']
		myConfigurationProfileGeneralCatagory = getConfigurationProfile['os_x_configuration_profile']['general']['category']
		
		#Scope Element for Computer Targets
		myConfigurationProfileScopeTargetsAllComputers = getConfigurationProfile['os_x_configuration_profile']['scope']['all_computers']
		myConfigurationProfileScopeTargetsComputers = getConfigurationProfile['os_x_configuration_profile']['scope']['computers']
		myConfigurationProfileScopeTargetsComputerGroups = getConfigurationProfile['os_x_configuration_profile']['scope']['computer_groups']
		
		#Scope Element For Limitation
		myConfigurationProfileScopeLimitationsUsers = getConfigurationProfile['os_x_configuration_profile']['scope']['limitations']['users']
		myConfigurationProfileScopeLimitationsUserGroups = getConfigurationProfile['os_x_configuration_profile']['scope']['limitations']['user_groups']
		
		#Scope Element For Exclusions
		myConfigurationProfileScopeExclusionsComputers = getConfigurationProfile['os_x_configuration_profile']['scope']['exclusions']['computers']
		myConfigurationProfileScopeExclusionsComputerGroups = getConfigurationProfile['os_x_configuration_profile']['scope']['exclusions']['computer_groups']
		
		##########################################################################################
		# Process ConfigurationProfile information for csv / Excel
		##########################################################################################
		
		# Individual ConfigurationProfile Info for each record
		getMyConfigurationProfileID = (str(myConfigurationProfileGeneral['id']) + " - " + myConfigurationProfileGeneral['name'])
		getMyConfigurationProfileGeneralCatagory = (str(myConfigurationProfileGeneralCatagory['id']) + " - " + myConfigurationProfileGeneralCatagory['name'])
		
		# Get info for Policies
		print("Working on Configuration Profile ID: " + getMyConfigurationProfileID)
		
		formatMyConfigurationProfileGeneralCatagory = f"\"{myConfigurationProfileGeneralCatagory['name']}\""
		
		# Set Variables for Dict for Configuration Profile Info
		appendDataToCVS_JAMF_Configuration_Profile_Info = "{'Configuration Profile Type':'Configuration Profile',\
		\
		'Configuration Profile ID':int(myConfigurationProfileGeneral['id']),\
		\
		'Configuration Profile Name':myConfigurationProfileGeneral['name'],\
		\
		'Configuration Profile Category ID':int(myConfigurationProfileGeneralCatagory['id']),\
		\
		'Configuration Profile Category Name':formatMyConfigurationProfileGeneralCatagory}"
		
		appendJAMF_Configuration_Profile_Info = eval(appendDataToCVS_JAMF_Configuration_Profile_Info)
		appendConfigProfileColumns = appendJAMF_Configuration_Profile_Info
		
		#Set Columns	
		Combined = MergeConfigProfileInfo(appendConfigProfileColumns, configProfileTargetsColumns, configProfileExclusionsColumns)
		
		#Set CSV File
		dataToCsvConfigurationProfile.append(Combined)	
		
		
		if get_JAMF_Configuration_Profile_Info_Targets == ("yes"):
			##########################################################################################		
			# Get info for Target Computers	
			##########################################################################################
			for computer in myConfigurationProfileScopeTargetsComputers:
				
				appendDataToCVS_JAMF_Configuration_Profile_Target_Info = "{'Configuration Profile Type':'Configuration Profile Target Computer',\
				\
				'Configuration Profile ID':int(myConfigurationProfileGeneral['id']),\
				\
				'Configuration Profile Name':myConfigurationProfileGeneral['name'],\
				\
				'Configuration Profile Category ID':int(myConfigurationProfileGeneralCatagory['id']),\
				\
				'Configuration Profile Category Name':formatMyConfigurationProfileGeneralCatagory,\
				\
				'Configuration Profile Target Computer ID':int(computer['id']),\
				\
				'Configuration Profile Target Computer Name':computer['name']}"
				
				appendJAMF_Configuration_Profile_Target_Info = eval(appendDataToCVS_JAMF_Configuration_Profile_Target_Info)
				appendConfigProfileTargetsColumns = appendJAMF_Configuration_Profile_Target_Info
				
				#Set Columns	
				Combined = MergeConfigProfileInfo(configProfileColumns, appendConfigProfileTargetsColumns, configProfileExclusionsColumns)
				
				#Set CSV File
				dataToCsvConfigurationProfile.append(Combined)	
				
			
			##########################################################################################
			# Get Info for Target Computer Groups
			##########################################################################################
			for target in myConfigurationProfileScopeTargetsComputerGroups:
				
				targetGroupID = str(target['id'])
				
				#Get Group Info from JAMF API
				url = JAMF_url + "/JSSResource/computergroups/id/" + targetGroupID
				
				targetGroupData = requests.request("GET", url, headers=headers, auth = HTTPBasicAuth(username, password))
				
				getTargetGroupData = targetGroupData.json()
				
				#Computer Group Element for Target Groups
				myTargetsComputerGroupInfo = getTargetGroupData['computer_group']
				
				
				# Get info for Target Computer Group
				appendDataToCVS_JAMF_Configuration_Profile_Target_Group_Info = "{'Configuration Profile Type':'Configuration Profile Target Computer Group',\
				\
				'Configuration Profile ID':int(myConfigurationProfileGeneral['id']),\
				\
				'Configuration Profile Name':myConfigurationProfileGeneral['name'],\
				\
				'Configuration Profile Category ID':int(myConfigurationProfileGeneralCatagory['id']),\
				\
				'Configuration Profile Category Name':formatMyConfigurationProfileGeneralCatagory,\
				\
				'Configuration Profile Target Group ID':int(myTargetsComputerGroupInfo['id']),\
				\
				'Configuration Profile Target Group Name':myTargetsComputerGroupInfo['name'],\
				\
				'Configuration Profile Target Group is Smart':str(myTargetsComputerGroupInfo['is_smart'])}"
				
				appendJAMF_Configuration_Profile_Target_Group_Info = eval(appendDataToCVS_JAMF_Configuration_Profile_Target_Group_Info)
				appendConfigProfileTargetGroupsColumns = appendJAMF_Configuration_Profile_Target_Group_Info
				
				#Set Columns	
				Combined = MergeConfigProfileInfo(configProfileColumns, appendConfigProfileTargetGroupsColumns, configProfileExclusionsColumns)
				
				#Set CSV File
				dataToCsvConfigurationProfile.append(Combined)


		if get_JAMF_Configuration_Profile_Info_Exclusions == ("yes"):
			
			##########################################################################################
			# Get info for exclusion Computers
			##########################################################################################
			for exclusion in myConfigurationProfileScopeExclusionsComputers:
				
				appendDataToCVS_JAMF_Configuration_Profile_Exclusion_Info = "{'Configuration Profile Type':'Configuration Profile Exclusion Computers',\
				\
				'Configuration Profile ID':int(myConfigurationProfileGeneral['id']),\
				\
				'Configuration Profile Name':myConfigurationProfileGeneral['name'],\
				\
				'Configuration Profile Category ID':int(myConfigurationProfileGeneralCatagory['id']),\
				\
				'Configuration Profile Category Name':formatMyConfigurationProfileGeneralCatagory,\
				\
				'Configuration Profile Exclusion Computer id':int(exclusion['id']),\
				\
				'Configuration Profile Exclusion Computer Name':exclusion['name']}"
				
				appendJAMF_Configuration_Profile_Exclusion_Info = eval(appendDataToCVS_JAMF_Configuration_Profile_Exclusion_Info)
				appendConfigProfileExclusionsColumns = appendJAMF_Configuration_Profile_Exclusion_Info
				
				#Set Columns	
				Combined = MergeConfigProfileInfo(configProfileColumns, configProfileTargetsColumns, appendConfigProfileExclusionsColumns)
				
				#Set CSV File
				dataToCsvConfigurationProfile.append(Combined)	
				
			
			##########################################################################################
			#Get Info for Computer Exclusions groups
			##########################################################################################
			for exclusion in myConfigurationProfileScopeExclusionsComputerGroups:
				
				exclusionGroupID = str(exclusion['id'])
				
				#Get Group Info from JAMF API
				url = JAMF_url + "/JSSResource/computergroups/id/" + exclusionGroupID
				
				exclusionGroupData = requests.request("GET", url, headers=headers, auth = HTTPBasicAuth(username, password))
				
				getExclusionGroupData = exclusionGroupData.json()
				
				myExclusionsComputerGroupInfo = getExclusionGroupData['computer_group']
				
				appendDataToCVS_JAMF_Configuration_Profile_Exclusion_Groups_Info = "{'Configuration Profile Type':'Configuration Profile Exclusion Computer Groups',\
				\
				'Configuration Profile ID':int(myConfigurationProfileGeneral['id']),\
				\
				'Configuration Profile Name':myConfigurationProfileGeneral['name'],\
				\
				'Configuration Profile Category ID':int(myConfigurationProfileGeneralCatagory['id']),\
				\
				'Configuration Profile Category Name':formatMyConfigurationProfileGeneralCatagory,\
				\
				'Configuration Profile Exclusion Group id':int(myExclusionsComputerGroupInfo['id']),\
				\
				'Configuration Profile Exclusion Group Name':myExclusionsComputerGroupInfo['name'],\
				\
				'Configuration Profile Exclusion Group is Smart':str(myExclusionsComputerGroupInfo['is_smart'])}"
				
				appendJAMF_Configuration_Profile_Exclusion_Groups_Info = eval(appendDataToCVS_JAMF_Configuration_Profile_Exclusion_Groups_Info)
				appendConfigProfileExclusionsGroupsColumns = appendJAMF_Configuration_Profile_Exclusion_Groups_Info
				
				#Set Columns	
				Combined = MergeConfigProfileInfo(configProfileColumns, configProfileTargetsColumns, appendConfigProfileExclusionsGroupsColumns)
				
				#Set CSV File
				dataToCsvConfigurationProfile.append(Combined)	
				

##########################################################################################
# Process data for Export to csv / Excel
##########################################################################################
# Check and make sure that either Policy or Config Profile was selected
if get_JAMF_Policy_Info == 'yes' or get_JAMF_Configuration_Profile_Info == 'yes':
	
	# Get export to csv file
	if get_JAMF_Policy_Info == ("yes"):
		df_policy = pd.DataFrame(dataToCsvPolicy)
		
	if get_JAMF_Configuration_Profile_Info == ("yes"):	
		df_configProfile = pd.DataFrame(dataToCsvConfigurationProfile)
	
	print('Creating Jamf Instance Info file.')
	
	# We'll define an Excel writer object and the target file
	Excelwriter = pd.ExcelWriter("Jamf_Instance_Info.xlsx", engine="xlsxwriter")
	
	if get_JAMF_Policy_Info == ("yes"):
		df_policy.to_excel(Excelwriter, sheet_name='Jamf Policy Info')
	
	if get_JAMF_Configuration_Profile_Info == ("yes"):
		df_configProfile.to_excel(Excelwriter, sheet_name='Jamf Configuration Profile Info')
	
	#And finally we save the file
	Excelwriter.save()
	
	print("Jamf Instance	 Info file is now Complete")
	
else:
	
	print("No Options Selected. No Report to Run.")