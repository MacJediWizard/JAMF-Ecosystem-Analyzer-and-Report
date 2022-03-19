#!/usr/bin/env python3

##########################################################################################
# General Information
##########################################################################################
#
#	Script created By William Grzybowski March 3, 2022
#
#	Version 1.0	- Initial Creation of Script.
#	Version 2.0 - Adding Computer fields and sheets to report
#
#	This script take User Imput and will call the JAMF API and get all Information 
#	related to a Policy, Configuration Profile, and Computers.
#
#	It looks up all selected Info and then returns an Excel spreadsheet.
#
#	Fields returned in csv / Excel are as follows below:
#
#
##################################################
#	Policy Record Type
##################################################
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
#
##################################################
#	Configuration Profile Record Type
##################################################
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
##################################################
#	Computer Record Type
##################################################
#	if you are usingSmartGroup
#
#		Computer SmartGroup ID
#
#		Computer SmartGroup Name
#
#		Computer Record Type
#
#		Computer ID
#
#		Computer Name
#
#		Computer Serial Number
#
#	If you are not usingSmartGroup
#
#		Computer Record Type
#
#		Computer ID
#
#		Computer Name
#
#		Computer Serial Number
#
#
#	Computer Make
#
#	Computer Model
#
#	Computer Model Identifier
#
#	Computer OS Name
#
#	Computer OS Version
#
#	Computer OS Build
#
#
#	Computer FileVault2 User
#
#	Computer Local Account Name
#
#	Computer Local Account Real Name
#
#	Computer Local Account ID
#
#	Computer Local Account is Admin
#
#	Computer Local Account in LDAP
#
#
##################################################
#	Additional Info
##################################################
#
#	The only requirement is that you have Python3 on the device. All other libraries
#	the script will look for them and download if they are not found.
#
#	Run from terminal and answer the 3 fields. URL, API Username, API Password.
#	You can also send command line args to the script
#	For Example : yourScript.py "URL" "API Username" "API Password"
#
#	You also get the option to select the path and filename for your xlsx file.
#
#	In the Computers section you have the option of running the report with a
#	smart group is or on the whole instance.
#
#	When looking up local accounts from the computers section, you can do an LDAP
#	check to see what accounts are in LDAP. Great for when you use a JIM server.
#	
#	It wall also look up all JIM servers and let you choose the one you want to use.
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
import os, sys, time, getpass, re

from os.path import exists


# For Using the Requests Library with the API
try:
	import requests
except ImportError:
	os.system('pip3 install requests')
	time.sleep(3)
	import requests
	
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.exceptions import HTTPError


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
dataToCsvComputers = []
dataToCsvPolicy = []
dataToCsvConfigurationProfile = []
JIMServerList = []


#To check User login in JAMF API
get_JAMF_URL_User_Test = "/JSSResource/accounts/username/"


# For default Local User Accounts you do not want in the List
filterDefaultUserAccountsList = ['daemon', 'jamfmgmt', 'nobody', 'root']


#CLA for terminal
APILoginURL = sys.argv[1]
APIUsername = sys.argv[2]
APIPassword = sys.argv[3]


##########################################################################################
# Jamf API Setup Information
##########################################################################################
# requests headers
headers = {
	'Accept': 'application/json',
	'Content-Type': 'application/json'
}


DEFAULT_TIMEOUT = 5 # seconds

class TimeoutHTTPAdapter(HTTPAdapter):
	def __init__(self, *args, **kwargs):
		self.timeout = DEFAULT_TIMEOUT
		if "timeout" in kwargs:
			self.timeout = kwargs["timeout"]
			del kwargs["timeout"]
		super().__init__(*args, **kwargs)
		
	def send(self, request, **kwargs):
		timeout = kwargs.get("timeout")
		if timeout is None:
			kwargs["timeout"] = self.timeout
		return super().send(request, **kwargs)
	
	
# Retry for requests
retry_strategy = Retry(
	total=10,
	backoff_factor=1,
	status_forcelist=[204, 413, 429, 500, 502, 503, 504],
	allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST", "HTTP"]
)

adapter = TimeoutHTTPAdapter(max_retries=retry_strategy)

http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)


##########################################################################################
# Functions
##########################################################################################
#Check for Yes or no answer from input
def getYesOrNoInput(prompt):
	while True:
		try:
			value = input(prompt)
		except ValueError:
			print("\nSorry, I didn't understand that.")
			continue
		
		if value.lower() != 'yes' and value.lower() != 'no':
			print("\nSorry, your response must be yes or no only.")
			continue
		else:
			break
	return value


#Merge Dictionaries
def MergeComputersInfo(dict1, dict2, dict3, dict4):
	result = dict1 | dict2 | dict3 | dict4
	return result


def MergePolicyInfo(dict1, dict2, dict3, dict4, dict5, dict6):
	result = dict1 | dict2 | dict3 | dict4 | dict5 | dict6
	return result


def MergeConfigProfileInfo(dict1, dict2, dict3):
	result = dict1 | dict2 | dict3
	return result


#Check User Input for URL, Username, and Password
def JAMFInfoCheck(url, username, password):
	try:
		response = http.get(url, headers=headers, auth = HTTPBasicAuth(username, password))
		if response.status_code == 200:
			return print(f"\nUser Input is OK, we can connect to JAMF API, Moving on.\n\n")
		else:
			raise SystemExit(f"\nUser Input is NOT OK, we cannot connect to JAMF API and now will EXIT! status_code: {response.status_code}\n\n")
			
	#Exception
	except requests.exceptions.RequestException as e:
		# print URL with Erors
		raise SystemExit(f"\nUser Input is NOT OK, we cannot connect to JAMF API and now will EXIT! \nErr: {e}")


# let user choose Options from list
def let_user_pick(label, options):
	print(label+"\n")
	
	for index, element in enumerate(options):
		print("{}) {}".format(index + 1, element))
		
	while True:
		try:
			i = input("\nEnter number: ")
			
			try:
				if 0 < int(i) <= len(options):
					return int(i) - 1
					break
			
				else:
					print("\nI didn't get a number in the list. Please try again with a number in the list.")
					continue
			
			except ValueError:
				print ("\nYou fail at typing numbers. Please try again with a NUMBER in the list")
				continue
			
			return None
		
		except:
			print ("\nOops, Something went wrong.")
			
		return None
	
	return None
	
# Check Input for Number only
def checkInputForNumber(label):
	
	while True:
		num = input(label+" ")
		try:
			val = int(num)
			
			print("\nSetting Smart Group ID to: "+num)
			smartGroupID = num
			break;
		
		except ValueError:
			
			try:
				float(num)
				print("Input is an float number.")
				print("Input number is: ", val)
				break;
			
			except ValueError:
				print("\nThis is not a number. Please enter a valid number\n")
	
	return num


def checkFilePath(prompt):
	while True:
		try:
			value = input(prompt)
		except ValueError:
			print("\nSorry, I didn't understand that.")
			continue
		
		pathExist = os.path.exists(value)
		
		if pathExist != True :
			print("\nFile does not Path Exists.")
			continue
		else:
			break
	return value  


def checkFileName(prompt):
	while True:
		try:
			value = input(prompt)
		except ValueError:
			print("\nSorry, I didn't understand that.")
			continue
		
		if not value.endswith('.xlsx'):
			print("\nFilename has the wrong extension for Excel.")
			continue
		else:
			break
	return value   


def confirmExcelFileName(prompt):
	while True:
		try:
			value = input(prompt)
		except ValueError:
			print("\nSorry, I didn't understand that.")
			continue
		
		if value.lower() != 'yes' and value.lower() != 'no':
			print("\nSorry, your response must be yes or no only.")
			continue
		elif value.lower() == 'no' :
			raise SystemExit(f"\nUser DID NOT confirm the Excel File Name and now will EXIT!")
			
		elif value.lower() == 'yes':
			break
	return value


##########################################################################################
# Get User Input
##########################################################################################
#Get User input if needed or use command line arguments

print("******************** JAMF API Credentials ********************\n")

if APILoginURL == "" :
	
	get_JAMF_URL = input("Enter your JAMF Instance URL (https://yourjamf.jamfcloud.com): ")
	
else:
	
	print("JAMF URL supplied in command line arguments.")
	get_JAMF_URL = sys.argv[1]

	
if APIUsername == "" :
	
	get_JAMF_API_Username = input("Enter your JAMF Instance API Username: ")
	
else:
	
	print("JAMF API Username supplied in command line arguments.")
	get_JAMF_API_Username = sys.argv[2]


if APIPassword == "" :
	
	get_JAMF_API_Password = getpass.getpass("Enter your JAMF Instance API Password: ")
	
else:
	
	print("JAMF API Username supplied in command line arguments.")
	get_JAMF_API_Password = sys.argv[3]



#Check User Input for URL, Username, and Password
JAMFInfoCheck((get_JAMF_URL+get_JAMF_URL_User_Test+get_JAMF_API_Username), get_JAMF_API_Username, get_JAMF_API_Password)


# Get Main Groups Section.
print("\n******************** JAMF API File Info ********************\n")
get_JAMF_FilePath_Info = checkFilePath("Please enter the full path where you want to save the file (ex. \"/Users/Shared/\") : ")
get_JAMF_FileName_Info = checkFileName("Please enter the name you want to save the excel file as. (ex. \"myExcelFile.xlsx\") : ")

getDesplayExcelReportFile = get_JAMF_FilePath_Info+get_JAMF_FileName_Info

desplayExcelReportFile = f"{getDesplayExcelReportFile}"

confirmExcelReportFile = confirmExcelFileName("Please confirm that the filename, " + desplayExcelReportFile + " is correct. (yes or no)")

if confirmExcelReportFile == 'yes':
	excelReportFile = desplayExcelReportFile
	print("\nSetting filename for JAMF Report to: "+excelReportFile+"\n")


# Get Main Groups Section.
print("\n\n******************** JAMF API Report Excel Sheets ********************\n")
get_JAMF_Computers_Info = getYesOrNoInput("Do you want to include JAMF Computer Info Section in Report? (yes or no): ")
get_JAMF_Policy_Info = getYesOrNoInput("Do you want to include JAMF Policy Info Section in Report? (yes or no): ")
get_JAMF_Configuration_Profile_Info = getYesOrNoInput("Do you want to include JAMF Configuration Profile Info Section in Report? (yes or no): ")


##########################################################################################
# JAMF API Variables
##########################################################################################
JAMF_url = get_JAMF_URL
username = get_JAMF_API_Username
password = get_JAMF_API_Password


##########################################################################################
# Core Script
##########################################################################################
##################################################
# Get Jamf Computer Info
##################################################
if get_JAMF_Computers_Info == ("yes"):
	
	#Get Computer Info
	print("\nIncluding JAMF Computer Info.\n\n")
	includeComputerInfo = "yes"
	
	
	#Get Smart Group ID if needed
	print("\n******************** JAMF API Computer Info Smart Group Section. ********************\n")
	get_JAMF_Computers_Info_SmartGroup = getYesOrNoInput("Do you want to use a JAMF Smart Group for the Computer Report Info? (yes or no): ")
	
	if get_JAMF_Computers_Info_SmartGroup == 'yes':
		
		print("\nUsing JAMF Smart Group for the Computer Report.\n\n")
		smartGroupIDLabel = "Enter your JAMF SmartGroup ID Number: "
		get_JAMF_SmartGroup_ID = checkInputForNumber(smartGroupIDLabel)
		print("\n")
		JAMF_SmartGroup_ID = get_JAMF_SmartGroup_ID
		usingSmartGroup = "yes"
		
		
	elif get_JAMF_Computers_Info_SmartGroup == ("no"):
		
		print("\nNot using JAMF Smart Group for the Computer Report.\n\n")
		usingSmartGroup = "no"
	
	
	#Get Policy Self Service Elements
	print("\n******************** JAMF API Computer Info Hardware Section. ********************\n")
	get_JAMF_Computers_Info_Hardware = getYesOrNoInput("Do you want to include JAMF Computer Hardware Info in Report? (yes or no): ")
	if get_JAMF_Computers_Info_Hardware == ("yes"):
		
		print("\nIncluding Computer Hardware Data.\n\n")		
		includeHardwareInfo = "yes"
		
	elif get_JAMF_Computers_Info_Hardware == ("no"):
		
		print("\nNot Including Computer Hardware Data.\n\n")		
		includeHardwareInfo = "no"
		
		
	#Get FileVault2 Users
	print("\n******************** JAMF API Computer Info FileVault2 Section. ********************\n")
	get_JAMF_Computers_Info_FileVault2_Users = getYesOrNoInput("Do you want to include JAMF Computer Hardware FileVault Users Info in Report? (yes or no): ")
	if get_JAMF_Computers_Info_FileVault2_Users == ("yes"):
		
		print("\nIncluding FileVault2 Info Data.\n\n")		
		includeFileVault2Info = "yes"
		
	elif get_JAMF_Computers_Info_FileVault2_Users == ("no"):
		
		print("\nNot including FileVault2 Info Data.\n\n")
		includeFileVault2Info = "no"

	
	#Get Local Users Accounts
	print("\n******************** JAMF API Computer Info Local Account Section. ********************\n")
	get_JAMF_Computers_Info_Local_Account = getYesOrNoInput("Do you want to include JAMF Computer Hardware Local Account Info in Report? (yes or no): ")
	if get_JAMF_Computers_Info_Local_Account == ("yes"):
		
		print("\nIncluding Local Account Info Data.\n\n")
		includeLocalAccountInfo = "yes"
		
		print("\n******************** JAMF API Computer Info Local Account LDAP Section. ********************\n")
		get_JAMF_Computers_Info_Local_Account_LDAP = getYesOrNoInput("Do you want to include JAMF Computer Hardware Local Accounts LDAP Verification in Report? (yes or no): ")
		
		if get_JAMF_Computers_Info_Local_Account_LDAP == ("yes"):
			
			print("\nIncluding Local Account Info LDAP Verification Data.\n\n")
			includeLocalAccountInfoLDAP = "yes"
			
			# Lookup JIM Server Name
			url = JAMF_url + "/JSSResource/ldapservers"
			
			try:
				response = http.get(url, headers=headers, auth = HTTPBasicAuth(username, password))
			
				response.raise_for_status()

				resp = response.json()
				
			except HTTPError as http_err:
				print(f'HTTP error occurred: {http_err}')
			except Exception as err:
				print(f'Other error occurred: {err}')	
			
			#For Testing
			#print(resp)
			
			JIMServerRecords = resp['ldap_servers']
			JIMServerRecords.sort(key=lambda item: item.get('id'), reverse=False)
			
			
			for JIMServer in JIMServerRecords:
				
				JIMServerRecordsName = JIMServer['name']
				JIMServerList.append(JIMServerRecordsName)
				
			JIMServerlabel = "Please choose the JIM Server you would like to use:"
			
			JimServerChoice = let_user_pick(JIMServerlabel, JIMServerList)
			
			JIMServerNameForURL = (JIMServerList[JimServerChoice])
			
			JIMServerLDAPLookupURL = "/JSSResource/ldapservers/name/" + JIMServerNameForURL
			
			
		elif get_JAMF_Computers_Info_Local_Account_LDAP == ("no"):
			
			print("\nIncluding Local Account Info LDAP Verification Data.\n\n")
			includeLocalAccountInfoLDAP = "no"
			
		
	elif get_JAMF_Computers_Info_Local_Account == ("no"):
		
		print("\nNot including Local Account Info Data.\n\n")
		includeLocalAccountInfo = "no"


##################################################
# Get Jamf Policy Info
##################################################
if get_JAMF_Policy_Info == ("yes"):
	
	#Get Policy Info
	print("\nIncluding JAMF Policy Info.\n\n")
	includePolicyInfo = "yes"
	
	
	#Get Policy Self Service Elements
	print("\n******************** JAMF API Policy Self Service Section. ********************\n")
	get_JAMF_Policy_Info_SelfService = getYesOrNoInput("Do you want to include JAMF Policy Self Service Info in Report? (yes or no): ")
	if get_JAMF_Policy_Info_SelfService == ("yes"):
		
		print("\nIncluding Self Service Data.\n\n")
		
		includeSelfServiceInfo = "yes"
		
	elif get_JAMF_Policy_Info_SelfService == ("no"):
		
		print("\nNot Including Self Service Data.\n\n")
		
		includeSelfServiceInfo = "no"
		
		
	#Get Policy Targets
	print("\n******************** JAMF API Policy Targets Section. ********************\n")
	get_JAMF_Policy_Info_Targets = getYesOrNoInput("Do you want to include JAMF Policy Targets Info in Report? (yes or no): ")
	if get_JAMF_Policy_Info_Targets == ("yes"):
		
		print("\nIncluding Target Data.\n\n")
		
		includeTargetsInfo = "yes"
		
	elif get_JAMF_Policy_Info_Targets == ("no"):
		
		print("\nNot Including Target Data.\n\n")
		
		includeTargetsInfo = "no"
		
		
	#Get Policy Exclusions
	print("\n******************** JAMF API Policy Exclusions Section. ********************\n")
	get_JAMF_Policy_Info_Exclusions = getYesOrNoInput("Do you want to include JAMF Policy Exclusions Info in Report? (yes or no): ")
	if get_JAMF_Policy_Info_Exclusions == ("yes"):
		
		print("\nIncluding Exclusions Data.\n\n")
		
		includeExclusionsInfo = "yes"
		
	elif get_JAMF_Policy_Info_Exclusions == ("no"):
		
		print("\nNot Including Exclusions Data.\n\n")
		
		includeExclusionsInfo = "no"
		
		
	#Get Policy Package Elements
	print("\n******************** JAMF API Policy Packages Section. ********************\n")
	get_JAMF_Policy_Info_Packages = getYesOrNoInput("Do you want to include JAMF Policy Packages Info in Report? (yes or no): ")
	if get_JAMF_Policy_Info_Packages == ("yes"):
		
		print("\nIncluding Package Data.\n\n")
		
		includePackagesInfo = "yes"
		
	elif get_JAMF_Policy_Info_Packages == ("no"):
		
		print("\nNot Including Package Data.\n\n")
		
		includePackagesInfo = "no"
		
		
	#Get Policy Script Elements
	print("\n******************** JAMF API Policy Scripts Section. ********************\n")
	get_JAMF_Policy_Info_Scripts = getYesOrNoInput("Do you want to include JAMF Policy Scripts Info in Report? (yes or no): ")
	if get_JAMF_Policy_Info_Scripts == ("yes"):
		
		print("\nIncluding Scripts Data.\n\n")
		
		includeScriptsInfo = "yes"
		
	elif get_JAMF_Policy_Info_Scripts == ("no"):
		
		print("\nNot Including Scripts Data.\n\n")
		
		includeScriptsInfo = "no"
		
		
elif get_JAMF_Policy_Info == ("no"):
	
	includePolicyInfo = "no"
	

##################################################
# Get Configuration Profile Info
##################################################
if get_JAMF_Configuration_Profile_Info == ("yes"):
	
	#Get Configuration Profile Info
	print("Including Configuration Profile Info.\n\n")
	
	includeConfigurationProfileInfo = "yes"
	
	#Get Policy Targets
	print("\n******************** JAMF API Configuration Profile Targets Section. ********************\n")
	get_JAMF_Configuration_Profile_Info_Targets = getYesOrNoInput("Do you want to include JAMF Configuration Profile Targets Info in Report? (yes or no): ")
	if get_JAMF_Configuration_Profile_Info_Targets == ("yes"):
		
		print("\nIncluding Target Data.\n\n")
		
		includeConfigurationProfileTargetsInfo = "yes"
		
	elif get_JAMF_Configuration_Profile_Info_Targets == ("no"):
		
		print("\nNot Including Target Data.\n\n")
		
		includeConfigurationProfileTargetsInfo = "no"
		
		
	#Get Policy Exclusions
	print("\n******************** JAMF API Configuration Profile Exclusions Section. ********************\n")
	get_JAMF_Configuration_Profile_Info_Exclusions = getYesOrNoInput("Do you want to include JAMF Configuration Profile Exclusions Info in Report? (yes or no): ")
	if get_JAMF_Configuration_Profile_Info_Exclusions == ("yes"):
		
		print("\nIncluding Exclusions Data.\n\n")
		
		includeConfigurationProfileExclusionsInfo = "yes"
		
	elif get_JAMF_Configuration_Profile_Info_Exclusions == ("no"):
		
		print("\nNot Including Exclusions Data.\n\n")
		
		includeConfigurationProfileExclusionsInfo = "no"
		
		
elif get_JAMF_Configuration_Profile_Info == ("no"):
	
	includeConfigurationProfileInfo = "no"
	

##################################################
# Set Variables for dict
##################################################
#Check Options set and desplay message to user
if get_JAMF_Computers_Info == 'yes' or get_JAMF_Policy_Info == 'yes' or get_JAMF_Configuration_Profile_Info == 'yes':
	
	print("\n******************** Running Requested Report Now. ********************\n\n")
	

	##################################################
	# Set Variables for Dict for Computers Info
	##################################################
	if usingSmartGroup == 'yes':
		
		dataToCVS_JAMF_Computers_Info = "{'Computer SmartGroup ID':'',\
		\
		'Computer SmartGroup Name':'',\
		\
		'Type':'',\
		\
		'Computer ID':'',\
		\
		'Computer Name':'',\
		\
		'Computer Serial Number':''}"
		
	elif usingSmartGroup == 'no':
		
		dataToCVS_JAMF_Computers_Info = "{'Type':'',\
		\
		'Computer ID':'',\
		\
		'Computer Name':'',\
		\
		'Computer Serial Number':''}"
		
	
	dataToCVS_JAMF_Computers_Hardware_Info = "{'Computer Make':'',\
	\
	'Computer Model':'',\
	\
	'Computer Model Identifier':'',\
	\
	'Computer OS Name':'',\
	\
	'Computer OS Version':'',\
	\
	'Computer OS Build':''}"	
	
	
	dataToCVS_JAMF_Computers_FileVault2_Info = "{'Computer FileVault2 User':''}"
	
	
	dataToCVS_JAMF_Computers_Local_Account_Info = "{'Computer Local Account Name':'',\
	\
	'Computer Local Account Real Name':'',\
	\
	'Computer Local Account ID':'',\
	\
	'Computer Local Account is Admin ':'',\
	\
	'Computer Local Account in LDAP ':''}"	
	
	
	##################################################
	# Set Variables for Dict for Policy Info
	##################################################
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
	

	##################################################
	# Set Variables for Dict for Computers Info to empty
	##################################################
	if usingSmartGroup == 'yes':
		
		dataToCVS_JAMF_Computers_Info_Empty = "{'Computer SmartGroup ID':'',\
		\
		'Computer SmartGroup Name':'',\
		\
		'Type':'',\
		\
		'Computer ID':'',\
		\
		'Computer Name':'',\
		\
		'Computer Serial Number':''}"
		
	elif usingSmartGroup == 'no':
		
		dataToCVS_JAMF_Computers_Info_Empty = "{'Type':'',\
		\
		'Computer ID':'',\
		\
		'Computer Name':'',\
		\
		'Computer Serial Number':''}"
		

	dataToCVS_JAMF_Computers_Hardware_Info_Empty = "{'Computer Make':'',\
	\
	'Computer Model':'',\
	\
	'Computer Model Identifier':'',\
	\
	'Computer OS Name':'',\
	\
	'Computer OS Version':'',\
	\
	'Computer OS Build':''}"	
	
	
	dataToCVS_JAMF_Computers_FileVault2_Info_Empty = "{'Computer FileVault2 User':''}"
	
	
	dataToCVS_JAMF_Computers_Local_Account_Info_Empty = "{'Computer Local Account Name':'',\
	\
	'Computer Local Account Real Name':'',\
	\
	'Computer Local Account ID':'',\
	\
	'Computer Local Account is Admin ':'',\
	\
	'Computer Local Account in LDAP ':''}"
	
	
	##################################################
	# Set Variables for Dict for Policy Info Empty
	##################################################
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
	
	
	##################################################
	# Set Variables for Dict for Configuration Profile Info to empty
	##################################################
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
	
	
	##################################################
	# Take Variables and make Dict
	##################################################
	# Computers Info
	JAMF_Computers_Info = eval(dataToCVS_JAMF_Computers_Info)
	JAMF_Computers_Hardware_Info = eval(dataToCVS_JAMF_Computers_Hardware_Info)
	JAMF_Computers_FileVault2_Info = eval(dataToCVS_JAMF_Computers_FileVault2_Info)
	JAMF_Computers_Local_Account_Info = eval(dataToCVS_JAMF_Computers_Local_Account_Info)
	
	# Policy Info
	JAMF_Policy_Info = eval(dataToCVS_JAMF_Policy_Info)
	JAMF_Policy_SelfService_Info = eval(dataToCVS_JAMF_Policy_SelfService_Info)
	JAMF_Policy_Target_Info = eval(dataToCVS_JAMF_Policy_Target_Info)
	JAMF_Policy_Exclusion_Info = eval(dataToCVS_JAMF_Policy_Exclusion_Info)
	JAMF_Policy_Packages_Info = eval(dataToCVS_JAMF_Policy_Packages_Info)
	JAMF_Policy_Scripts_Info = eval(dataToCVS_JAMF_Policy_Scripts_Info)
	
	# Configuration Profile Info
	JAMF_Configuration_Profile_Info = eval(dataToCVS_JAMF_Configuration_Profile_Info)
	JAMF_Configuration_Profile_Target_Info = eval(dataToCVS_JAMF_Configuration_Profile_Target_Info)
	JAMF_Configuration_Profile_Exclusion_Info = eval(dataToCVS_JAMF_Configuration_Profile_Exclusion_Info)
	
	
	##################################################
	# Take Variables and make them a Empty Dict
	##################################################
	# Computers Info
	JAMF_Computers_Info_Empty = eval(dataToCVS_JAMF_Computers_Info_Empty)
	JAMF_Computers_Hardware_Info_Empty = eval(dataToCVS_JAMF_Computers_Hardware_Info_Empty)
	JAMF_Computers_FileVault2_Info_Empty = eval(dataToCVS_JAMF_Computers_FileVault2_Info_Empty)
	JAMF_Computers_Local_Account_Info_Empty = eval(dataToCVS_JAMF_Computers_Local_Account_Info_Empty)
	
	# Policy Info
	JAMF_Policy_Info_Empty = eval(dataToCVS_JAMF_Policy_Info_Empty)
	JAMF_Policy_SelfService_Info_Empty = eval(dataToCVS_JAMF_Policy_SelfService_Info_Empty)
	JAMF_Policy_Target_Info_Empty = eval(dataToCVS_JAMF_Policy_Target_Info_Empty)
	JAMF_Policy_Exclusion_Info_Empty = eval(dataToCVS_JAMF_Policy_Exclusion_Info_Empty)
	JAMF_Policy_Packages_Info_Empty = eval(dataToCVS_JAMF_Policy_Packages_Info_Empty)
	JAMF_Policy_Scripts_Info_Empty = eval(dataToCVS_JAMF_Policy_Scripts_Info_Empty)
	
	# Configuration Profile Info
	JAMF_Configuration_Profile_Info_Empty = eval(dataToCVS_JAMF_Configuration_Profile_Info_Empty)
	JAMF_Configuration_Profile_Target_Info_Empty = eval(dataToCVS_JAMF_Configuration_Profile_Target_Info_Empty)
	JAMF_Configuration_Profile_Exclusion_Info_Empty = eval(dataToCVS_JAMF_Configuration_Profile_Exclusion_Info_Empty)
	
	
	##################################################
	# Build the dataToCsvPolicy
	##################################################
	# Computer Fields
	if get_JAMF_Computers_Info == "yes":
		
		if includeComputerInfo == "yes":
			
			computerColumns = JAMF_Computers_Info
			
			
		if includeHardwareInfo == "yes":
			
			hardwareColumns = JAMF_Computers_Hardware_Info
			
		elif includeHardwareInfo == "no":
			
			hardwareColumns = JAMF_Computers_Hardware_Info_Empty
			
		
		if includeFileVault2Info == "yes":
			
			FileVault2Columns = JAMF_Computers_FileVault2_Info
			
		elif includeFileVault2Info == "no":
			
			FileVault2Columns = JAMF_Computers_FileVault2_Info_Empty
			
		
		if includeLocalAccountInfo == "yes":
			
			LocalAccountColumns = JAMF_Computers_Local_Account_Info
			
		elif includeLocalAccountInfo == "no":
			
			LocalAccountColumns = JAMF_Computers_Local_Account_Info_Empty
			
	elif get_JAMF_Computers_Info == "no":
		
		computerColumns = JAMF_Computers_Info_Empty
		hardwareColumns = JAMF_Computers_Hardware_Info_Empty
		FileVault2Columns = JAMF_Computers_FileVault2_Info_Empty
		LocalAccountColumns = JAMF_Computers_Local_Account_Info_Empty
						
	
	# Policy Fields
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
		
	
	# Configuration Profile Fields
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
		

##########################################################################################
# Process Requested Info for Policies
##########################################################################################			
if get_JAMF_Computers_Info == ("yes"):
	
	##########################################################################################
	# Process Computers information for csv / Excel
	##########################################################################################
	# Set up url for getting a list of all Computers from JAMF API
	if usingSmartGroup == 'yes':
		
		url = JAMF_url + "/JSSResource/computergroups/id/" + JAMF_SmartGroup_ID
		
	elif usingSmartGroup == 'no':
		
		url = JAMF_url + "/JSSResource/computers"
	
	try:
		response = http.get(url, headers=headers, auth = HTTPBasicAuth(username, password))
		
		response.raise_for_status()
		
		resp = response.json()
		
	except HTTPError as http_err:
		print(f'HTTP error occurred: {http_err}')
	except Exception as err:
		print(f'Other error occurred: {err}')
	
	# For Testing
	#print(response.json())
	
	if usingSmartGroup == 'yes':
		
		computerRecords = resp['computer_group']['computers']
		computerRecords.sort(key=lambda item: item.get('id'), reverse=False)
		
		smartGroupRecords = resp['computer_group']
		smartGroupRecordName = smartGroupRecords['name']
		
		#Set Variables if Data Available
		if len(str(smartGroupRecords['id'])) == 0:
			smartGroupRecordID = ''
		else:
			smartGroupRecordID = int(smartGroupRecords['id'])
		
	elif usingSmartGroup == 'no':
		
		computerRecords = resp['computers']
		computerRecords.sort(key=lambda item: item.get('id'), reverse=False)
	
	
	# Process Computers List and get information linked to Computers
	for computerRecord in computerRecords:
		
		# Get configurationProfile ID to do JAMF API lookup
		computerRecordID = str(computerRecord['id']) 
		
		#For Testing
		#print(computerRecordID)
		
		# Set up url for getting information from each configurationProfile ID from JAMF API
		url = JAMF_url + "/JSSResource/computers/id/" + computerRecordID
		
		try:
			response = http.get(url, headers=headers, auth = HTTPBasicAuth(username, password))
			
			response.raise_for_status()
			
			computerRecordProfile = response.json()
			
		except HTTPError as http_err:
			print(f'HTTP error occurred: {http_err}')
		except Exception as err:
			print(f'Other error occurred: {err}')
			
		
		# For Testing
		#print(computerRecordProfile)
		
		#General Element for ID and Catagory
		mycomputerRecordGeneral = computerRecordProfile['computer']['general']
		mycomputerRecordHardware = computerRecordProfile['computer']['hardware']
		mycomputerRecordHardwareFileVault2Users = computerRecordProfile['computer']['hardware']['filevault2_users']
		mycomputerRecordHardwareLocalAccounts = computerRecordProfile['computer']['groups_accounts']['local_accounts']
		
		
		##########################################################################################
		# Process ConfigurationProfile information for csv / Excel
		##########################################################################################
		# Individual Computers Info for each record
		getMycomputerRecordGeneralID = (str(mycomputerRecordGeneral['id']) + " - " + mycomputerRecordGeneral['name'])
		
		# Get info for Policies
		print("Working on Computer ID: " + getMycomputerRecordGeneralID)
		
		#Set Variables if Data Available
		if len(str(mycomputerRecordGeneral['id'])) == 0:
			mycomputerRecordGeneralID = ''
		else:
			mycomputerRecordGeneralID = int(mycomputerRecordGeneral['id'])
			
	
		# Set Variables for Dict for Computers Info
		if usingSmartGroup == 'yes':
			
			appendDataToCVS_JAMF_Computers_Info = "{'Computer SmartGroup ID':smartGroupRecordID,\
			\
			'Computer SmartGroup Name':smartGroupRecordName,\
			\
			'Type':'Computer Info',\
			\
			'Computer ID':mycomputerRecordGeneralID,\
			\
			'Computer Name':mycomputerRecordGeneral['name'],\
			\
			'Computer Serial Number':str(mycomputerRecordGeneral['serial_number'])}"
			
		elif usingSmartGroup == 'no':
			
			appendDataToCVS_JAMF_Computers_Info = "{'Type':'Computer Info',\
			\
			'Computer ID':mycomputerRecordGeneralID,\
			\
			'Computer Name':mycomputerRecordGeneral['name'],\
			\
			'Computer Serial Number':str(mycomputerRecordGeneral['serial_number'])}"
			
			
		appendJAMF_Computers_Info = eval(appendDataToCVS_JAMF_Computers_Info)
		appendComputerColumns = appendJAMF_Computers_Info
		
		#Set Columns	
		Combined = MergeComputersInfo(appendComputerColumns, hardwareColumns, FileVault2Columns, LocalAccountColumns)
		
		#Set CSV File
		dataToCsvComputers.append(Combined)	
		
		
		if get_JAMF_Computers_Info_Hardware == ("yes"):
			##########################################################################################		
			# Get info for Hardware	
			##########################################################################################
			formatMyComputerRecordHardwareOSBuild = f"\"{mycomputerRecordHardware['os_build']}\""
			
			appendDataToCVS_JAMF_Computers_Hardware_Info = "{'Type':'Computer Hardware Info',\
			\
			'Computer ID':mycomputerRecordGeneralID,\
			\
			'Computer Name':mycomputerRecordGeneral['name'],\
			\
			'Computer Make':mycomputerRecordHardware['make'],\
			\
			'Computer Model':mycomputerRecordHardware['model'],\
			\
			'Computer Model Identifier':mycomputerRecordHardware['model_identifier'],\
			\
			'Computer OS Name':mycomputerRecordHardware['os_name'],\
			\
			'Computer OS Version':str(mycomputerRecordHardware['os_version']),\
			\
			'Computer OS Build':formatMyComputerRecordHardwareOSBuild}"	
			
			appendJAMF_Computers_Hardware_Info = eval(appendDataToCVS_JAMF_Computers_Hardware_Info)
			appendComputerHardwareColumns = appendJAMF_Computers_Hardware_Info
			
			#Set Columns	
			Combined = MergeComputersInfo(computerColumns, appendComputerHardwareColumns, FileVault2Columns, LocalAccountColumns)
			
			#Set CSV File
			dataToCsvComputers.append(Combined)	
				
		
		if get_JAMF_Computers_Info_FileVault2_Users == ("yes"):
			##########################################################################################		
			# Get info for FileVautl2	
			##########################################################################################
			for FileVault2User in mycomputerRecordHardwareFileVault2Users :
				
				appendDataToCVS_JAMF_Computers_FileVault2_Info = "{'Type':'Computer Hardware FileVault2 Info',\
				\
				'Computer ID':mycomputerRecordGeneralID,\
				\
				'Computer Name':mycomputerRecordGeneral['name'],\
				\
				'Computer FileVault2 User':FileVault2User}"
				
				appendJAMF_Computers_FileVault2_Info = eval(appendDataToCVS_JAMF_Computers_FileVault2_Info)
				appendComputerFileVault2Columns = appendJAMF_Computers_FileVault2_Info
				
				#Set Columns	
				Combined = MergeComputersInfo(computerColumns, hardwareColumns, appendComputerFileVault2Columns, LocalAccountColumns)
				
				#Set CSV File
				dataToCsvComputers.append(Combined)	
		
			
		if get_JAMF_Computers_Info_Local_Account == ("yes"):
			##########################################################################################		
			# Get info for Local Accounts	
			##########################################################################################
			for computerLocalAccount in mycomputerRecordHardwareLocalAccounts:
				
				# Put current data into variable to filter
				filterComputerLocalAccountData = computerLocalAccount['name']
				
				# Regex Pattern
				filterPattern = r"^((?![_/][a-zA-Z]*))"
				filterDefaultUserAccountsListdata = filterDefaultUserAccountsList
				
				if re.match(filterPattern, filterComputerLocalAccountData): #Check if regex is correct
				
					if filterComputerLocalAccountData not in filterDefaultUserAccountsListdata :
						
						verifyLocalAccountIsAdmin = computerLocalAccount['administrator']
						computerLocalAccountName = computerLocalAccount['name']
						computerLocalAccountRealName = computerLocalAccount['realname']
						
						#Set Variables if Data Available
						if len(str(computerLocalAccount['uid'])) == 0:
							computerLocalAccountUID = ''
						else:
							computerLocalAccountUID = int(computerLocalAccount['uid'])
							
						computerLocalAccountIsAdmin = verifyLocalAccountIsAdmin
						computerInInLDAP = "false"
						
						if includeLocalAccountInfoLDAP == "yes":
							
							# Set up url for getting information from each configurationProfile ID from JAMF API
							url = JAMF_url + JIMServerLDAPLookupURL + "/user/" + filterComputerLocalAccountData
							
							try:
								response = http.get(url, headers=headers, auth = HTTPBasicAuth(username, password))
								
								response.raise_for_status()
								
								verifyLocalAccount = response.json()
								
							except HTTPError as http_err:
								print(f'HTTP error occurred: {http_err}')
							except Exception as err:
								print(f'Other error occurred: {err}')
								
							
							# For Testing
							#print(verifyLocalAccount)
							
							verifidLocalAccountRecords = verifyLocalAccount['ldap_users']
							verifidLocalAccountRecords.sort(key=lambda item: item.get('id'), reverse=False)
							
							for localAccountRecord in verifidLocalAccountRecords :
								
								#print(localAccountRecord['username'])
								
								#Set Variables if Data Available
								if len(str(localAccountRecord['uid'])) == 0:
									computerLocalAccountUID = ''
								else:
									computerLocalAccountUID = int(localAccountRecord['uid'])
									
								
								computerInInLDAP = "true"
								
								
								#print(computerRecordID, compd']
								computerInInLDAP = "true"
								
					
						appendDataToCVS_JAMF_Computers_Local_Account_Info = "{'Type':'Computer Hardware Local Account Info',\
						\
						'Computer ID':mycomputerRecordGeneralID,\
						\
						'Computer Name':mycomputerRecordGeneral['name'],\
						\
						'Computer Local Account Name':computerLocalAccountName,\
						\
						'Computer Local Account Real Name':computerLocalAccountRealName,\
						\
						'Computer Local Account ID':computerLocalAccountUID,\
						\
						'Computer Local Account is Admin ':computerLocalAccountIsAdmin,\
						\
						'Computer Local Account in LDAP ':computerInInLDAP}"
					
						
						appendJAMF_Computers_Local_Account_Info = eval(appendDataToCVS_JAMF_Computers_Local_Account_Info)
						appendLocalAccountColumns = appendJAMF_Computers_Local_Account_Info
					
						#Set Columns	
						Combined = MergeComputersInfo(computerColumns, hardwareColumns, FileVault2Columns, appendLocalAccountColumns)
					
						#Set CSV File
						dataToCsvComputers.append(Combined)	
				

##################################################
# Process Requested Info for Policies
##################################################

if get_JAMF_Policy_Info == ("yes"):
	# Set up url for getting a list of all policies from JAMF API
	url = JAMF_url + "/JSSResource/policies"
	
	try:
		response = http.get(url, headers=headers, auth = HTTPBasicAuth(username, password))
		
		response.raise_for_status()
		
		resp = response.json()
		
	except HTTPError as http_err:
		print(f'HTTP error occurred: {http_err}')
	except Exception as err:
		print(f'Other error occurred: {err}')
	
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
		
		try:
			response = http.get(url, headers=headers, auth = HTTPBasicAuth(username, password))
			
			response.raise_for_status()
			
			getPolicy = response.json()
			
		except HTTPError as http_err:
			print(f'HTTP error occurred: {http_err}')
		except Exception as err:
			print(f'Other error occurred: {err}')
		
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
		
		#Set Variables if Data Available
		if len(str(myPolicyGeneral['id'])) == 0:
			myPolicyGeneralID = ''
		else:
			myPolicyGeneralID = int(myPolicyGeneral['id'])
		
		if len(str(myPolicyGeneralCatagory['id'])) == 0:
			myPolicyGeneralCatagoryID = ''
		else:
			myPolicyGeneralCatagoryID = int(myPolicyGeneralCatagory['id'])
		
		#Get Catagory name and format for excel
		formatMyPolicyGeneralCatagory = f"\"{myPolicyGeneralCatagory['name']}\""
		
		# Set Variables for Dict for Policy Info
		appendDataToCVS_JAMF_Policy_Info = "{'Type':'Policy',\
			\
			'Policy ID':myPolicyGeneralID,\
			\
			'Policy Name':myPolicyGeneral['name'],\
			\
			'Policy Category ID':myPolicyGeneralCatagoryID,\
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
				'Policy ID':myPolicyGeneralID,\
				\
				'Policy Name':myPolicyGeneral['name'],\
				\
				'Policy Category ID':myPolicyGeneralCatagoryID,\
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
				
				#Set Variables if Data Available
				if len(str(computer['id'])) == 0:
					computerID = ''
				else:
					computerID = int(computer['id'])
					
					
				appendDataToCVS_JAMF_Policy_Target_Info = "{'Type':'Policy Computer Targets',\
				\
				'Policy ID':myPolicyGeneralID,\
				\
				'Policy Name':myPolicyGeneral['name'],\
				\
				'Policy Category ID':myPolicyGeneralCatagoryID,\
				\
				'Policy Category Name':formatMyPolicyGeneralCatagory,\
				\
				'Policy Target All Computers':str(myPolicyScopeTargetsAllComputers),\
				\
				'Policy Target Computer ID':computerID,\
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
				
				try:
					response = http.get(url, headers=headers, auth = HTTPBasicAuth(username, password))
					
					response.raise_for_status()
					
					getTargetGroupData = response.json()
					
				except HTTPError as http_err:
					print(f'HTTP error occurred: {http_err}')
				except Exception as err:
					print(f'Other error occurred: {err}')
					
				
				#Computer Group Element for Target Groups
				myTargetsComputerGroupInfo = getTargetGroupData['computer_group']
				
				#Set Variables if Data Available
				if len(str(myTargetsComputerGroupInfo['id'])) == 0:
					myTargetsComputerGroupInfoID = ''
				else:
					myTargetsComputerGroupInfoID = int(myTargetsComputerGroupInfo['id'])
					
					
				appendDataToCVS_JAMF_Policy_Target_Group_Info = "{'Type':'Policy Computer Target Group',\
				\
				'Policy ID':myPolicyGeneralID,\
				\
				'Policy Name':myPolicyGeneral['name'],\
				\
				'Policy Category ID':myPolicyGeneralCatagoryID,\
				\
				'Policy Category Name':formatMyPolicyGeneralCatagory,\
				\
				'Policy Target Group ID':myTargetsComputerGroupInfoID,\
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
				
				#Set Variables if Data Available
				if len(str(exclusion['id'])) == 0:
					exclusionID = ''
				else:
					exclusionID = int(exclusion['id'])
					
					
				appendDataToCVS_JAMF_Policy_Exclusion_Info = "{'Type':'Policy Computer Exclusions',\
				\
				'Policy ID':myPolicyGeneralID,\
				\
				'Policy Name':myPolicyGeneral['name'],\
				\
				'Policy Category ID':myPolicyGeneralCatagoryID,\
				\
				'Policy Category Name':formatMyPolicyGeneralCatagory,\
				\
				'Policy Exclusion Computer ID':exclusionID,\
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
				
				try:
					response = http.get(url, headers=headers, auth = HTTPBasicAuth(username, password))
					
					response.raise_for_status()
					
					getExclusionGroupData = response.json()
					
				except HTTPError as http_err:
					print(f'HTTP error occurred: {http_err}')
				except Exception as err:
					print(f'Other error occurred: {err}')
					
				
				myExclusionsComputerGroupInfo = getExclusionGroupData['computer_group']
				
				#Set Variables if Data Available
				if len(str(myExclusionsComputerGroupInfo['id'])) == 0:
					myExclusionsComputerGroupInfoID = ''
				else:
					myExclusionsComputerGroupInfoID = int(myExclusionsComputerGroupInfo['id'])
					
					
				appendDataToCVS_JAMF_Policy_Exclusion_Group_Info = "{'Type':'Policy Computer Exclusions Group',\
				\
				'Policy ID':myPolicyGeneralID,\
				\
				'Policy Name':myPolicyGeneral['name'],\
				\
				'Policy Category ID':myPolicyGeneralCatagoryID,\
				\
				'Policy Category Name':formatMyPolicyGeneralCatagory,\
				\
				'Policy Exclusion Group id':myExclusionsComputerGroupInfoID,\
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
				
				try:
					response = http.get(url, headers=headers, auth = HTTPBasicAuth(username, password))
					
					response.raise_for_status()
					
					getPackageData = response.json()
					
				except HTTPError as http_err:
					print(f'HTTP error occurred: {http_err}')
				except Exception as err:
					print(f'Other error occurred: {err}')
					
				
				myPackageInfo = getPackageData['package']
				
				formatMyPackageInfoCatagory = f"\"{myPackageInfo['category']}\""
				
				#Set Variables if Data Available
				if len(str(myPackageInfo['id'])) == 0:
					myPackageInfoID = ''
				else:
					myPackageInfoID = int(myPackageInfo['id'])
					
					
				appendDataToCVS_JAMF_Policy_Packages_Info = "{'Type':'Policy Package',\
				\
				'Policy ID':myPolicyGeneralID,\
				\
				'Policy Name':myPolicyGeneral['name'],\
				\
				'Policy Category ID':myPolicyGeneralCatagoryID,\
				\
				'Policy Category Name':formatMyPolicyGeneralCatagory,\
				\
				'Policy Package ID':myPackageInfoID,\
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
				
				try:
					response = http.get(url, headers=headers, auth = HTTPBasicAuth(username, password))
					
					response.raise_for_status()
					
					getScriptData = response.json()
					
				except HTTPError as http_err:
					print(f'HTTP error occurred: {http_err}')
				except Exception as err:
					print(f'Other error occurred: {err}')
					
				
				myScriptInfo = getScriptData['script']
				
				formatMyScriptsinfoCatagory = f"\"{myScriptInfo['category']}\""
				
				#Set Variables if Data Available
				if len(str(myScriptInfo['id'])) == 0:
					myScriptInfoID = ''
				else:
					myScriptInfoID = int(myScriptInfo['id'])
					
				appendDataToCVS_JAMF_Policy_Scripts_Info = "{'Type':'Policy Scripts',\
				\
				'Policy ID':myPolicyGeneralID,\
				\
				'Policy Name':myPolicyGeneral['name'],\
				\
				'Policy Category ID':myPolicyGeneralCatagoryID,\
				\
				'Policy Category Name':formatMyPolicyGeneralCatagory,\
				\
				'Policy Script ID':myScriptInfoID,\
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
	
	try:
		response = http.get(url, headers=headers, auth = HTTPBasicAuth(username, password))
		
		response.raise_for_status()
		
		resp = response.json()
		
	except HTTPError as http_err:
		print(f'HTTP error occurred: {http_err}')
	except Exception as err:
		print(f'Other error occurred: {err}')
	
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
		
		try:
			response = http.get(url, headers=headers, auth = HTTPBasicAuth(username, password))
			
			response.raise_for_status()
			
			getConfigurationProfile = response.json()
			
		except HTTPError as http_err:
			print(f'HTTP error occurred: {http_err}')
		except Exception as err:
			print(f'Other error occurred: {err}')
			
		
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
		
		#Set Variables if Data Available
		if len(str(myConfigurationProfileGeneral['id'])) == 0:
			myConfigurationProfileGeneralID = ''
		else:
			myConfigurationProfileGeneralID = int(myConfigurationProfileGeneral['id'])
		
		#Set Variables if Data Available
		if len(str(myConfigurationProfileGeneralCatagory['id'])) == 0:
			myConfigurationProfileGeneralCatagoryID = ''
		else:
			myConfigurationProfileGeneralCatagoryID = int(myConfigurationProfileGeneralCatagory['id'])
			
			
		# Set Variables for Dict for Configuration Profile Info
		appendDataToCVS_JAMF_Configuration_Profile_Info = "{'Configuration Profile Type':'Configuration Profile',\
		\
		'Configuration Profile ID':myConfigurationProfileGeneralID,\
		\
		'Configuration Profile Name':myConfigurationProfileGeneral['name'],\
		\
		'Configuration Profile Category ID':myConfigurationProfileGeneralCatagoryID,\
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
				'Configuration Profile ID':myConfigurationProfileGeneralID,\
				\
				'Configuration Profile Name':myConfigurationProfileGeneral['name'],\
				\
				'Configuration Profile Category ID':myConfigurationProfileGeneralCatagoryID,\
				\
				'Configuration Profile Category Name':formatMyConfigurationProfileGeneralCatagory,\
				\
				'Configuration Profile Target Computer ID':computerID,\
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
				
				try:
					response = http.get(url, headers=headers, auth = HTTPBasicAuth(username, password))
					
					response.raise_for_status()
					
					getTargetGroupData = response.json()
					
				except HTTPError as http_err:
					print(f'HTTP error occurred: {http_err}')
				except Exception as err:
					print(f'Other error occurred: {err}')
					
				
				#Computer Group Element for Target Groups
				myTargetsComputerGroupInfo = getTargetGroupData['computer_group']
				
				#Set Variables if Data Available
				if len(str(myTargetsComputerGroupInfo['id'])) == 0:
					myTargetsComputerGroupInfoID = ''
				else:
					myTargetsComputerGroupInfoID = int(myTargetsComputerGroupInfo['id'])
					
					
				# Get info for Target Computer Group
				appendDataToCVS_JAMF_Configuration_Profile_Target_Group_Info = "{'Configuration Profile Type':'Configuration Profile Target Computer Group',\
				\
				'Configuration Profile ID':myConfigurationProfileGeneralID,\
				\
				'Configuration Profile Name':myConfigurationProfileGeneral['name'],\
				\
				'Configuration Profile Category ID':myConfigurationProfileGeneralCatagoryID,\
				\
				'Configuration Profile Category Name':formatMyConfigurationProfileGeneralCatagory,\
				\
				'Configuration Profile Target Group ID':myTargetsComputerGroupInfoID,\
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
				
				#Set Variables if Data Available
				if len(str(exclusion['id'])) == 0:
					exclusionID = ''
				else:
					exclusionID = int(exclusion['id'])
					
					
				appendDataToCVS_JAMF_Configuration_Profile_Exclusion_Info = "{'Configuration Profile Type':'Configuration Profile Exclusion Computers',\
				\
				'Configuration Profile ID':myConfigurationProfileGeneralID,\
				\
				'Configuration Profile Name':myConfigurationProfileGeneral['name'],\
				\
				'Configuration Profile Category ID':myConfigurationProfileGeneralCatagoryID,\
				\
				'Configuration Profile Category Name':formatMyConfigurationProfileGeneralCatagory,\
				\
				'Configuration Profile Exclusion Computer id':exclusionID,\
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
				
				try:
					response = http.get(url, headers=headers, auth = HTTPBasicAuth(username, password))
					
					response.raise_for_status()
					
					getExclusionGroupData = response.json()
					
				except HTTPError as http_err:
					print(f'HTTP error occurred: {http_err}')
				except Exception as err:
					print(f'Other error occurred: {err}')
					
				
				myExclusionsComputerGroupInfo = getExclusionGroupData['computer_group']
				
				#Set Variables if Data Available
				if len(str(myExclusionsComputerGroupInfo['id'])) == 0:
					myExclusionsComputerGroupInfoID = ''
				else:
					myExclusionsComputerGroupInfoID = int(myExclusionsComputerGroupInfo['id'])
					
					
				appendDataToCVS_JAMF_Configuration_Profile_Exclusion_Groups_Info = "{'Configuration Profile Type':'Configuration Profile Exclusion Computer Groups',\
				\
				'Configuration Profile ID':myConfigurationProfileGeneralID,\
				\
				'Configuration Profile Name':myConfigurationProfileGeneral['name'],\
				\
				'Configuration Profile Category ID':myConfigurationProfileGeneralCatagoryID,\
				\
				'Configuration Profile Category Name':formatMyConfigurationProfileGeneralCatagory,\
				\
				'Configuration Profile Exclusion Group id':myExclusionsComputerGroupInfoID,\
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
if get_JAMF_Policy_Info == 'yes' or get_JAMF_Configuration_Profile_Info == 'yes' or get_JAMF_Computers_Info == 'yes':
	
	# Get export to csv file
	if get_JAMF_Computers_Info == ("yes"):
		df_computers = pd.DataFrame(dataToCsvComputers)
		
	if get_JAMF_Policy_Info == ("yes"):
		df_policy = pd.DataFrame(dataToCsvPolicy)
		
	if get_JAMF_Configuration_Profile_Info == ("yes"):	
		df_configProfile = pd.DataFrame(dataToCsvConfigurationProfile)

	
	print('\n******************** Creating Jamf Instance Info file. ********************\n')
	
	
	# We'll define an Excel writer object and the target file
	Excelwriter = pd.ExcelWriter(excelReportFile, engine="xlsxwriter")
	
	if get_JAMF_Computers_Info == ("yes"):
		df_computers.to_excel(Excelwriter, sheet_name='Jamf Computers Info')
		
	if get_JAMF_Policy_Info == ("yes"):
		df_policy.to_excel(Excelwriter, sheet_name='Jamf Policy Info')
	
	if get_JAMF_Configuration_Profile_Info == ("yes"):
		df_configProfile.to_excel(Excelwriter, sheet_name='Jamf Configuration Profile Info')
	
	#And finally we save the file
	Excelwriter.save()
	
	print("\n******************** Jamf Instance Info file is now Complete. ********************\n")
	
else:
	
	print("\n******************** No Options Selected. No Report to Run. ********************\n")