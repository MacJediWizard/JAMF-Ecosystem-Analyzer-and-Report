#!/usr/bin/env python3

##########################################################################################
# General Information
##########################################################################################
#
#	Script created By William Grzybowski March 3, 2022
#
#	Version 1.0	- Initial Creation of Script.
#	Version 2.0 - Adding Computer fields and sheets to report
#	Version 3.0 - Adding Bearer Token Auth for requests
#	Version 4.0 - Adding Package to policy / Prestage Policy lookup for unused packages.
#	Version 5.0 - Adding Computer Group Membership to Computers Sheet in report
#	Version 6.0 - Adding Results filter for Computer Record Sheet to filter by 
#				  computer, smart group, or none.
#	Version 7.0	- Adding Configuration Profile Membership to Computers Sheet in report.
#	Version 7.0 - Adding Default file path and file name to choice with date and time.
#	Version 8.0 - Adding Script to Policy lookup for unused Scripts.
#	Version 9.0 - Adding Multithreading to Computer, Policy, and Configuration Profile
#				  sections to increase performance for those reports.
#				- Formated excel sheets with color highlighting, auto column with for
#				  data, and formated titles and headers to make easier to read.
#
#	Version 10.0 - Adding last checkin and site info to computer info.
#
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
#	if you are usingFilter for SmartGroup
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
#		Computer Last Check-in
#
#		Computer Site Info
#
#	If you are not usingFilter or just single computer
#
#		Computer Record Type
#
#		Computer ID
#
#		Computer Name
#
#		Computer Serial Number
#
#		Computer Last Check-in
#
#		Computer Site Info
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
#	Computer Group Membership Group ID
#
#	Computer Group Membership Group Name
#
#	Computer Group Membership Group Is Smart
#
#
#	Configuration Profile Membership ID
#
#	Configuration Profile Membership Name
#
#
##################################################
#	Package to Policy lookup
##################################################
#	Provides the following:
#	
#	Package used or Package Not Used
#	in Policies
#
#	Which Policy Package is used in. Policies
#	or PreStage Policies
#	
#	Package ID
#
#	Package Name
#
#	Package File Name
#
#	Policy ID if used in a Policy
#
#	Policy Name if used in Policy
#
#	PreStage Policy ID if used 
#	in PreStage Policy
#
#	PreStage Policy Name if used 
#	in PreStage Policy
#
#	Patch Management Policy ID if used 
#	in Patch Management Policy
#
#	Patch Management Policy Name if used 
#	in Patch Management Policy
#
#	Patch Management Policy Software Version
#	Name if used in Patch Management Policy
#
#
##################################################
#	Script to Policy lookup
##################################################
#	Provides the following:
#	
#	Script used or Script Not Used
#	in Policies
#	
#	Script ID
#
#	Script Name
#
#	Script File Name
#
#	Policy ID if used in a Policy
#
#	Policy Name if used in Policy
#
#
##################################################
#	Additional Info
##################################################
#
#	The only requirement is that you have Python 3.9 + on the device. All other libraries
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
#	The script uses the new bearer token auth for the API calls and then
#	invalidates it when script is complete.
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
import os, sys, time, getpass, re, datetime

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


#For xml to dict processing. using where bad json response.
try:
	import xmltodict
except ImportError:
	os.system('pip3 install xmltodict')
	time.sleep(3)
	import xmltodict

	
# New MultiThread libraries
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import pandas.io.formats.excel


##########################################################################################
# Variables
##########################################################################################
#Set Variable for the Data
dataToCsvComputers = []
dataToCsvPolicy = []
dataToCsvConfigurationProfile = []
dataToCsvPackageToPolicy = []
dataToCsvScriptToPolicy = []
JIMServerList = []


#To check User login in JAMF API
get_JAMF_URL_User_Test = "/JSSResource/accounts/username/"


# For default Local User Accounts you do not want in the List
filterDefaultUserAccountsList = ['daemon', 'jamfmgmt', 'nobody', 'root']


#Check CLA for input
if len(sys.argv) == 1:
	# No CLA Given
	APILoginURL = ""
	APIUsername = ""
	APIPassword = ""
	
elif len(sys.argv) == 2:
	# No CLA Given
	APILoginURL = sys.argv[1]
	APIUsername = ""
	APIPassword = ""
	
elif len(sys.argv) == 3:
	# No CLA Given
	APILoginURL = sys.argv[1]
	APIUsername = sys.argv[2]
	APIPassword = ""
	
elif len(sys.argv) == 4:
	# No CLA Given
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


DEFAULT_TIMEOUT = 15 # seconds

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
	total=25,
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
def MergeComputersInfo(dict1, dict2, dict3, dict4, dict5, dict6):
	result = dict1 | dict2 | dict3 | dict4 | dict5 | dict6
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
		raise SystemExit(f"\nUser Input is NOT OK, we cannot connect to JAMF API and now will EXIT! \n\nErr: {e}")


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


def checkIfPackageIsUsedInPolicy(data, key, value):
	for i in range(len(data)):
		try:
			if(data[i][key]==value): return True
		except:
			pass
	return False


def checkIfScriptIsUsedInPolicy(data, key, value):
	for i in range(len(data)):
		try:
			if(data[i][key]==value): return True
		except:
			pass
	return False


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


##########################################################################################
# JAMF API Variables
##########################################################################################
JAMF_url = get_JAMF_URL
username = get_JAMF_API_Username
password = get_JAMF_API_Password


# Get Bearer token from JAMF API since we confirmed the Username and Password
btURL = JAMF_url + "/api/v1/auth/token"
token = http.post(btURL, headers=headers, auth = HTTPBasicAuth(username, password))
bearer = token.json()['token']


# requests headers with token auth
btHeaders = {
	'Accept': 'application/json',
	'Authorization': 'Bearer '+bearer
}


##########################################################################################
# Get Report Config Input
##########################################################################################
# Get Main Groups Section.
print("\n******************** JAMF API Excel File Info ********************\n")
get_JAMF_Default_Path_Name = getYesOrNoInput("Do you want to use the Default filename and path for the Report (/Users/Shared/JAMF_Excel_Report_xx_xx_xxxx-xx:xx:xx.xlsx) ? (yes or no): ")

if get_JAMF_Default_Path_Name == 'yes':
	# Get Time
	getFileNameTime = datetime.datetime.now()
	fileNameTimeString = (getFileNameTime.strftime("%a_%b-%d-%Y_%H-%M-%S"))
	
	#Set filename with time and date
	get_JAMF_FilePath_Info = '/Users/Shared/'
	get_JAMF_FileName_Info = 'JAMF_Excel_Report_' + str(fileNameTimeString) + '.xlsx'
	
elif get_JAMF_Default_Path_Name == 'no':
	
	get_JAMF_Default_FilePath = getYesOrNoInput("Do you want to use the Default file path for the Report (/Users/Shared/) ? (yes or no): ")
	
	if get_JAMF_Default_FilePath == 'yes':
		get_JAMF_FilePath_Info = '/Users/Shared/'
		get_JAMF_FileName_Info = checkFileName("Please enter the name you want to save the excel file as. (ex. \"myExcelFile.xlsx\") : ")
		
	elif get_JAMF_Default_FilePath == 'no':
		get_JAMF_FilePath_Info = checkFilePath("Please enter the full path where you want to save the file (ex. \"/Users/Shared/\") : ")
		get_JAMF_FileName_Info = checkFileName("Please enter the name you want to save the excel file as. (ex. \"myExcelFile.xlsx\") : ")


getDesplayExcelReportFile = get_JAMF_FilePath_Info+get_JAMF_FileName_Info

desplayExcelReportFile = f"{getDesplayExcelReportFile}"

confirmExcelReportFile = confirmExcelFileName("Please confirm that the filename, " + desplayExcelReportFile + " is correct. (yes or no)")

if confirmExcelReportFile == 'yes':
	excelReportFile = desplayExcelReportFile
	print("\nSetting filename for JAMF Report to: "+excelReportFile+"\n")


# Get Main Groups Section.
print("\n\n******************** JAMF API Report Included Excel Sheets ********************\n")
get_JAMF_Computers_Info = getYesOrNoInput("Do you want to include JAMF Computer Info Section in Report? (yes or no): ")
get_JAMF_Policy_Info = getYesOrNoInput("Do you want to include JAMF Policy Info Section in Report? (yes or no): ")
get_JAMF_Configuration_Profile_Info = getYesOrNoInput("Do you want to include JAMF Configuration Profile Info Section in Report? (yes or no): ")
get_JAMF_Package_To_Policy_Info = getYesOrNoInput("Do you want to include JAMF Package To Policy Info Section in Report? (yes or no): ")
get_JAMF_Script_To_Policy_Info = getYesOrNoInput("Do you want to include JAMF Script To Policy Info Section in Report? (yes or no): ")


##########################################################################################
# Core Script
##########################################################################################
##################################################
# Get Jamf Computer Info
##################################################
print("\n\n******************** JAMF API Report Included Excel Sheets Config Info ********************\n")

if get_JAMF_Computers_Info == ("yes"):
	
	#Get Computer Info
	print("\nIncluding JAMF Computer Info.\n\n")
	includeComputerInfo = "yes"
	
	
	#Get Smart Group ID if needed
	print("\n******************** JAMF API Computer Info Results Filter Section. ********************\n")
	print("\n\nPlease choose how you would like the results returned in your report. It is recommended to use a smart group id or computer id for this report for quickest results.\n")
	print("\nPlease Note if you choose all computers the report may take some time to complete depending on the number of computers in your JAMF system.")
	
	# Set options for results filter for this section and question
	myResultsFilterLabel = "Your results filter choices are:"
	mymyResultsFilterOptions = ["Filter results for 1 Computer ID", "Filter results By Smart Group ID", "No Filter, Return All Computers"]
	
	# Get choice from user
	get_JAMF_Computers_Info_Results_Filter = let_user_pick(myResultsFilterLabel, mymyResultsFilterOptions)
	
	get_JAMF_Computers_Info_Results_Filter_Choice = (mymyResultsFilterOptions[get_JAMF_Computers_Info_Results_Filter])
	
	#Return choice and set filter
	if get_JAMF_Computers_Info_Results_Filter_Choice == 'Filter results for 1 Computer ID':
		
		print("\nUsing JAMF Computer ID to filter the Computer Report for 1 Computer Record.\n\n")
		computerIDLabel = "Enter your JAMF Computer ID Number: "
		get_JAMF_Computer_ID = checkInputForNumber(computerIDLabel)
		print("\n")
		JAMF_Computer_ID = get_JAMF_Computer_ID
		usingFilter = "computerFilter"
		
		
	elif get_JAMF_Computers_Info_Results_Filter_Choice == 'Filter results By Smart Group ID':
		
		print("\nUsing JAMF Smart Group to filter the Computer Report for 1 Computer Smart Group.\n\n")
		smartGroupIDLabel = "Enter your JAMF SmartGroup ID Number: "
		get_JAMF_SmartGroup_ID = checkInputForNumber(smartGroupIDLabel)
		print("\n")
		JAMF_SmartGroup_ID = get_JAMF_SmartGroup_ID
		usingFilter = "smartGroupFilter"
		
		
	elif get_JAMF_Computers_Info_Results_Filter_Choice == 'No Filter, Return All Computers':
		
		print("\nNot using JAMF Results Filter for the Computer Report.\n\n")
		usingFilter = "noFilter"
	
	
	#Get hardware Elements
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
				response = http.get(url, headers=btHeaders)
			
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

	
	#Get Group Membership
	print("\n******************** JAMF API Computer Info Computer Group Membership Section. ********************\n")
	get_JAMF_Computers_Info_Computer_Group_Membership = getYesOrNoInput("Do you want to include JAMF Computer Hardware Computer Group Membership Info in Report? (yes or no): ")
	if get_JAMF_Computers_Info_Computer_Group_Membership == ("yes"):
		
		print("\nIncluding Computer Group Membership Info Data.\n\n")		
		includeComputerGroupMembershipInfo = "yes"
		
	elif get_JAMF_Computers_Info_Computer_Group_Membership == ("no"):
		
		print("\nNot including Computer Group Membership Info Data.\n\n")
		includeComputerGroupMembershipInfo = "no"
		
		
	#Get Config Profile Membership
	print("\n******************** JAMF API Computer Info Computer Configuration Profile Membership Section. ********************\n")
	get_JAMF_Computers_Info_Computer_Configuration_Profile_Membership = getYesOrNoInput("Do you want to include JAMF Computer Hardware Configuration Profile Membership Info in Report? (yes or no): ")
	if get_JAMF_Computers_Info_Computer_Configuration_Profile_Membership == ("yes"):
		
		print("\nIncluding Computer Configuration Profile Membership Info Data.\n\n")		
		includeComputerConfigurationProfileMembershipInfo = "yes"
		
	elif get_JAMF_Computers_Info_Computer_Configuration_Profile_Membership == ("no"):
		
		print("\nNot including Computer Group Membership Info Data.\n\n")
		includeComputerConfigurationProfileMembershipInfo = "no"


elif get_JAMF_Computers_Info == ("no"):
	
	includeComputerInfo = "no"
	usingFilter = "noFilter"
	includeHardwareInfo = "no"
	includeFileVault2Info = "no"
	includeLocalAccountInfo = "no"
	includeComputerGroupMembershipInfo = "no"
	includeComputerConfigurationProfileMembershipInfo = "no"
	

##################################################
# Get Jamf Policy Info
##################################################
print("\n\n******************** JAMF API Report Included Excel Sheets Config Info ********************\n")

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
print("\n\n******************** JAMF API Report Included Excel Sheets Config Info ********************\n")

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
# Get Jamf Package To Policy Info
##################################################
print("\n\n******************** JAMF API Report Included Package To Policy Info ********************\n")

if get_JAMF_Package_To_Policy_Info == ("yes"):
	
	#Get Package To Policy Info
	print("\nIncluding JAMF Regular Package Info.\n\n")
	
	includeRegularPackageToPolicyInfo = "yes"
	
	#Get Policy Exclusions
	print("\n******************** JAMF API Package To Policy in PreStage Policy Section. ********************\n")
	get_JAMF_Policy_in_PreStage_Policy_Info = getYesOrNoInput("Do you want to include JAMF Package To Policy in PreStage Policy Info in Report? (yes or no): ")
	if get_JAMF_Policy_in_PreStage_Policy_Info == ("yes"):
		
		print("\nIncluding PreStage Policy Info.\n\n")
		
		includePreStagePackageToPolicyInfo = "yes"
		
	elif get_JAMF_Policy_in_PreStage_Policy_Info == ("no"):
		
		print("\nNot Including PreStage Policy Info.\n\n")
		
		includePreStagePackageToPolicyInfo = "no"
		
		
	print("\n******************** JAMF API Package To Policy in Patch Management Section. ********************\n")
	get_JAMF_Policy_in_Patch_Management_Info = getYesOrNoInput("Do you want to include JAMF Package To Policy in Patch Management Info in Report? (yes or no): ")
	if get_JAMF_Policy_in_Patch_Management_Info == ("yes"):
		
		print("\nIncluding Patch Management Info.\n\n")
		
		includePatchManagementPackageToPolicyInfo = "yes"
		
	elif get_JAMF_Policy_in_Patch_Management_Info == ("no"):
		
		print("\nNot Including Patch Management Info.\n\n")
		
		includePatchManagementPackageToPolicyInfo = "no"
		
		
##################################################
# Get Jamf Script To Policy Info
##################################################
print("\n\n******************** JAMF API Report Included Script To Policy Info ********************\n")

if get_JAMF_Script_To_Policy_Info == ("yes"):
	
	#Get Script To Policy Info
	print("\nIncluding JAMF Regular Script Info.\n\n")
	
	includeRegularScriptToPolicyInfo = "yes"

				
##################################################
# Set Variables for dict
##################################################
#Check Options set and desplay message to user
if get_JAMF_Computers_Info == 'yes' or get_JAMF_Policy_Info == 'yes' or get_JAMF_Configuration_Profile_Info == 'yes' or get_JAMF_Package_To_Policy_Info == 'yes' or get_JAMF_Script_To_Policy_Info == 'yes':
	
	print("\n******************** Running Requested Report Now. ********************\n\n")
	

	##################################################
	# Set Variables for Dict for Computers Info
	##################################################
	if usingFilter == 'computerFilter':
		
		dataToCVS_JAMF_Computers_Info = "{'Type':'',\
		\
		'Computer ID':'',\
		\
		'Computer Name':'',\
		\
		'Computer Serial Number':'',\
		\
		'Computer Last Check-in':'',\
		\
		'Computer Site Info':''}"
		
	elif usingFilter == 'smartGroupFilter':
		
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
		'Computer Serial Number':'',\
		\
		'Computer Last Check-in':'',\
		\
		'Computer Site Info':''}"
		
	elif usingFilter == 'noFilter':
		
		dataToCVS_JAMF_Computers_Info = "{'Type':'',\
		\
		'Computer ID':'',\
		\
		'Computer Name':'',\
		\
		'Computer Serial Number':'',\
		\
		'Computer Last Check-in':'',\
		\
		'Computer Site Info':''}"
		
	
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

	
	dataToCVS_JAMF_Computers_Info_Computer_Group_Membership = "{'Computer Group Membership Group ID':'',\
	\
	'Computer Group Membership Group Name':'',\
	\
	'Computer Group Membership Group Is Smart':''}"
	
	
	dataToCVS_JAMF_Computers_Info_Computer_Configuration_Profile_Membership = "{'Computer Configuration Profile Membership ID':'',\
	\
	'Computer Configuration Profile Membership Name':''}"
	
	
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
	
	
	##################################################
	# Set Variables for Dict for Configuration Profile Info
	##################################################
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
	# Set Variables for Dict for Packages to Policies Info
	##################################################
	dataToCVS_JAMF_Package_To_Regular_Policy_Info = "{'Type':'',\
	\
	'Package List':'',\
	\
	'Package ID':'',\
	\
	'Package Name':'',\
	\
	'Package File Name':'',\
	\
	'Policy ID':'',\
	\
	'Policy Name':''}"
	
	
	dataToCVS_JAMF_Package_To_PreStage_Policy_Info = "{'Type':'',\
	\
	'Package List':'',\
	\
	'Package ID':'',\
	\
	'Package Name':'',\
	\
	'Package File Name':'',\
	\
	'Policy ID':'',\
	\
	'Policy Name':''}"
	
	
	dataToCVS_JAMF_Package_Unused_Info = "{'Type':'',\
	\
	'Package List':'',\
	\
	'Package ID':'',\
	\
	'Package Name':'',\
	\
	'Package File Name':''}"
	
	
	##################################################
	# Set Variables for Dict for Script to Policies Info
	##################################################
	dataToCVS_JAMF_Script_To_Regular_Policy_Info = "{'Type':'',\
	\
	'Script ID':'',\
	\
	'Script Name':'',\
	\
	'Script File Name':'',\
	\
	'Policy ID':'',\
	\
	'Policy Name':''}"
	
	dataToCVS_JAMF_Script_Unused_Info = "{'Type':'',\
	\
	'Script ID':'',\
	\
	'Script Name':'',\
	\
	'Script File Name':''}"	
	

	##################################################
	# Set Variables for Dict for Computers Info to empty
	##################################################
	if usingFilter == 'computerFilter':
		
		dataToCVS_JAMF_Computers_Info_Empty = "{'Type':'',\
		\
		'Computer ID':'',\
		\
		'Computer Name':'',\
		\
		'Computer Serial Number':'',\
		\
		'Computer Last Check-in':'',\
		\
		'Computer Site Info':''}"
		
	elif usingFilter == 'smartGroupFilter':
		
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
		'Computer Serial Number':'',\
		\
		'Computer Last Check-in':'',\
		\
		'Computer Site Info':''}"
		
	elif usingFilter == 'noFilter':
		
		dataToCVS_JAMF_Computers_Info_Empty = "{'Type':'',\
		\
		'Computer ID':'',\
		\
		'Computer Name':'',\
		\
		'Computer Serial Number':'',\
		\
		'Computer Last Check-in':'',\
		\
		'Computer Site Info':''}"
		
		

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
	
	
	dataToCVS_JAMF_Computers_Info_Computer_Group_Membership_Empty = "{'Computer Group Membership Group ID':'',\
	\
	'Computer Group Membership Group Name':'',\
	\
	'Computer Group Membership Group Is Smart':''}"
	
	
	dataToCVS_JAMF_Computers_Info_Computer_Configuration_Profile_Membership_Empty = "{'Computer Configuration Profile Membership ID':'',\
	\
	'Computer Configuration Profile Membership Name':''}"
	
	
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
	# Set Variables for Dict for Script Profile Info to empty
	##################################################
	dataToCVS_JAMF_Package_To_Regular_Policy_Info_Empty = "{'Type':'',\
	\
	'Package List':'',\
	\
	'Package ID':'',\
	\
	'Package Name':'',\
	\
	'Package File Name':'',\
	\
	'Policy ID':'',\
	\
	'Policy Name':''}"
	
	
	dataToCVS_JAMF_Package_To_PreStage_Policy_Info_Empty = "{'Type':'',\
	\
	'Package List':'',\
	\
	'Package ID':'',\
	\
	'Package Name':'',\
	\
	'Package File Name':'',\
	\
	'Policy ID':'',\
	\
	'Policy Name':''}"
	
	
	dataToCVS_JAMF_Package_Unused_Info_Empty = "{'Type':'',\
	\
	'Package List':'',\
	\
	'Package ID':'',\
	\
	'Package Name':'',\
	\
	'Package File Name':''}"
	
	
	##################################################
	# Set Variables for Dict for Script to Policies Info Empty
	##################################################
	dataToCVS_JAMF_Script_To_Regular_Policy_Info_Empty = "{'Type':'',\
	\
	'Script ID':'',\
	\
	'Script Name':'',\
	\
	'Script File Name':'',\
	\
	'Policy ID':'',\
	\
	'Policy Name':''}"
	
	dataToCVS_JAMF_Script_Unused_Info_Empty = "{'Type':'',\
	\
	'Script ID':'',\
	\
	'Script Name':'',\
	\
	'Script File Name':''}"	
	
	
	##################################################
	# Take Variables and make Dict
	##################################################
	# Computers Info
	JAMF_Computers_Info = eval(dataToCVS_JAMF_Computers_Info)
	JAMF_Computers_Hardware_Info = eval(dataToCVS_JAMF_Computers_Hardware_Info)
	JAMF_Computers_FileVault2_Info = eval(dataToCVS_JAMF_Computers_FileVault2_Info)
	JAMF_Computers_Local_Account_Info = eval(dataToCVS_JAMF_Computers_Local_Account_Info)
	JAMF_Computers_Info_Computer_Group_Membership = eval(dataToCVS_JAMF_Computers_Info_Computer_Group_Membership)
	JAMF_Computers_Info_Computer_Configuration_Profile_Membership = eval(dataToCVS_JAMF_Computers_Info_Computer_Configuration_Profile_Membership)
	
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
	
	# Package to Policy Info
	JAMF_Package_To_Regular_Policy_Info = eval(dataToCVS_JAMF_Package_To_Regular_Policy_Info)
	JAMF_Package_To_PreStage_Policy_Info = eval(dataToCVS_JAMF_Package_To_PreStage_Policy_Info)
	JAMF_Package_Unused_Info = eval(dataToCVS_JAMF_Package_Unused_Info)
	
	
	# Script to Policy Info
	JAMF_Script_To_Regular_Policy_Info = eval(dataToCVS_JAMF_Script_To_Regular_Policy_Info)
	JAMF_Script_Unused_Info = eval(dataToCVS_JAMF_Script_Unused_Info)
	
	
	##################################################
	# Take Variables and make them a Empty Dict
	##################################################
	# Computers Info
	JAMF_Computers_Info_Empty = eval(dataToCVS_JAMF_Computers_Info_Empty)
	JAMF_Computers_Hardware_Info_Empty = eval(dataToCVS_JAMF_Computers_Hardware_Info_Empty)
	JAMF_Computers_FileVault2_Info_Empty = eval(dataToCVS_JAMF_Computers_FileVault2_Info_Empty)
	JAMF_Computers_Local_Account_Info_Empty = eval(dataToCVS_JAMF_Computers_Local_Account_Info_Empty)
	JAMF_Computers_Info_Computer_Group_Membership_Empty = eval(dataToCVS_JAMF_Computers_Info_Computer_Group_Membership_Empty)
	JAMF_Computers_Info_Computer_Configuration_Profile_Membership_Empty = eval(dataToCVS_JAMF_Computers_Info_Computer_Configuration_Profile_Membership_Empty)
	
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
	
	# Package to Policy Info
	JAMF_Package_To_Regular_Policy_Info_Empty = eval(dataToCVS_JAMF_Package_To_Regular_Policy_Info_Empty)
	JAMF_Package_To_PreStage_Policy_Info_Empty = eval(dataToCVS_JAMF_Package_To_PreStage_Policy_Info_Empty)
	JAMF_Package_Unused_Info_Empty = eval(dataToCVS_JAMF_Package_Unused_Info_Empty)
	
	# Script to Policy Info
	JAMF_Script_To_Regular_Policy_Info_Empty = eval(dataToCVS_JAMF_Script_To_Regular_Policy_Info_Empty)
	JAMF_Script_Unused_Info_Empty = eval(dataToCVS_JAMF_Script_Unused_Info_Empty)
	
	
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
			
			
		if includeComputerGroupMembershipInfo == 'yes':
			
			computerGroupMembershipColumns = JAMF_Computers_Info_Computer_Group_Membership
			
		elif includeComputerGroupMembershipInfo == 'no':
			
			computerGroupMembershipColumns = JAMF_Computers_Info_Computer_Group_Membership_Empty
			
			
		if includeComputerConfigurationProfileMembershipInfo == 'yes':
			
			computerConfigurationProfileMembershipColumns = JAMF_Computers_Info_Computer_Configuration_Profile_Membership
			
		elif includeComputerConfigurationProfileMembershipInfo == 'no':
			
			computerConfigurationProfileMembershipColumns = JAMF_Computers_Info_Computer_Configuration_Profile_Membership_Empty	
			
			
	elif get_JAMF_Computers_Info == "no":
		
		computerColumns = JAMF_Computers_Info_Empty
		hardwareColumns = JAMF_Computers_Hardware_Info_Empty
		FileVault2Columns = JAMF_Computers_FileVault2_Info_Empty
		LocalAccountColumns = JAMF_Computers_Local_Account_Info_Empty
		computerGroupMembershipColumns = JAMF_Computers_Info_Computer_Group_Membership_Empty
		computerConfigurationProfileMembershipColumns = JAMF_Computers_Info_Computer_Configuration_Profile_Membership_Empty	
						
	
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
	
	
	# Package to Policy Info fields
	if get_JAMF_Package_To_Policy_Info == 'yes':
		
		# Regular columns
		if includeRegularPackageToPolicyInfo == "yes":
			
			packageToRegularPolicyColumns = JAMF_Package_To_Regular_Policy_Info
			packageUnusedColumns = JAMF_Package_Unused_Info	
			
		elif includeRegularPackageToPolicyInfo == "no":
			
			packageToRegularPolicyColumns = JAMF_Package_To_Regular_Policy_Info_Empty
			packageUnusedColumns = JAMF_Package_Unused_Info_Empty
		
		#prestage columns
		if includePreStagePackageToPolicyInfo == "yes":
			
			packageToPreStagePolicyColumns = JAMF_Package_To_PreStage_Policy_Info
			packageUnusedColumns = JAMF_Package_Unused_Info
			
		elif includePreStagePackageToPolicyInfo == "no":
			
			packageToPreStagePolicyColumns = JAMF_Package_To_PreStage_Policy_Info_Empty
			packageUnusedColumns = JAMF_Package_Unused_Info_Empty
			
			
	# Script to Policy Info fields
	if get_JAMF_Script_To_Policy_Info == 'yes':
		
		# Regular columns
		if includeRegularScriptToPolicyInfo == "yes":
			
			ScriptToRegularPolicyColumns = JAMF_Script_To_Regular_Policy_Info
			ScriptUnusedColumns = JAMF_Script_Unused_Info	
			
		elif includeRegularScriptToPolicyInfo == "no":
			
			ScriptToRegularPolicyColumns = JAMF_Script_To_Regular_Policy_Info_Empty
			ScriptUnusedColumns = JAMF_Script_Unused_Info_Empty
			

##########################################################################################
# Process Requested Info for Sheets
##########################################################################################			
if get_JAMF_Computers_Info == ("yes"):
	
	##########################################################################################
	# Process Computers information for csv / Excel
	##########################################################################################
	# Set up url for getting a list of all Computers from JAMF API
	if usingFilter == 'computerFilter':
		
		url = JAMF_url + "/JSSResource/computers/id/" + JAMF_Computer_ID
		
	elif usingFilter == 'smartGroupFilter':
		
		url = JAMF_url + "/JSSResource/computergroups/id/" + JAMF_SmartGroup_ID
		
	elif usingFilter == 'noFilter':
		
		url = JAMF_url + "/JSSResource/computers"
	
	try:
		response = http.get(url, headers=btHeaders)
		
		response.raise_for_status()
		
		resp = response.json()
		
	except HTTPError as http_err:
		print(f'HTTP error occurred: {http_err}')
	except Exception as err:
		print(f'Other error occurred: {err}')
	
	# For Testing
	#print(response.json())
	
	#Choose filter for records
	if usingFilter == 'computerFilter':
		
		computerRecords = resp['computer']['general']

		
	elif usingFilter == 'smartGroupFilter':
		
		computerRecords = resp['computer_group']['computers']
		computerRecords.sort(key=lambda item: item.get('id'), reverse=False)
		
		smartGroupRecords = resp['computer_group']
		smartGroupRecordName = smartGroupRecords['name']
		
		#Set Variables if Data Available
		if len(str(smartGroupRecords['id'])) == 0:
			smartGroupRecordID = ''
		else:
			smartGroupRecordID = int(smartGroupRecords['id'])
		
	elif usingFilter == 'noFilter':
		
		computerRecords = resp['computers']
		computerRecords.sort(key=lambda item: item.get('id'), reverse=False)
	
	
	# Process Computers List and get information linked to Computers
	if usingFilter == 'computerFilter':
		
		#run for single computer
		# Get ID to do JAMF API lookup
		computerRecordID = str(computerRecords['id'])
		
		#For Testing
		#print(computerRecordID)
		
		# Set up url for getting information from each configurationProfile ID from JAMF API
		url = JAMF_url + "/JSSResource/computers/id/" + computerRecordID
		
		try:
			response = http.get(url, headers=btHeaders)
			
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
		mycomputerRecordComputerGroupMembership = computerRecordProfile['computer']['groups_accounts']['computer_group_memberships']
		mycomputerConfigurationProfileMembership = computerRecordProfile['computer']['configuration_profiles']
		
		
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
		if usingFilter == 'computerFilter':
			
			appendDataToCVS_JAMF_Computers_Info = "{'Type':'Computer Info',\
			\
			'Computer ID':mycomputerRecordGeneralID,\
			\
			'Computer Name':mycomputerRecordGeneral['name'],\
			\
			'Computer Serial Number':str(mycomputerRecordGeneral['serial_number']),\
			\
			'Computer Last Check-in':str(mycomputerRecordGeneral['last_contact_time']),\
			\
			'Computer Site Info':str(mycomputerRecordGeneral['site']['name'])}"
			
		elif usingFilter == 'smartGroupFilter':
			
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
			'Computer Serial Number':str(mycomputerRecordGeneral['serial_number']),\
			\
			'Computer Last Check-in':str(mycomputerRecordGeneral['last_contact_time']),\
			\
			'Computer Site Info':str(mycomputerRecordGeneral['site']['name'])}"
			
		elif usingFilter == 'noFilter':
			
			appendDataToCVS_JAMF_Computers_Info = "{'Type':'Computer Info',\
			\
			'Computer ID':mycomputerRecordGeneralID,\
			\
			'Computer Name':mycomputerRecordGeneral['name'],\
			\
			'Computer Serial Number':str(mycomputerRecordGeneral['serial_number']),\
			\
			'Computer Last Check-in':str(mycomputerRecordGeneral['last_contact_time']),\
			\
			'Computer Site Info':str(mycomputerRecordGeneral['site']['name'])}"
			
			
		appendJAMF_Computers_Info = eval(appendDataToCVS_JAMF_Computers_Info)
		appendComputerColumns = appendJAMF_Computers_Info
		
		#Set Columns	
		Combined = MergeComputersInfo(appendComputerColumns, hardwareColumns, FileVault2Columns, LocalAccountColumns, computerGroupMembershipColumns, computerConfigurationProfileMembershipColumns)
		
		#Set CSV File
		dataToCsvComputers.append(Combined)	
		
		
		if get_JAMF_Computers_Info_Hardware == ("yes"):
			##########################################################################################		
			# Get info for Hardware	
			##########################################################################################
			# Get info for Policies
			print(".......Getting Hardware Info for Computer ID: " + getMycomputerRecordGeneralID)
			
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
			Combined = MergeComputersInfo(computerColumns, appendComputerHardwareColumns, FileVault2Columns, LocalAccountColumns, computerGroupMembershipColumns, computerConfigurationProfileMembershipColumns)
			
			#Set CSV File
			dataToCsvComputers.append(Combined)	
			
			
		if get_JAMF_Computers_Info_FileVault2_Users == ("yes"):
			##########################################################################################		
			# Get info for FileVautl2	
			##########################################################################################
			print(".......Getting FileVault Info for Computer ID: " + getMycomputerRecordGeneralID)
			
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
				Combined = MergeComputersInfo(computerColumns, hardwareColumns, appendComputerFileVault2Columns, LocalAccountColumns, computerGroupMembershipColumns, computerConfigurationProfileMembershipColumns)
				
				#Set CSV File
				dataToCsvComputers.append(Combined)	
				
				
		if get_JAMF_Computers_Info_Local_Account == ("yes"):
			##########################################################################################		
			# Get info for Local Accounts	
			##########################################################################################
			print(".......Getting Local Account Info for Computer ID: " + getMycomputerRecordGeneralID)
			
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
								response = http.get(url, headers=btHeaders)
								
								response.raise_for_status()
								
								verifyLocalAccount = response.json()
								
							except HTTPError as http_err:
								# Process HTTP Error
								check_http_err = str(http_err)
								split_My_http_err = check_http_err.split()
								
								myHttpError = split_My_http_err[0]
								myMissingRecordID = filterComputerLocalAccountData
								myMissingRecordURL = split_My_http_err[5]
								
								if myHttpError == '404':
									print(f".......We found that Record: {myMissingRecordID}, does not exist in your JAMF Instance at URL: {myMissingRecordURL}")
									
								else:
									print(f'HTTP error occurred: {http_err}')
									
								continue
							except Exception as err:
								print(f'Other error occurred: {err}')
								continue
								
								
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
						Combined = MergeComputersInfo(computerColumns, hardwareColumns, FileVault2Columns, appendLocalAccountColumns, computerGroupMembershipColumns, computerConfigurationProfileMembershipColumns)
						
						#Set CSV File
						dataToCsvComputers.append(Combined)	
						
						
		if get_JAMF_Computers_Info_Computer_Group_Membership == 'yes':
			##########################################################################################		
			# Get info for Computer Group Membership	
			##########################################################################################
			print(".......Getting Computer Group Info for Computer ID: " + getMycomputerRecordGeneralID)
			
			#Get Info from record
			computerGroupMembershipRecords = mycomputerRecordComputerGroupMembership
			
			
			list_of_groups = []
			
			for groupName in computerGroupMembershipRecords :
				list_of_groups.append(f'{groupName}')
				
				
			# Renew token because the report is a long process
			# renew token
			tokenURL = JAMF_url + "/api/v1/auth/keep-alive"
			
			token = http.post(tokenURL, headers=btHeaders)
			
			bearer = token.json()['token']
			
			btHeaders = {
				'Accept': 'application/json',
				'Authorization': 'Bearer '+bearer
			}
			
			
			def get_clean_List(url, groups):
				
				myURL = (f"{url}/JSSResource/computergroups/name/{groups}")
				
				test = http.get(myURL, headers=btHeaders)
				
				if test.status_code != 200:
					list_of_groups.remove(groups)
					
				
			def get_url(url, groups):
				
				print(f"..............Working on Computer Group: {groups}, for Computer ID: " + getMycomputerRecordGeneralID)
				
				myURL = (f"{url}/JSSResource/computergroups/name/{groups}")
				
				try:
					
					computerGroupMembershipNameResponse = http.get(myURL, headers=btHeaders)
					
					computerGroupMembershipNameResponse.raise_for_status()
					
					resp = computerGroupMembershipNameResponse.json()
					
				except HTTPError as http_err:
					
					# Process HTTP Error
					check_http_err = str(http_err)
					split_My_http_err = check_http_err.split()
					
					myHttpError = split_My_http_err[0]
					myMissingRecordID = groups
					myMissingRecordURL = split_My_http_err[5]
					
					if myHttpError == '404':
						print(f".......We found that Record: {myMissingRecordID}, does not exist in your JAMF Instance at URL: {myMissingRecordURL}")
						
					else:
						print(f'HTTP error occurred: {http_err}')
						
				except Exception as err:
					print(f'Other error occurred: {err}')
					
					
				#Set Variables if Data Available
				if len(str(resp['computer_group']['id'])) == 0:
					mygroupMembershipId = ''
				else:
					mygroupMembershipId = int(resp['computer_group']['id'])	
					
					
				groupMembershipName = resp['computer_group']['name']
				groupMembershipIsSmart = resp['computer_group']['is_smart']
				
				
				return mygroupMembershipId, groupMembershipName, groupMembershipIsSmart
			
		
			# Clean List
			with ThreadPoolExecutor(max_workers=100) as pool:
				get_data = partial(get_clean_List, JAMF_url)
				list(pool.map(get_data,list_of_groups))
				
				
			#print(list_of_groups)	
				
				
			# Process List	
			with ThreadPoolExecutor(max_workers=100) as pool:
				get_data = partial(get_url, JAMF_url)
				response_list = list(pool.map(get_data,list_of_groups))
			
				#print(response_list)


			# Renew token because the report is a long process
			# renew token
			tokenURL = JAMF_url + "/api/v1/auth/keep-alive"
			
			token = http.post(tokenURL, headers=btHeaders)
			
			bearer = token.json()['token']
			
			btHeaders = {
				'Accept': 'application/json',
				'Authorization': 'Bearer '+bearer
			}
			
			
			for response in response_list:
				# Make sure to refresh variables for each loop
				myComputerID = mycomputerRecordGeneralID
				myComputerName = mycomputerRecordGeneral['name']
				myGroupMemberID = response[0] 
				myGroupMemberName = response[1] 
				myGroupIsSmart = response[2]
				
				#print(f"My Group info: {response}")	
				
				appendDataToCVS_JAMF_Computers_Info_Computer_Group_Membership = "{'Type':'Computer Group Membership Info',\
				\
				'Computer ID':myComputerID,\
				\
				'Computer Name':myComputerName,\
				\
				'Computer Group Membership Group ID':myGroupMemberID,\
				\
				'Computer Group Membership Group Name':myGroupMemberName,\
				\
				'Computer Group Membership Group Is Smart':myGroupIsSmart}"
				
				
				appendJAMF_Computers_Info_Computer_Group_Membership = eval(appendDataToCVS_JAMF_Computers_Info_Computer_Group_Membership)
				appendComputerGroupMembershipColumns = appendJAMF_Computers_Info_Computer_Group_Membership
				
				#Set Columns	
				Combined = MergeComputersInfo(computerColumns, hardwareColumns, FileVault2Columns, LocalAccountColumns, appendComputerGroupMembershipColumns, computerConfigurationProfileMembershipColumns)
				
				#Set CSV File
				dataToCsvComputers.append(Combined)
				
				
		if get_JAMF_Computers_Info_Computer_Configuration_Profile_Membership == 'yes':
			##########################################################################################		
			# Get info for Computer Configuration Profile Membership	
			##########################################################################################
			print(".......Working on Configuration Profile Membership for Computer ID: " + getMycomputerRecordGeneralID)
			
			#Get Info from record
			computerConfigurationProfileMembership = mycomputerConfigurationProfileMembership
			
			
			list_of_config_profiles_ID = []
			
			for ConfigProfile in computerConfigurationProfileMembership :
				if ConfigProfile['id'] > 0:
					configurationProfileID = str(ConfigProfile['id'])
					list_of_config_profiles_ID.append(f'{configurationProfileID}')
					
					
			def get_clean_List(url, configProfiles):
				
				myURL = (f"{url}/JSSResource/osxconfigurationprofiles/id/{configProfiles}")
				
				test = http.get(myURL, headers=headers, auth = HTTPBasicAuth(username, password))
				
				if test.status_code != 200:
					list_of_config_profiles_ID.remove(configProfiles)
					
					
			def get_url(url, configProfiles):
				
				print(f"..............Working on Configuration Profile ID: {configProfiles}, for Computer ID: " + getMycomputerRecordGeneralID)
				
				myURL = (f"{url}/JSSResource/osxconfigurationprofiles/id/{configProfiles}")
				
				try:
					
					computerConfigurationProfileMembershipResponse = http.get(myURL, headers=headers, auth = HTTPBasicAuth(username, password))
					
					computerConfigurationProfileMembershipResponse.raise_for_status()
					
					resp = computerConfigurationProfileMembershipResponse.json()
					
				except HTTPError as http_err:
					
					# Process HTTP Error
					check_http_err = str(http_err)
					split_My_http_err = check_http_err.split()
					
					myHttpError = split_My_http_err[0]
					myMissingRecordID = configProfiles
					myMissingRecordURL = split_My_http_err[5]
					
					if myHttpError == '404':
						print(f".......We found that Record: {myMissingRecordID}, does not exist in your JAMF Instance at URL: {myMissingRecordURL}")
						
					else:
						print(f'HTTP error occurred: {http_err}')
						
				except Exception as err:
					print(f'Other error occurred: {err}')
					
					
				#General Element for ID and Catagory
				myConfigurationProfileGeneral = resp['os_x_configuration_profile']['general']
				myConfigurationProfileGeneralID = myConfigurationProfileGeneral['id']
				myConfigurationProfileGeneralName = myConfigurationProfileGeneral['name']
				
				
				return myConfigurationProfileGeneralID, myConfigurationProfileGeneralName
			
			
			
			# Clean List
			with ThreadPoolExecutor(max_workers=100) as pool:
				get_data = partial(get_clean_List, JAMF_url)
				list(pool.map(get_data,list_of_config_profiles_ID))
				
				
			#print(list_of_config_profiles_ID)	
				
			# Process List	
			with ThreadPoolExecutor(max_workers=100) as pool:
				get_data = partial(get_url, JAMF_url)
				response_list = list(pool.map(get_data,list_of_config_profiles_ID))
				
			#print(response_list)
				
				
			for response in response_list:
				# Make sure to refresh variables for each loop
				myComputerID = mycomputerRecordGeneralID
				myComputerName = mycomputerRecordGeneral['name']
				myConfigProfileID = response[0] 
				myConfigProfileName = response[1] 
			
				#print(f"My Group info: {response}")
			
				appendDataToCVS_JAMF_Computers_Info_Computer_Configuration_Profile_Membership = "{'Type':'Computer Configuration Profile Membership Info',\
				\
				'Computer ID':myComputerID,\
				\
				'Computer Name':myComputerName,\
				\
				'Computer Configuration Profile Membership ID':myConfigProfileID,\
				\
				'Computer Configuration Profile Membership Name':myConfigProfileName}"
				
				
				appendJAMF_Computers_Info_Computer_Configuration_Profile_Membership = eval(appendDataToCVS_JAMF_Computers_Info_Computer_Configuration_Profile_Membership)
				appendComputerConfigurationProfileMembershipColumns = appendJAMF_Computers_Info_Computer_Configuration_Profile_Membership
				
				#Set Columns	
				Combined = MergeComputersInfo(computerColumns, hardwareColumns, FileVault2Columns, LocalAccountColumns, computerGroupMembershipColumns, appendComputerConfigurationProfileMembershipColumns)
				
				#Set CSV File
				dataToCsvComputers.append(Combined)
			
		
	else:		
		
		#Run for smart group on no filter
		for computerRecord in computerRecords:
			
			# Get ID to do JAMF API lookup
			computerRecordID = str(computerRecord['id'])
			
			#For Testing
			#print(computerRecordID)
			
			# Set up url for getting information from each configurationProfile ID from JAMF API
			url = JAMF_url + "/JSSResource/computers/id/" + computerRecordID
			
			try:
				response = http.get(url, headers=btHeaders)
				
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
			mycomputerRecordComputerGroupMembership = computerRecordProfile['computer']['groups_accounts']['computer_group_memberships']
			mycomputerConfigurationProfileMembership = computerRecordProfile['computer']['configuration_profiles']
			
			
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
			if usingFilter == 'computerFilter':
				
				appendDataToCVS_JAMF_Computers_Info = "{'Type':'Computer Info',\
				\
				'Computer ID':mycomputerRecordGeneralID,\
				\
				'Computer Name':mycomputerRecordGeneral['name'],\
				\
				'Computer Serial Number':str(mycomputerRecordGeneral['serial_number']),\
				\
				'Computer Last Check-in':str(mycomputerRecordGeneral['last_contact_time']),\
				\
				'Computer Site Info':str(mycomputerRecordGeneral['site']['name'])}"
				
			elif usingFilter == 'smartGroupFilter':
				
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
				'Computer Serial Number':str(mycomputerRecordGeneral['serial_number']),\
				\
				'Computer Last Check-in':str(mycomputerRecordGeneral['last_contact_time']),\
				\
				'Computer Site Info':str(mycomputerRecordGeneral['site']['name'])}"
				
			elif usingFilter == 'noFilter':
				
				appendDataToCVS_JAMF_Computers_Info = "{'Type':'Computer Info',\
				\
				'Computer ID':mycomputerRecordGeneralID,\
				\
				'Computer Name':mycomputerRecordGeneral['name'],\
				\
				'Computer Serial Number':str(mycomputerRecordGeneral['serial_number']),\
				\
				'Computer Last Check-in':str(mycomputerRecordGeneral['last_contact_time']),\
				\
				'Computer Site Info':str(mycomputerRecordGeneral['site']['name'])}"
				
				
			appendJAMF_Computers_Info = eval(appendDataToCVS_JAMF_Computers_Info)
			appendComputerColumns = appendJAMF_Computers_Info
			
			#Set Columns	
			Combined = MergeComputersInfo(appendComputerColumns, hardwareColumns, FileVault2Columns, LocalAccountColumns, computerGroupMembershipColumns, computerConfigurationProfileMembershipColumns)
			
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
				Combined = MergeComputersInfo(computerColumns, appendComputerHardwareColumns, FileVault2Columns, LocalAccountColumns, computerGroupMembershipColumns, computerConfigurationProfileMembershipColumns)
				
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
					Combined = MergeComputersInfo(computerColumns, hardwareColumns, appendComputerFileVault2Columns, LocalAccountColumns, computerGroupMembershipColumns, computerConfigurationProfileMembershipColumns)
					
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
									response = http.get(url, headers=btHeaders)
									
									response.raise_for_status()
									
									verifyLocalAccount = response.json()
									
								except HTTPError as http_err:
									# Process HTTP Error
									check_http_err = str(http_err)
									split_My_http_err = check_http_err.split()
									
									myHttpError = split_My_http_err[0]
									myMissingRecordID = filterComputerLocalAccountData
									myMissingRecordURL = split_My_http_err[5]
									
									if myHttpError == '404':
										print(f".......We found that Record: {myMissingRecordID}, does not exist in your JAMF Instance at URL: {myMissingRecordURL}")
										
									else:
										print(f'HTTP error occurred: {http_err}')
										
									continue
								except Exception as err:
									print(f'Other error occurred: {err}')
									continue
									
								
								# For Testing
								#print(verifyLocalAccount)
								
								verifidLocalAccountRecords = verifyLocalAccount['ldap_users']
								#verifidLocalAccountRecords.sort(key=lambda item: item.get('id'), reverse=False)
								
								for localAccountRecord in verifidLocalAccountRecords :
									
									#print(localAccountRecord['username'])
									
									#Set Variables if Data Available
									if len(str(localAccountRecord['uid'])) == 0:
										computerLocalAccountUID = ''
									else:
										computerLocalAccountUID = int(localAccountRecord['uid'])
										
									
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
							Combined = MergeComputersInfo(computerColumns, hardwareColumns, FileVault2Columns, appendLocalAccountColumns, computerGroupMembershipColumns, computerConfigurationProfileMembershipColumns)
						
							#Set CSV File
							dataToCsvComputers.append(Combined)	
							
							
			if get_JAMF_Computers_Info_Computer_Group_Membership == 'yes':
				##########################################################################################		
				# Get info for Computer Group Membership	
				##########################################################################################
				print(".......Getting Computer Group Info for Computer ID: " + getMycomputerRecordGeneralID)
				
				#Get Info from record
				computerGroupMembershipRecords = mycomputerRecordComputerGroupMembership
				
				
				list_of_groups = []
				
				for groupName in computerGroupMembershipRecords :
					list_of_groups.append(f'{groupName}')
					
					
				# Renew token because the report is a long process
				# renew token
				tokenURL = JAMF_url + "/api/v1/auth/keep-alive"
				
				token = http.post(tokenURL, headers=btHeaders)
				
				bearer = token.json()['token']
				
				btHeaders = {
					'Accept': 'application/json',
					'Authorization': 'Bearer '+bearer
				}
				
				
				def get_clean_List(url, groups):
					
					myURL = (f"{url}/JSSResource/computergroups/name/{groups}")
					
					test = http.get(myURL, headers=btHeaders)
					
					if test.status_code != 200:
						list_of_groups.remove(groups)
						
						
				def get_url(url, groups):
					
					print(f"..............Working on Computer Group: {groups}, for Computer ID: " + getMycomputerRecordGeneralID)
					
					myURL = (f"{url}/JSSResource/computergroups/name/{groups}")
					
					try:
						
						computerGroupMembershipNameResponse = http.get(myURL, headers=btHeaders)
						
						computerGroupMembershipNameResponse.raise_for_status()
						
						resp = computerGroupMembershipNameResponse.json()
						
					except HTTPError as http_err:
						
						# Process HTTP Error
						check_http_err = str(http_err)
						split_My_http_err = check_http_err.split()
						
						myHttpError = split_My_http_err[0]
						myMissingRecordID = groups
						myMissingRecordURL = split_My_http_err[5]
						
						if myHttpError == '404':
							print(f".......We found that Record: {myMissingRecordID}, does not exist in your JAMF Instance at URL: {myMissingRecordURL}")
							
						else:
							print(f'HTTP error occurred: {http_err}')
							
					except Exception as err:
						print(f'Other error occurred: {err}')
						
						
					#Set Variables if Data Available
					if len(str(resp['computer_group']['id'])) == 0:
						mygroupMembershipId = ''
					else:
						mygroupMembershipId = int(resp['computer_group']['id'])	
						
						
					groupMembershipName = resp['computer_group']['name']
					groupMembershipIsSmart = resp['computer_group']['is_smart']
					
					
					return mygroupMembershipId, groupMembershipName, groupMembershipIsSmart
				
				
				# Clean List
				with ThreadPoolExecutor(max_workers=100) as pool:
					get_data = partial(get_clean_List, JAMF_url)
					list(pool.map(get_data,list_of_groups))
					
					
				#print(list_of_groups)	
					
					
				# Process List	
				with ThreadPoolExecutor(max_workers=100) as pool:
					get_data = partial(get_url, JAMF_url)
					response_list = list(pool.map(get_data,list_of_groups))
					
					#print(response_list)
					
					
				# Renew token because the report is a long process
				# renew token
				tokenURL = JAMF_url + "/api/v1/auth/keep-alive"
				
				token = http.post(tokenURL, headers=btHeaders)
				
				bearer = token.json()['token']
				
				btHeaders = {
					'Accept': 'application/json',
					'Authorization': 'Bearer '+bearer
				}
				
				
				for response in response_list:
					# Make sure to refresh variables for each loop
					myComputerID = mycomputerRecordGeneralID
					myComputerName = mycomputerRecordGeneral['name']
					myGroupMemberID = response[0] 
					myGroupMemberName = response[1] 
					myGroupIsSmart = response[2]
					
					#print(f"My Group info: {response}")	
					
					appendDataToCVS_JAMF_Computers_Info_Computer_Group_Membership = "{'Type':'Computer Group Membership Info',\
					\
					'Computer ID':myComputerID,\
					\
					'Computer Name':myComputerName,\
					\
					'Computer Group Membership Group ID':myGroupMemberID,\
					\
					'Computer Group Membership Group Name':myGroupMemberName,\
					\
					'Computer Group Membership Group Is Smart':myGroupIsSmart}"
					
					
					appendJAMF_Computers_Info_Computer_Group_Membership = eval(appendDataToCVS_JAMF_Computers_Info_Computer_Group_Membership)
					appendComputerGroupMembershipColumns = appendJAMF_Computers_Info_Computer_Group_Membership
					
					#Set Columns	
					Combined = MergeComputersInfo(computerColumns, hardwareColumns, FileVault2Columns, LocalAccountColumns, appendComputerGroupMembershipColumns, computerConfigurationProfileMembershipColumns)
					
					#Set CSV File
					dataToCsvComputers.append(Combined)
					
					
					
			if get_JAMF_Computers_Info_Computer_Configuration_Profile_Membership == 'yes':
				##########################################################################################		
				# Get info for Computer Configuration Profile Membership	
				##########################################################################################
				print(".......Working on Configuration Profile Membership for Computer ID: " + getMycomputerRecordGeneralID)
				
				#Get Info from record
				computerConfigurationProfileMembership = mycomputerConfigurationProfileMembership
				

				
				list_of_config_profiles_ID = []
				
				for ConfigProfile in computerConfigurationProfileMembership :
					if ConfigProfile['id'] > 0:
						configurationProfileID = str(ConfigProfile['id'])
						list_of_config_profiles_ID.append(f'{configurationProfileID}')
						
						
				def get_clean_List(url, configProfiles):
					
					myURL = (f"{url}/JSSResource/osxconfigurationprofiles/id/{configProfiles}")
					
					test = http.get(myURL, headers=headers, auth = HTTPBasicAuth(username, password))
					
					if test.status_code != 200:
						list_of_config_profiles_ID.remove(configProfiles)
						
						
				def get_url(url, configProfiles):
					
					print(f"..............Working on Configuration Profile ID: {configProfiles}, for Computer ID: " + getMycomputerRecordGeneralID)
					
					myURL = (f"{url}/JSSResource/osxconfigurationprofiles/id/{configProfiles}")
					
					try:
						
						computerConfigurationProfileMembershipResponse = http.get(myURL, headers=headers, auth = HTTPBasicAuth(username, password))
						
						computerConfigurationProfileMembershipResponse.raise_for_status()
						
						resp = computerConfigurationProfileMembershipResponse.json()
						
					except HTTPError as http_err:
						
						# Process HTTP Error
						check_http_err = str(http_err)
						split_My_http_err = check_http_err.split()
						
						myHttpError = split_My_http_err[0]
						myMissingRecordID = configProfiles
						myMissingRecordURL = split_My_http_err[5]
						
						if myHttpError == '404':
							print(f".......We found that Record: {myMissingRecordID}, does not exist in your JAMF Instance at URL: {myMissingRecordURL}")
							
						else:
							print(f'HTTP error occurred: {http_err}')
							
					except Exception as err:
						print(f'Other error occurred: {err}')
						
						
					#General Element for ID and Catagory
					myConfigurationProfileGeneral = resp['os_x_configuration_profile']['general']
					myConfigurationProfileGeneralID = myConfigurationProfileGeneral['id']
					myConfigurationProfileGeneralName = myConfigurationProfileGeneral['name']
					
					
					return myConfigurationProfileGeneralID, myConfigurationProfileGeneralName
				
				
				
				# Clean List
				with ThreadPoolExecutor(max_workers=100) as pool:
					get_data = partial(get_clean_List, JAMF_url)
					list(pool.map(get_data,list_of_config_profiles_ID))
					
					
				#print(list_of_config_profiles_ID)	
					
				# Process List	
				with ThreadPoolExecutor(max_workers=100) as pool:
					get_data = partial(get_url, JAMF_url)
					response_list = list(pool.map(get_data,list_of_config_profiles_ID))
					
				#print(response_list)
					
					
				for response in response_list:
					# Make sure to refresh variables for each loop
					myComputerID = mycomputerRecordGeneralID
					myComputerName = mycomputerRecordGeneral['name']
					myConfigProfileID = response[0] 
					myConfigProfileName = response[1] 
					
					#print(f"My Group info: {response}")
					
					appendDataToCVS_JAMF_Computers_Info_Computer_Configuration_Profile_Membership = "{'Type':'Computer Configuration Profile Membership Info',\
					\
					'Computer ID':myComputerID,\
					\
					'Computer Name':myComputerName,\
					\
					'Computer Configuration Profile Membership ID':myConfigProfileID,\
					\
					'Computer Configuration Profile Membership Name':myConfigProfileName}"
					
					
					appendJAMF_Computers_Info_Computer_Configuration_Profile_Membership = eval(appendDataToCVS_JAMF_Computers_Info_Computer_Configuration_Profile_Membership)
					appendComputerConfigurationProfileMembershipColumns = appendJAMF_Computers_Info_Computer_Configuration_Profile_Membership
					
					#Set Columns	
					Combined = MergeComputersInfo(computerColumns, hardwareColumns, FileVault2Columns, LocalAccountColumns, computerGroupMembershipColumns, appendComputerConfigurationProfileMembershipColumns)
					
					#Set CSV File
					dataToCsvComputers.append(Combined)
						
				
				
##################################################
# Process Requested Info for Policies
##################################################

if get_JAMF_Policy_Info == ("yes"):
	# Set up url for getting a list of all policies from JAMF API
	url = JAMF_url + "/JSSResource/policies"
	
	try:
		response = http.get(url, headers=btHeaders)
		
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
	
	
	list_of_policies = []
	
	for policy in policies :
		PolicyID = str(policy['id']) 
		list_of_policies.append(f'{PolicyID}')
		
		
	#Renew token because the report is a long process
	#renew token
	url = JAMF_url+"/api/v1/auth/keep-alive"
	
	token = http.post(url, headers=btHeaders)
	
	bearer = token.json()['token']
	
	btHeaders = {
		'Accept': 'application/json',
		'Authorization': 'Bearer '+bearer
	}
	
	
	def get_clean_List(url, policyIDList):
		
		myURL = (f"{url}/JSSResource/policies/id/{policyIDList}")
		
		test = http.get(myURL, headers=btHeaders)
		
		if test.status_code != 200:
			list_of_policies.remove(policyIDList)
			
			
			
	def get_url(url, policyIDList):
		
		getPolicy = ''
		
		myURL = (f"{url}/JSSResource/policies/id/{policyIDList}")
		
		try:
			
			response = http.get(myURL, headers=btHeaders)
			
			response.raise_for_status()
			
			getPolicy = response.json()
			
		except HTTPError as http_err:
			
			# Process HTTP Error
			check_http_err = str(http_err)
			split_My_http_err = check_http_err.split()
			
			myHttpError = split_My_http_err[0]
			myMissingRecordID = policyIDList
			myMissingRecordURL = split_My_http_err[5]
			
			if myHttpError == '404':
				print(f".......We found that Record: {myMissingRecordID}, does not exist in your JAMF Instance at URL: {myMissingRecordURL}")
				
			else:
				print(f'HTTP error occurred: {http_err}')
				
		except Exception as err:
			print(f'Other error occurred: {err}')
			
			
		return getPolicy
	
	
	# Clean List
	with ThreadPoolExecutor(max_workers=100) as pool:
		get_data = partial(get_clean_List, JAMF_url)
		list(pool.map(get_data,list_of_policies))
		
		
	#print(list_of_policies)
		
		
	#Renew token because the report is a long process
	#renew token
	url = JAMF_url+"/api/v1/auth/keep-alive"
	
	token = http.post(url, headers=btHeaders)
	
	bearer = token.json()['token']
	
	btHeaders = {
		'Accept': 'application/json',
		'Authorization': 'Bearer '+bearer
	}
	
	
	# Process List	
	with ThreadPoolExecutor(max_workers=100) as pool:
		get_data = partial(get_url, JAMF_url)
		response_list = list(pool.map(get_data,list_of_policies))
		
		#print(response_list)
		
		
	#Renew token because the report is a long process
	#renew token
	url = JAMF_url+"/api/v1/auth/keep-alive"
	
	token = http.post(url, headers=btHeaders)
	
	bearer = token.json()['token']
	
	btHeaders = {
		'Accept': 'application/json',
		'Authorization': 'Bearer '+bearer
	}
	
	
	def processData(response):
		global btHeaders
	##	# Make sure to refresh variables for each loop
		#General Element for ID and Catagory
		myPolicyGeneral = response['policy']['general']
		myPolicyGeneralCatagory = response['policy']['general']['category']
		
		#Scope Element for Computer Targets
		myPolicyScopeTargetsAllComputers = response['policy']['scope']['all_computers']
		myPolicyScopeTargetsComputers = response['policy']['scope']['computers']
		myPolicyScopeTargetsComputerGroups = response['policy']['scope']['computer_groups']
		
		#Scope Element For Limitation
		#myPolicyScopeLimitationsUsers = getPolicy['policy']['scope']['limitations']['users']
		#myPolicyScopeLimitationsUserGroups = getPolicy['policy']['scope']['limitations']['user_groups']
		
		#Scope Element For Exclusions
		myPolicyScopeExclusionsComputers = response['policy']['scope']['exclusions']['computers']
		myPolicyScopeExclusionsComputerGroups = response['policy']['scope']['exclusions']['computer_groups']
		
		
		#Package Element
		myPackagesInfo = response['policy']['package_configuration']['packages']
		
		
		#Script Elements
		myScriptInfo = response['policy']['scripts']
		
		#SelfService Element
		mySelfServiceInfo = response['policy']['self_service']
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
			#Renew token because the report is a long process
			#renew token
			url = JAMF_url+"/api/v1/auth/keep-alive"
			
			token = http.post(url, headers=btHeaders)
			
			bearer = token.json()['token']
			
			btHeaders = {
				'Accept': 'application/json',
				'Authorization': 'Bearer '+bearer
			}
			
			
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
			#Renew token because the report is a long process
			#renew token
			url = JAMF_url+"/api/v1/auth/keep-alive"
			
			token = http.post(url, headers=btHeaders)
			
			bearer = token.json()['token']
			
			btHeaders = {
				'Accept': 'application/json',
				'Authorization': 'Bearer '+bearer
			}
			
			
			for computer in myPolicyScopeTargetsComputers:
				
				#Set Variables if Data Available
				if len(str(computer['id'])) == 0:
					computerID = ''
				else:
					computerID = int(computer['id'])
					
				# Get info for Policies
				print(f"Working on Computer ID: {computerID}")
				
				
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
			# Start New MultiProcess Code here
				
			list_of_Targets = []
			
			for target in myPolicyScopeTargetsComputerGroups:
				targetID = str(target['id']) 
				list_of_Targets.append(f'{targetID}')
				
				
			#Renew token because the report is a long process
			#renew token
			url = JAMF_url+"/api/v1/auth/keep-alive"
			
			token = http.post(url, headers=btHeaders)
			
			bearer = token.json()['token']
			
			btHeaders = {
				'Accept': 'application/json',
				'Authorization': 'Bearer '+bearer
			}
			
			
			def get_clean_List(url, targetIDList):
				
				myURL = (f"{url}/JSSResource/computergroups/id/{targetIDList}")
				
				test = http.get(myURL, headers=btHeaders)
				
				if test.status_code != 200:
					list_of_Targets.remove(targetIDList)
					
					
					
			def get_url(url, targetIDList):
				
				getTargetGroupData = ''
				
				myURL = (f"{url}/JSSResource/computergroups/id/{targetIDList}")
				
				try:
					
					response = http.get(myURL, headers=btHeaders)
					
					response.raise_for_status()
					
					getTargetGroupData = response.json()
					
				except HTTPError as http_err:
					
					# Process HTTP Error
					check_http_err = str(http_err)
					split_My_http_err = check_http_err.split()
					
					myHttpError = split_My_http_err[0]
					myMissingRecordID = targetIDList
					myMissingRecordURL = split_My_http_err[5]
					
					if myHttpError == '404':
						print(f".......We found that Record: {myMissingRecordID}, does not exist in your JAMF Instance at URL: {myMissingRecordURL}")
						
					else:
						print(f'HTTP error occurred: {http_err}')
						
				except Exception as err:
					print(f'Other error occurred: {err}')
					
					
				return getTargetGroupData
			
			
			# Clean List
			with ThreadPoolExecutor(max_workers=100) as pool:
				get_data = partial(get_clean_List, JAMF_url)
				list(pool.map(get_data,list_of_Targets))
				
				
			#print(list_of_policies)	
				
				
			#Renew token because the report is a long process
			#renew token
			url = JAMF_url+"/api/v1/auth/keep-alive"
			
			token = http.post(url, headers=btHeaders)
			
			bearer = token.json()['token']
			
			btHeaders = {
				'Accept': 'application/json',
				'Authorization': 'Bearer '+bearer
			}
			
			
			# Process List	
			with ThreadPoolExecutor(max_workers=100) as pool:
				get_data = partial(get_url, JAMF_url)
				response_list = list(pool.map(get_data,list_of_Targets))
				
				
			#print(response_list)
			
			
			for response in response_list:
			##	# Make sure to refresh variables for each loop
				myTargetsComputerGroupInfo = response['computer_group']
				
				
				#Set Variables if Data Available
				if len(str(myTargetsComputerGroupInfo['id'])) == 0:
					myTargetsComputerGroupInfoID = ''
				else:
					myTargetsComputerGroupInfoID = int(myTargetsComputerGroupInfo['id'])
					
				# Get info for Policies
				print(f"Working on Target Group ID: {myTargetsComputerGroupInfoID}")
				
				
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
			#Renew token because the report is a long process
			#renew token
			url = JAMF_url+"/api/v1/auth/keep-alive"
			
			token = http.post(url, headers=btHeaders)
			
			bearer = token.json()['token']
			
			btHeaders = {
				'Accept': 'application/json',
				'Authorization': 'Bearer '+bearer
			}
			
			
			for exclusion in myPolicyScopeExclusionsComputers:
				
				#Set Variables if Data Available
				if len(str(exclusion['id'])) == 0:
					exclusionID = ''
				else:
					exclusionID = int(exclusion['id'])
					
				# Get info for Policies
				print(f"Working on Target Group ID: {exclusionID}")
				
				
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
			# Start New MultiProcess Code here
				
			list_of_Exclusions = []
			
			for exclusion in myPolicyScopeExclusionsComputerGroups:
				exclusionID = str(exclusion['id']) 
				list_of_Exclusions.append(f'{exclusionID}')
				
				
			#Renew token because the report is a long process
			#renew token
			url = JAMF_url+"/api/v1/auth/keep-alive"
			
			token = http.post(url, headers=btHeaders)
			
			bearer = token.json()['token']
			
			btHeaders = {
				'Accept': 'application/json',
				'Authorization': 'Bearer '+bearer
			}
			
			
			def get_clean_List(url, exclusionIDList):
				
				myURL = (f"{url}/JSSResource/computergroups/id/{exclusionIDList}")
				
				test = http.get(myURL, headers=btHeaders)
				
				if test.status_code != 200:
					list_of_Exclusions.remove(exclusionIDList)
					
					
					
			def get_url(url, exclusionIDList):
				
				getExclusionGroupData = ''
				
				myURL = (f"{url}/JSSResource/computergroups/id/{exclusionIDList}")
				
				try:
					
					response = http.get(myURL, headers=btHeaders)
					
					response.raise_for_status()
					
					getExclusionGroupData = response.json()
					
				except HTTPError as http_err:
					
					# Process HTTP Error
					check_http_err = str(http_err)
					split_My_http_err = check_http_err.split()
					
					myHttpError = split_My_http_err[0]
					myMissingRecordID = exclusionIDList
					myMissingRecordURL = split_My_http_err[5]
					
					if myHttpError == '404':
						print(f".......We found that Record: {myMissingRecordID}, does not exist in your JAMF Instance at URL: {myMissingRecordURL}")
						
					else:
						print(f'HTTP error occurred: {http_err}')
						
				except Exception as err:
					print(f'Other error occurred: {err}')
					
					
				return getExclusionGroupData
			
			
			# Clean List
			with ThreadPoolExecutor(max_workers=100) as pool:
				get_data = partial(get_clean_List, JAMF_url)
				list(pool.map(get_data,list_of_Exclusions))
				
				
			#print(list_of_policies)	
				
				
			#Renew token because the report is a long process
			#renew token
			url = JAMF_url+"/api/v1/auth/keep-alive"
			
			token = http.post(url, headers=btHeaders)
			
			bearer = token.json()['token']
			
			btHeaders = {
				'Accept': 'application/json',
				'Authorization': 'Bearer '+bearer
			}
			
			
			# Process List	
			with ThreadPoolExecutor(max_workers=100) as pool:
				get_data = partial(get_url, JAMF_url)
				response_list = list(pool.map(get_data,list_of_Exclusions))
				
				
			#print(response_list)
			
			
			for response in response_list:
			##	# Make sure to refresh variables for each loop
				myExclusionsComputerGroupInfo = response['computer_group']
				
				#Set Variables if Data Available
				if len(str(myExclusionsComputerGroupInfo['id'])) == 0:
					myExclusionsComputerGroupInfoID = ''
				else:
					myExclusionsComputerGroupInfoID = int(myExclusionsComputerGroupInfo['id'])
					
				# Get info for Policies
				print(f"Working on Exclusion Group ID: {myExclusionsComputerGroupInfoID}")
				
				
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
			#Renew token because the report is a long process
			#renew token
			url = JAMF_url+"/api/v1/auth/keep-alive"
			
			token = http.post(url, headers=btHeaders)
			
			bearer = token.json()['token']
			
			btHeaders = {
				'Accept': 'application/json',
				'Authorization': 'Bearer '+bearer
			}
			
			
			# Start New MultiProcess Code here
			
			list_of_Packages = []
			
			for package in myPackagesInfo:
				packageID = str(package['id']) 
				list_of_Packages.append(f'{packageID}')
				
				
			def get_clean_List(url, packageIDList):
				
				myURL = (f"{url}/JSSResource/packages/id/{packageIDList}")
				
				test = http.get(myURL, headers=btHeaders)
				
				if test.status_code != 200:
					list_of_Packages.remove(packageIDList)
					
					
					
			def get_url(url, packageIDList):
				
				getPackageData = ''
				
				myURL = (f"{url}/JSSResource/packages/id/{packageIDList}")
				
				try:
					
					response = http.get(myURL, headers=btHeaders)
					
					response.raise_for_status()
					
					getPackageData = response.json()
					
				except HTTPError as http_err:
					
					# Process HTTP Error
					check_http_err = str(http_err)
					split_My_http_err = check_http_err.split()
					
					myHttpError = split_My_http_err[0]
					myMissingRecordID = packageIDList
					myMissingRecordURL = split_My_http_err[5]
					
					if myHttpError == '404':
						print(f".......We found that Record: {myMissingRecordID}, does not exist in your JAMF Instance at URL: {myMissingRecordURL}")
						
					else:
						print(f'HTTP error occurred: {http_err}')
						
				except Exception as err:
					print(f'Other error occurred: {err}')
					
					
				return getPackageData
			
			
			# Clean List
			with ThreadPoolExecutor(max_workers=100) as pool:
				get_data = partial(get_clean_List, JAMF_url)
				list(pool.map(get_data,list_of_Packages))
				
				
			#print(list_of_policies)
				
				
			#Renew token because the report is a long process
			#renew token
			url = JAMF_url+"/api/v1/auth/keep-alive"
			
			token = http.post(url, headers=btHeaders)
			
			bearer = token.json()['token']
			
			btHeaders = {
				'Accept': 'application/json',
				'Authorization': 'Bearer '+bearer
			}
			
			
			# Process List	
			with ThreadPoolExecutor(max_workers=100) as pool:
				get_data = partial(get_url, JAMF_url)
				response_list = list(pool.map(get_data,list_of_Packages))
				
				
			#print(response_list)
			
			
			for response in response_list:
				myPackageInfo = response['package']
				
				formatMyPackageInfoCatagory = f"\"{myPackageInfo['category']}\""
				
				#Set Variables if Data Available
				if len(str(myPackageInfo['id'])) == 0:
					myPackageInfoID = ''
				else:
					myPackageInfoID = int(myPackageInfo['id'])
					
					
				# Get info for Policies
				print(f"Working on Package ID: {myPackageInfoID}")
				
				
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
			#Renew token because the report is a long process
			#renew token
			url = JAMF_url+"/api/v1/auth/keep-alive"
			
			token = http.post(url, headers=btHeaders)
			
			bearer = token.json()['token']
			
			btHeaders = {
				'Accept': 'application/json',
				'Authorization': 'Bearer '+bearer
			}
			
			
			# Start New MultiProcess Code here
			
			list_of_Scripts = []
			
			for script in myScriptInfo:
				scriptID = str(script['id'])
				list_of_Scripts.append(f'{scriptID}')
				
				
			#Renew token because the report is a long process
			#renew token
			url = JAMF_url+"/api/v1/auth/keep-alive"
			
			token = http.post(url, headers=btHeaders)
			
			bearer = token.json()['token']
			
			btHeaders = {
				'Accept': 'application/json',
				'Authorization': 'Bearer '+bearer
			}
			
			
			def get_clean_List(url, scriptIDList):
				
				myURL = (f"{url}/JSSResource/scripts/id/{scriptIDList}")
				
				test = http.get(myURL, headers=btHeaders)
				
				if test.status_code != 200:
					list_of_Scripts.remove(scriptIDList)
					
					
					
			def get_url(url, scriptIDList):
				
				getScriptData = ''
				
				myURL = (f"{url}/JSSResource/scripts/id/{scriptIDList}")
				
				try:
					
					response = http.get(myURL, headers=btHeaders)
					
					response.raise_for_status()
					
					getScriptData = response.json()
					
				except HTTPError as http_err:
					
					# Process HTTP Error
					check_http_err = str(http_err)
					split_My_http_err = check_http_err.split()
					
					myHttpError = split_My_http_err[0]
					myMissingRecordID = scriptIDList
					myMissingRecordURL = split_My_http_err[5]
					
					if myHttpError == '404':
						print(f".......We found that Record: {myMissingRecordID}, does not exist in your JAMF Instance at URL: {myMissingRecordURL}")
						
					else:
						print(f'HTTP error occurred: {http_err}')
						
				except Exception as err:
					print(f'Other error occurred: {err}')
					
					
				return getScriptData
			
			
			# Clean List
			with ThreadPoolExecutor(max_workers=100) as pool:
				get_data = partial(get_clean_List, JAMF_url)
				list(pool.map(get_data,list_of_Scripts))
				
				
			#print(list_of_policies)	
				
				
			#Renew token because the report is a long process
			#renew token
			url = JAMF_url+"/api/v1/auth/keep-alive"
			
			token = http.post(url, headers=btHeaders)
			
			bearer = token.json()['token']
			
			btHeaders = {
				'Accept': 'application/json',
				'Authorization': 'Bearer '+bearer
			}
			
			
			# Process List	
			with ThreadPoolExecutor(max_workers=100) as pool:
				get_data = partial(get_url, JAMF_url)
				response_list = list(pool.map(get_data,list_of_Scripts))
				
				
			#print(response_list)
						
			
			for response in response_list:
				myScriptInfo = response['script']
				
				formatMyScriptsinfoCatagory = f"\"{myScriptInfo['category']}\""
				
				#Set Variables if Data Available
				if len(str(myScriptInfo['id'])) == 0:
					myScriptInfoID = ''
				else:
					myScriptInfoID = int(myScriptInfo['id'])
					
				# Get info for Policies
				print(f"Working on Script ID: {myScriptInfoID}")
				
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
				
				
	#Renew token because the report is a long process
	#renew token
	url = JAMF_url+"/api/v1/auth/keep-alive"
	
	token = http.post(url, headers=btHeaders)
	
	bearer = token.json()['token']
	
	btHeaders = {
		'Accept': 'application/json',
		'Authorization': 'Bearer '+bearer
	}
	
	
	# Process List
	with ThreadPoolExecutor(max_workers=100) as pool:
		list(pool.map(processData,response_list))


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
		response = http.get(url, headers=btHeaders)
		
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
	

	
	list_of_configuration_profiles = []
	
	for configurationProfile in configurationProfiles :
		configurationProfileID = str(configurationProfile['id']) 
		list_of_configuration_profiles.append(f'{configurationProfileID}')
		
		
		#Renew token because the report is a long process
		#renew token
	url = JAMF_url+"/api/v1/auth/keep-alive"
	
	token = http.post(url, headers=btHeaders)
	
	bearer = token.json()['token']
	
	btHeaders = {
		'Accept': 'application/json',
		'Authorization': 'Bearer '+bearer
	}
	
	
	def get_clean_List(url, configurationProfileIDList):
		
		myURL = (f"{url}/JSSResource/osxconfigurationprofiles/id/{configurationProfileIDList}")
		
		test = http.get(myURL, headers=btHeaders)
		
		if test.status_code != 200:
			list_of_configuration_profiles.remove(configurationProfileIDList)
			
			
			
	def get_url(url, configurationProfileIDList):
		
		getConfigurationProfile = ''
		
		myURL = (f"{url}/JSSResource/osxconfigurationprofiles/id/{configurationProfileIDList}")
		
		try:
			
			response = http.get(myURL, headers=btHeaders)
			
			response.raise_for_status()
			
			getConfigurationProfile = response.json()
			
		except HTTPError as http_err:
			
			# Process HTTP Error
			check_http_err = str(http_err)
			split_My_http_err = check_http_err.split()
			
			myHttpError = split_My_http_err[0]
			myMissingRecordID = configurationProfileIDList
			myMissingRecordURL = split_My_http_err[5]
			
			if myHttpError == '404':
				print(f".......We found that Record: {myMissingRecordID}, does not exist in your JAMF Instance at URL: {myMissingRecordURL}")
				
			else:
				print(f'HTTP error occurred: {http_err}')
				
		except Exception as err:
			print(f'Other error occurred: {err}')
			
			
		return getConfigurationProfile
	
	
	# Clean List
	with ThreadPoolExecutor(max_workers=100) as pool:
		get_data = partial(get_clean_List, JAMF_url)
		list(pool.map(get_data,list_of_configuration_profiles))
		
		
	#print(list_of_policies)
		
		
	#Renew token because the report is a long process
	#renew token
	url = JAMF_url+"/api/v1/auth/keep-alive"
	
	token = http.post(url, headers=btHeaders)
	
	bearer = token.json()['token']
	
	btHeaders = {
		'Accept': 'application/json',
		'Authorization': 'Bearer '+bearer
	}
	
	
	# Process List	
	with ThreadPoolExecutor(max_workers=100) as pool:
		get_data = partial(get_url, JAMF_url)
		response_list = list(pool.map(get_data,list_of_configuration_profiles))
		
		#print(response_list)
		
		
	#Renew token because the report is a long process
	#renew token
	url = JAMF_url+"/api/v1/auth/keep-alive"
	
	token = http.post(url, headers=btHeaders)
	
	bearer = token.json()['token']
	
	btHeaders = {
		'Accept': 'application/json',
		'Authorization': 'Bearer '+bearer
	}
	
	
	def processData(response):
		global btHeaders
		# Make sure to refresh variables for each loop
		#General Element for ID and Catagory
		myConfigurationProfileGeneral = response['os_x_configuration_profile']['general']
		myConfigurationProfileGeneralCatagory = response['os_x_configuration_profile']['general']['category']
		
		#Scope Element for Computer Targets
		myConfigurationProfileScopeTargetsAllComputers = response['os_x_configuration_profile']['scope']['all_computers']
		myConfigurationProfileScopeTargetsComputers = response['os_x_configuration_profile']['scope']['computers']
		myConfigurationProfileScopeTargetsComputerGroups = response['os_x_configuration_profile']['scope']['computer_groups']
		
		#Scope Element For Limitation
		myConfigurationProfileScopeLimitationsUsers = response['os_x_configuration_profile']['scope']['limitations']['users']
		myConfigurationProfileScopeLimitationsUserGroups = response['os_x_configuration_profile']['scope']['limitations']['user_groups']
		
		#Scope Element For Exclusions
		myConfigurationProfileScopeExclusionsComputers = response['os_x_configuration_profile']['scope']['exclusions']['computers']
		myConfigurationProfileScopeExclusionsComputerGroups = response['os_x_configuration_profile']['scope']['exclusions']['computer_groups']
		
		
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
			#Renew token because the report is a long process
			#renew token
			url = JAMF_url+"/api/v1/auth/keep-alive"
			
			token = http.post(url, headers=btHeaders)
			
			bearer = token.json()['token']
			
			btHeaders = {
				'Accept': 'application/json',
				'Authorization': 'Bearer '+bearer
			}
			
			
			for computer in myConfigurationProfileScopeTargetsComputers:
				
				#Set Variables if Data Available
				if len(str(computer['id'])) == 0:
					computerID = ''
				else:
					computerID = int(computer['id'])
					
				# Get info for Policies
				print(f"Working on Computer ID: {computerID}")
				
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
				'Configuration Profile Target Computer ID':computer['id'],\
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
			# Start New MultiProcess Code here
				
			list_of_Targets = []
			
			for target in myConfigurationProfileScopeTargetsComputerGroups:
				targetID = str(target['id']) 
				list_of_Targets.append(f'{targetID}')
				
				
			#Renew token because the report is a long process
			#renew token
			url = JAMF_url+"/api/v1/auth/keep-alive"
			
			token = http.post(url, headers=btHeaders)
			
			bearer = token.json()['token']
			
			btHeaders = {
				'Accept': 'application/json',
				'Authorization': 'Bearer '+bearer
			}
			
			
			def get_clean_List(url, targetIDList):
				
				myURL = (f"{url}/JSSResource/computergroups/id/{targetIDList}")
				
				test = http.get(myURL, headers=btHeaders)
				
				if test.status_code != 200:
					list_of_Targets.remove(targetIDList)
					
					
					
			def get_url(url, targetIDList):
				
				getTargetGroupData = ''
				
				myURL = (f"{url}/JSSResource/computergroups/id/{targetIDList}")
				
				try:
					
					response = http.get(myURL, headers=btHeaders)
					
					response.raise_for_status()
					
					getTargetGroupData = response.json()
					
				except HTTPError as http_err:
					
					# Process HTTP Error
					check_http_err = str(http_err)
					split_My_http_err = check_http_err.split()
					
					myHttpError = split_My_http_err[0]
					myMissingRecordID = targetIDList
					myMissingRecordURL = split_My_http_err[5]
					
					if myHttpError == '404':
						print(f".......We found that Record: {myMissingRecordID}, does not exist in your JAMF Instance at URL: {myMissingRecordURL}")
						
					else:
						print(f'HTTP error occurred: {http_err}')
						
				except Exception as err:
					print(f'Other error occurred: {err}')
					
					
				return getTargetGroupData
			
			
			# Clean List
			with ThreadPoolExecutor(max_workers=100) as pool:
				get_data = partial(get_clean_List, JAMF_url)
				list(pool.map(get_data,list_of_Targets))
				
				
			#print(list_of_policies)	
				
				
			#Renew token because the report is a long process
			#renew token
			url = JAMF_url+"/api/v1/auth/keep-alive"
			
			token = http.post(url, headers=btHeaders)
			
			bearer = token.json()['token']
			
			btHeaders = {
				'Accept': 'application/json',
				'Authorization': 'Bearer '+bearer
			}
			
			
			# Process List	
			with ThreadPoolExecutor(max_workers=100) as pool:
				get_data = partial(get_url, JAMF_url)
				response_list = list(pool.map(get_data,list_of_Targets))
				
				
			#print(response_list)
				
				
			for response in response_list:
			##	# Make sure to refresh variables for each loop
				myTargetsComputerGroupInfo = response['computer_group']
				
				
				#Set Variables if Data Available
				if len(str(myTargetsComputerGroupInfo['id'])) == 0:
					myTargetsComputerGroupInfoID = ''
				else:
					myTargetsComputerGroupInfoID = int(myTargetsComputerGroupInfo['id'])
					
				# Get info for Policies
				print(f"Working on Target Group ID: {myTargetsComputerGroupInfoID}")
				
				
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
			#Renew token because the report is a long process
			#renew token
			url = JAMF_url+"/api/v1/auth/keep-alive"
			
			token = http.post(url, headers=btHeaders)
			
			bearer = token.json()['token']
			
			btHeaders = {
				'Accept': 'application/json',
				'Authorization': 'Bearer '+bearer
			}
			
			
			for exclusion in myConfigurationProfileScopeExclusionsComputers:
				
				#Set Variables if Data Available
				if len(str(exclusion['id'])) == 0:
					exclusionID = ''
				else:
					exclusionID = int(exclusion['id'])
					
				# Get info for Policies
				print(f"Working on Target Group ID: {exclusionID}")
				
				
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
			# Get Info for Computer Exclusions groups
			##########################################################################################
			# Start New MultiProcess Code here
				
			list_of_Exclusions = []
			
			for exclusion in myConfigurationProfileScopeExclusionsComputerGroups:
				exclusionID = str(exclusion['id']) 
				list_of_Exclusions.append(f'{exclusionID}')
				
				
			#Renew token because the report is a long process
			#renew token
			url = JAMF_url+"/api/v1/auth/keep-alive"
			
			token = http.post(url, headers=btHeaders)
			
			bearer = token.json()['token']
			
			btHeaders = {
				'Accept': 'application/json',
				'Authorization': 'Bearer '+bearer
			}
			
			
			def get_clean_List(url, exclusionIDList):
				
				myURL = (f"{url}/JSSResource/computergroups/id/{exclusionIDList}")
				
				test = http.get(myURL, headers=btHeaders)
				
				if test.status_code != 200:
					list_of_Exclusions.remove(exclusionIDList)
					
					
					
			def get_url(url, exclusionIDList):
				
				getExclusionGroupData = ''
				
				myURL = (f"{url}/JSSResource/computergroups/id/{exclusionIDList}")
				
				try:
					
					response = http.get(myURL, headers=btHeaders)
					
					response.raise_for_status()
					
					getExclusionGroupData = response.json()
					
				except HTTPError as http_err:
					
					# Process HTTP Error
					check_http_err = str(http_err)
					split_My_http_err = check_http_err.split()
					
					myHttpError = split_My_http_err[0]
					myMissingRecordID = exclusionIDList
					myMissingRecordURL = split_My_http_err[5]
					
					if myHttpError == '404':
						print(f".......We found that Record: {myMissingRecordID}, does not exist in your JAMF Instance at URL: {myMissingRecordURL}")
						
					else:
						print(f'HTTP error occurred: {http_err}')
						
				except Exception as err:
					print(f'Other error occurred: {err}')
					
					
				return getExclusionGroupData
			
			
			# Clean List
			with ThreadPoolExecutor(max_workers=100) as pool:
				get_data = partial(get_clean_List, JAMF_url)
				list(pool.map(get_data,list_of_Exclusions))
				
				
			#print(list_of_policies)	
				
				
			#Renew token because the report is a long process
			#renew token
			url = JAMF_url+"/api/v1/auth/keep-alive"
			
			token = http.post(url, headers=btHeaders)
			
			bearer = token.json()['token']
			
			btHeaders = {
				'Accept': 'application/json',
				'Authorization': 'Bearer '+bearer
			}
			
			
			# Process List	
			with ThreadPoolExecutor(max_workers=100) as pool:
				get_data = partial(get_url, JAMF_url)
				response_list = list(pool.map(get_data,list_of_Exclusions))
				
				
			#print(response_list)
				
				
			for response in response_list:
			##	# Make sure to refresh variables for each loop
				myExclusionsComputerGroupInfo = response['computer_group']
				
				#Set Variables if Data Available
				if len(str(myExclusionsComputerGroupInfo['id'])) == 0:
					myExclusionsComputerGroupInfoID = ''
				else:
					myExclusionsComputerGroupInfoID = int(myExclusionsComputerGroupInfo['id'])
					
				# Get info for Policies
				print(f"Working on Exclusion Group ID: {myExclusionsComputerGroupInfoID}")
				
				
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
				
				
	#Renew token because the report is a long process
	#renew token
	url = JAMF_url+"/api/v1/auth/keep-alive"
	
	token = http.post(url, headers=btHeaders)
	
	bearer = token.json()['token']
	
	btHeaders = {
		'Accept': 'application/json',
		'Authorization': 'Bearer '+bearer
	}
	
	
	# Process List
	with ThreadPoolExecutor(max_workers=100) as pool:
		list(pool.map(processData,response_list))

	
##########################################################################################
# Package to Policies Section
##########################################################################################			
if get_JAMF_Package_To_Policy_Info == ("yes"):
	
	##########################################################################################
	# Process Package to Policies information for csv / Excel
	##########################################################################################
	# Set up url for getting a list of all Package to Regular Policies from JAMF API
	url = JAMF_url + "/JSSResource/policies"
	
	# Set up list
	policyPackagesList = []
	preStagePolicyPackagesList = []
	patchManagementPolicyPackagesList = []
	
	
	try:
		policyResponse = http.get(url, headers=btHeaders)
		
		policyResponse.raise_for_status()
		
		resp = policyResponse.json()
		
	except HTTPError as http_err:
		print(f'HTTP error occurred: {http_err}')
	except Exception as err:
		print(f'Other error occurred: {err}')	
		
	#For Testing
	#print(resp)
		
	policyRecords = resp['policies']
	policyRecords.sort(key=lambda item: item.get('id'), reverse=False)


	for policy in policyRecords:
		
		#Renew token because the report is a long process
		#renew token
		url = JAMF_url+"/api/v1/auth/keep-alive"
		
		token = http.post(url, headers=btHeaders)
		
		bearer = token.json()['token']
		
		btHeaders = {
			'Accept': 'application/json',
			'Authorization': 'Bearer '+bearer
		}
		
		# Get Policy ID to do JAMF API lookup 
		policyRecordsID = str(policy['id']) 
		
		#	For Testing
		#print(policyRecordsID)
		
		# Set up url for getting information from each policy ID from JAMF API
		url = JAMF_url + "/JSSResource/policies/id/" + policyRecordsID
		
		try:
			PolicyRecordsResponse = http.get(url, headers=btHeaders)
			
			PolicyRecordsResponse.raise_for_status()
			
			getPolicyRecords = PolicyRecordsResponse.json()
			
		except HTTPError as http_err:
			# Process HTTP Error
			check_http_err = str(http_err)
			split_My_http_err = check_http_err.split()
			
			myHttpError = split_My_http_err[0]
			myMissingRecordID = policyRecordsID
			myMissingRecordURL = split_My_http_err[5]
			
			if myHttpError == '404':
				print(f".......We found that Record: {myMissingRecordID}, does not exist in your JAMF Instance at URL: {myMissingRecordURL}")
				
			else:
				print(f'HTTP error occurred: {http_err}')
				
			continue
		except Exception as err:
			print(f'Other error occurred: {err}')
			continue
			
		# For Testing
		#print(getPolicyRecords)
			
		#Get policy ID and Name for report
		policyInfoID = getPolicyRecords['policy']['general']['id']
		policyInfoName = getPolicyRecords['policy']['general']['name']
		
		# Find the package data in each policy
		policyPackageInfo = getPolicyRecords['policy']['package_configuration']['packages']
		
		
		# Individual Policy Info for each record
		getMyPolicyIDList = (str(policyInfoID) + " - " + policyInfoName)
		
		# Get info for Policies
		print("Gathering List for Package Info from Policy ID: " + getMyPolicyIDList)
		
		
		#Get Package ID from Policy to compare and find unused packages.
		for policyPackage in policyPackageInfo:
			
			#get package info for dict
			policyPackagesDict = {'Policy ID': policyInfoID, 'Policy Name': policyInfoName, 'Package ID': str(policyPackage['id'])}
			
			policyPackagesList.append(policyPackagesDict)
	
	
	#For testing
	#print(policyPackagesList)	
	
	


	if includePreStagePackageToPolicyInfo == ("yes"):
		##########################################################################################
		# Process Package to PreStage Policies information for csv / Excel
		##########################################################################################
		# Set up url for getting a list of all Package to PreStage Policies from JAMF API
		PSURL = JAMF_url + "/api/v2/computer-prestages"
		
		
		try:
			preStagePolicyPackagesResponse = http.get(PSURL, headers=btHeaders)
			
			preStagePolicyPackagesResponse.raise_for_status()
			
			resp = preStagePolicyPackagesResponse.json()
			
		except HTTPError as http_err:
			print(f'HTTP error occurred: {http_err}')
		except Exception as err:
			print(f'Other error occurred: {err}')	
			
		#For Testing
		#print(resp)
		
		preStagePolicies = resp['results']
		
		for results in preStagePolicies:
			
			#Renew token because the report is a long process
			#renew token
			url = JAMF_url+"/api/v1/auth/keep-alive"
			
			token = http.post(url, headers=btHeaders)
			
			bearer = token.json()['token']
			
			btHeaders = {
				'Accept': 'application/json',
				'Authorization': 'Bearer '+bearer
			}
			
			preStagePoliciesID = results['id']
			packages = results['customPackageIds']
			preStagePoliciesDisplayName = results['displayName']
			
			
			# Individual Policy Info for each record
			getMyPreStagePolicyIDList = (str(preStagePoliciesID) + " - " + preStagePoliciesDisplayName)
			
			# Get info for Policies
			print("Gathering List for Package Info from PreStage Policy ID: " + getMyPreStagePolicyIDList)
			
			
			for package in packages:
				
				#print(package)
				
				preStagePolicyPackagesDict = {'PreStage Policy ID': preStagePoliciesID, 'PreStage Policy Display Name': preStagePoliciesDisplayName, 'Package ID': package}
				
				preStagePolicyPackagesList.append(preStagePolicyPackagesDict)
				
				
		#print(preStagePolicyPackagesList)
	
	if includePatchManagementPackageToPolicyInfo == ("yes"):
		##########################################################################################
		# Process Package to PreStage Policies information for csv / Excel
		##########################################################################################
		# Set up url for getting a list of all Package to PreStage Policies from JAMF API
		allPatchPolicies = JAMF_url + "/JSSResource/patchpolicies"
		patchPoliciesByID = JAMF_url + "/JSSResource/patchpolicies/id/"
		patchSoftwareTitlesByID = JAMF_url + "/JSSResource/patchsoftwaretitles/id/"
		
		
		# Find all patch Policy ID
		try:
			patchManagementPolicyPackagesResponse = http.get(allPatchPolicies, headers=headers, auth = HTTPBasicAuth(username, password))
			
			patchManagementPolicyPackagesResponse.raise_for_status()
			
			resp = patchManagementPolicyPackagesResponse.json()
			
		except HTTPError as http_err:
			print(f'HTTP error occurred: {http_err}')
		except Exception as err:
			print(f'Other error occurred: {err}')	
			
		#For Testing
		#print(resp)
			
		# Get ID from patch policy
		patchPolicy = resp['patch_policies']
		
		
		# Find Patch Policiy ID
		for policy in patchPolicy :
			
			#Renew token because the report is a long process
			#renew token
			url = JAMF_url+"/api/v1/auth/keep-alive"
			
			token = http.post(url, headers=btHeaders)
			
			bearer = token.json()['token']
			
			btHeaders = {
				'Accept': 'application/json',
				'Authorization': 'Bearer '+bearer
			}
			
			btBrokenXMLHeaders = {
				"Accept": "application/xml, application/json",
				"Content-Type": "application/xml",
				'Authorization': 'Bearer '+bearer
			}
			
			
			patchManagementID = str(policy['id'])
			
			# Get info for Policies
			print("Gathering List for Package Info from Patch Management Policy ID: " + patchManagementID)
			
			try:
				patchManagementPolicyPackagesResponseID = http.get(patchPoliciesByID+patchManagementID, headers=btHeaders)
				
				patchManagementPolicyPackagesResponseID.raise_for_status()
				
				resp = patchManagementPolicyPackagesResponseID.json()
				
			except HTTPError as http_err:
				print(f'HTTP error occurred: {http_err}')
			except Exception as err:
				print(f'Other error occurred: {err}')	
				
			#For Testing
			#print(resp['patch_policy']['software_title_configuration_id'])
				
			pmSoftwareTitleConfigurationID = str(resp['patch_policy']['software_title_configuration_id'])
			
			#print(pmSoftwareTitleConfigurationID)
			
			try:
				patchManagementSoftwareTitleConfigurationInfo = http.get(patchSoftwareTitlesByID+pmSoftwareTitleConfigurationID, headers=btBrokenXMLHeaders)
				
				patchManagementSoftwareTitleConfigurationInfo.raise_for_status()
				
				resp = xmltodict.parse(patchManagementSoftwareTitleConfigurationInfo.content)
				
			except HTTPError as http_err:
				print(f'HTTP error occurred: {http_err}')
			except Exception as err:
				print(f'Other error occurred: {err}')	
				
			#For Testing
			#print(resp['patch_software_title'])
				
			patchManagementPolicyDisplayName = resp['patch_software_title']['name']
			pmSoftwareTitleVersionInfo = resp['patch_software_title']['versions']['version']
			
			for version in pmSoftwareTitleVersionInfo :
				packageInfo = version['package']
				pmSoftwareVersionName = version['software_version']
				
				if packageInfo != None :
					#print(packageInfo['id'])
					#print(packageInfo['name'])
					
					patchManagementPackageID = str(packageInfo['id'])
					patchManagementSoftwareVersionName = pmSoftwareVersionName
					
					patchManagementPolicyPackagesDict = {'Patch Management ID': patchManagementID, 'Patch Management Display Name': patchManagementPolicyDisplayName, 'Patch Management Software Version Name': patchManagementSoftwareVersionName, 'Package ID': patchManagementPackageID}
					
					patchManagementPolicyPackagesList.append(patchManagementPolicyPackagesDict)
					
					
		#print(patchManagementPolicyPackagesList)
	
	
	##########################################################################################
	# lookup package information and compair to dict and list to find what is in use.
	##########################################################################################
	url = JAMF_url + "/JSSResource/packages"
	
	try:
		packageResponse = http.get(url, headers=btHeaders)
		
		packageResponse.raise_for_status()
		
		resp = packageResponse.json()
		
	except HTTPError as http_err:
		print(f'HTTP error occurred: {http_err}')
	except Exception as err:
		print(f'Other error occurred: {err}')	
		
	#For Testing
	#print(resp)
		
	packageRecords = resp['packages']
	packageRecords.sort(key=lambda item: item.get('id'), reverse=False)
	
	
	#print(packageRecords)
	
	
	#process package records and set dict and list
	for package in packageRecords:
		
		#Renew token because the report is a long process
		#renew token
		url = JAMF_url+"/api/v1/auth/keep-alive"
		
		token = http.post(url, headers=btHeaders)
		
		bearer = token.json()['token']
		
		btHeaders = {
			'Accept': 'application/json',
			'Authorization': 'Bearer '+bearer
		}
		
		packageRecordsID = package['id']
		packageRecordsName = package['name']
		
		key = 'Package ID' 
		value = str(packageRecordsID)
		
		# Individual Policy Info for each record
		getMyPackageList = (str(packageRecordsID) + " - " + packageRecordsName)
		
		# Get info for Policies
		print("Checking Policies that use Package: " + getMyPackageList) 
		
		#for testing
		#print(packageRecordsID)
		#print(policyPackagesList)
		#print(type(value))
		
		
		#Process Info for packages to policies
		if checkIfPackageIsUsedInPolicy(policyPackagesList, key, value) and checkIfPackageIsUsedInPolicy(preStagePolicyPackagesList, key, value) and checkIfPackageIsUsedInPolicy(patchManagementPolicyPackagesList, key, value):
			
			for policy in policyPackagesList:
				
				policyPackageID = policy['Package ID']
				
				checkPolicyListID = str(policyPackageID)
				checkPackageRecordsID = str(packageRecordsID)
				
				
				if checkPolicyListID == checkPackageRecordsID:
					
					# Set up url for getting information from each policy ID from JAMF API
					url = JAMF_url + "/JSSResource/packages/id/" + str(packageRecordsID)
					
					try:
						myPackageRecordsResponse = http.get(url, headers=btHeaders)
						
						myPackageRecordsResponse.raise_for_status()
						
						getMyPackageRecords = myPackageRecordsResponse.json()
						
					except HTTPError as http_err:
						# Process HTTP Error
						check_http_err = str(http_err)
						split_My_http_err = check_http_err.split()
						
						myHttpError = split_My_http_err[0]
						myMissingRecordID = str(packageRecordsID)
						myMissingRecordURL = split_My_http_err[5]
						
						if myHttpError == '404':
							print(f".......We found that Record: {myMissingRecordID}, does not exist in your JAMF Instance at URL: {myMissingRecordURL}")
							
						else:
							print(f'HTTP error occurred: {http_err}')
							
						continue
					except Exception as err:
						print(f'Other error occurred: {err}')
						continue
						
					# for testing
					#print(getMyPackageRecords['package']['id'])
						
						
					#Set Variables if Data Available
					if len(str(getMyPackageRecords['package']['id'])) == 0:
						myCurrentPackageID = ''
					else:
						myCurrentPackageID = int(getMyPackageRecords['package']['id'])
						
					myCurrentPackageName =  getMyPackageRecords['package']['name']
					myPackageRecordsFileName = getMyPackageRecords['package']['filename']
					
					if len(str(policy['Policy ID'])) == 0:
						myCurrentPolicyID = ''
					else:
						myCurrentPolicyID = int(policy['Policy ID'])
						
					myCurrentPolicyName = policy['Policy Name']
					
					
					appendDataToCVS_JAMF_Package_To_Regular_Policy_Info = "{'Type':'Package Used',\
					\
					'Package List':'Regular Policy',\
					\
					'Package ID':myCurrentPackageID,\
					\
					'Package Name':myCurrentPackageName,\
					\
					'Package File Name':myPackageRecordsFileName,\
					\
					'Policy ID':myCurrentPolicyID,\
					\
					'Policy Name':myCurrentPolicyName}"
					
					appendJAMF_Package_To_Regular_Policy_Info = eval(appendDataToCVS_JAMF_Package_To_Regular_Policy_Info)
					appendPackageToRegularPolicyColumns = appendJAMF_Package_To_Regular_Policy_Info
					
					#Set Columns	
					Combined = appendPackageToRegularPolicyColumns
					
					#Set CSV File
					dataToCsvPackageToPolicy.append(Combined)
					
					# For Testing
					#print(f"Yes, Package ID: " + myCurrentPackageID + " with Package Name: " + myCurrentPackageName + " and Package File Name: " + myPackageRecordsFileName + ", is being used by Policy ID: " + str(myCurrentPolicyID) + " with Policy Name: " + myCurrentPolicyName)
			
			
			for preStagePolicy in preStagePolicyPackagesList:
				
				preStagePolicyPackageID = preStagePolicy['Package ID']
				
				checkPreStagePolicyListID = str(preStagePolicyPackageID)
				checkPackageRecordsID = str(packageRecordsID)
				
				if checkPreStagePolicyListID == checkPackageRecordsID:
					
					# Set up url for getting information from each policy ID from JAMF API
					url = JAMF_url + "/JSSResource/packages/id/" + str(packageRecordsID)
					
					try:
						myPackageRecordsResponse = http.get(url, headers=headers, auth = HTTPBasicAuth('jamf-api', 'J@MF@P!acc3s$'))
						
						myPackageRecordsResponse.raise_for_status()
						
						getMyPackageRecords = myPackageRecordsResponse.json()
						
					except HTTPError as http_err:
						# Process HTTP Error
						check_http_err = str(http_err)
						split_My_http_err = check_http_err.split()
						
						myHttpError = split_My_http_err[0]
						myMissingRecordID = str(packageRecordsID)
						myMissingRecordURL = split_My_http_err[5]
						
						if myHttpError == '404':
							print(f".......We found that Record: {myMissingRecordID}, does not exist in your JAMF Instance at URL: {myMissingRecordURL}")
							
						else:
							print(f'HTTP error occurred: {http_err}')
							
						continue
					except Exception as err:
						print(f'Other error occurred: {err}')
						continue
					
						
						
					#print(getMyPackageRecords['package']['id'])
						
						
					#Set Variables if Data Available
					if len(str(getMyPackageRecords['package']['id'])) == 0:
						myCurrentPackageID = ''
					else:
						myCurrentPackageID = int(getMyPackageRecords['package']['id'])
						
					myCurrentPackageName =  getMyPackageRecords['package']['name']
					myPackageRecordsFileName = getMyPackageRecords['package']['filename']
					
					if len(str(preStagePolicy['PreStage Policy ID'])) == 0:
						myCurrentPreStagePolicyID = ''
					else:
						myCurrentPreStagePolicyID = int(preStagePolicy['PreStage Policy ID'])
						
					myCurrentPreStagePolicyName = preStagePolicy['PreStage Policy Display Name']
					
					
					appendDataToCVS_JAMF_Package_To_PreStage_Policy_Info = "{'Type':'Package Used',\
					\
					'Package List':'PreStage Policy',\
					\
					'Package ID':myCurrentPackageID,\
					\
					'Package Name':myCurrentPackageName,\
					\
					'Package File Name':myPackageRecordsFileName,\
					\
					'PreStage Policy ID':myCurrentPreStagePolicyID,\
					\
					'PreStage Policy Name':myCurrentPreStagePolicyName}"
					
					
					appendJAMF_Package_To_PreStage_Policy_Info = eval(appendDataToCVS_JAMF_Package_To_PreStage_Policy_Info)
					appendPackageToPreStagePolicyColumns = appendJAMF_Package_To_PreStage_Policy_Info
					
					#Set Columns	
					Combined = appendPackageToPreStagePolicyColumns
					
					#Set CSV File
					dataToCsvPackageToPolicy.append(Combined)
					
					# For Testing
					#print(f"Yes, Package ID: " + myCurrentPackageID + " with Package Name: " + myCurrentPackageName + " and Package FileName: "+ myPackageRecordsFileName + " is being used in PreStage Policies ID: " + myCurrentPreStagePolicyID + " with PreStage Display Name: " + myCurrentPreStagePolicyName)
			
			
			for patchManagementPolicy in patchManagementPolicyPackagesList:
				
				patchManagementPolicyPackageID = patchManagementPolicy['Package ID']
				
				checkPatchManagementPolicyListID = str(patchManagementPolicyPackageID)
				checkPackageRecordsID = str(packageRecordsID)
				
				if checkPatchManagementPolicyListID == checkPackageRecordsID:
					
					# Set up url for getting information from each policy ID from JAMF API
					url = JAMF_url + "/JSSResource/packages/id/" + str(packageRecordsID)
					
					try:
						myPackageRecordsResponse = http.get(url, headers=headers, auth = HTTPBasicAuth('jamf-api', 'J@MF@P!acc3s$'))
						
						myPackageRecordsResponse.raise_for_status()
						
						getMyPackageRecords = myPackageRecordsResponse.json()
						
					except HTTPError as http_err:
						# Process HTTP Error
						check_http_err = str(http_err)
						split_My_http_err = check_http_err.split()
						
						myHttpError = split_My_http_err[0]
						myMissingRecordID = str(packageRecordsID)
						myMissingRecordURL = split_My_http_err[5]
						
						if myHttpError == '404':
							print(f".......We found that Record: {myMissingRecordID}, does not exist in your JAMF Instance at URL: {myMissingRecordURL}")
							
						else:
							print(f'HTTP error occurred: {http_err}')
							
						continue
					except Exception as err:
						print(f'Other error occurred: {err}')
						continue
					
					
					
					#print(getMyPackageRecords['package']['id'])
					
					
					#Set Variables if Data Available
					if len(str(getMyPackageRecords['package']['id'])) == 0:
						myCurrentPackageID = ''
					else:
						myCurrentPackageID = int(getMyPackageRecords['package']['id'])
						
					myCurrentPackageName =  getMyPackageRecords['package']['name']
					myPackageRecordsFileName = getMyPackageRecords['package']['filename']
					
					if len(str(patchManagementPolicy['Patch Management ID'])) == 0:
						myCurrentPatchManagementPolicyID = ''
					else:
						myCurrentPatchManagementPolicyID = int(patchManagementPolicy['Patch Management ID'])
						
					myCurrentPatchManagementPolicyName = patchManagementPolicy['Patch Management Display Name']
					
					myCurrentPatchManagementPolicySoftwareVersionName = patchManagementPolicy['Patch Management Software Version Name']
					
					
					appendDataToCVS_JAMF_Package_To_Patch_Management_Policy_Info = "{'Type':'Package Used',\
					\
					'Package List':'Patch Management Policy',\
					\
					'Package ID':myCurrentPackageID,\
					\
					'Package Name':myCurrentPackageName,\
					\
					'Package File Name':myPackageRecordsFileName,\
					\
					'Patch Management Policy ID':myCurrentPatchManagementPolicyID,\
					\
					'Patch Management Policy Name':myCurrentPatchManagementPolicyName,	\
					\
					'Patch Management Policy Software Version Name':myCurrentPatchManagementPolicySoftwareVersionName}"
					
					
					appendJAMF_Package_To_Patch_Management_Policy_Info = eval(appendDataToCVS_JAMF_Package_To_Patch_Management_Policy_Info)
					appendPackageToPatchManagementPolicyColumns = appendJAMF_Package_To_Patch_Management_Policy_Info
					
					#Set Columns	
					Combined = appendPackageToPatchManagementPolicyColumns
					
					#Set CSV File
					dataToCsvPackageToPolicy.append(Combined)
					
					# For Testing
					#print(f"Yes, Package ID: " + myCurrentPackageID + " with Package Name: " + myCurrentPackageName + " and Package FileName: "+ myPackageRecordsFileName + " is being used in Patch Management Policies ID: " + myCurrentPatchManagementPolicyID + " with Patch Management Display Name: " + myCurrentPatchManagementPolicyID + " with Patch Management Display Software Version Name: " + myCurrentPatchManagementPolicySoftwareVersionName)
					
					
		elif checkIfPackageIsUsedInPolicy(policyPackagesList, key, value):
			
			for policy in policyPackagesList:
				
				policyPackageID = policy['Package ID']
				
				checkPolicyListID = str(policyPackageID)
				checkPackageRecordsID = str(packageRecordsID)
				
				
				if checkPolicyListID == checkPackageRecordsID:
					
					# Set up url for getting information from each policy ID from JAMF API
					url = JAMF_url + "/JSSResource/packages/id/" + str(packageRecordsID)
					
					try:
						myPackageRecordsResponse = http.get(url, headers=btHeaders)
						
						myPackageRecordsResponse.raise_for_status()
						
						getMyPackageRecords = myPackageRecordsResponse.json()
						
					except HTTPError as http_err:
						# Process HTTP Error
						check_http_err = str(http_err)
						split_My_http_err = check_http_err.split()
						
						myHttpError = split_My_http_err[0]
						myMissingRecordID = str(packageRecordsID)
						myMissingRecordURL = split_My_http_err[5]
						
						if myHttpError == '404':
							print(f".......We found that Record: {myMissingRecordID}, does not exist in your JAMF Instance at URL: {myMissingRecordURL}")
							
						else:
							print(f'HTTP error occurred: {http_err}')
							
						continue
					except Exception as err:
						print(f'Other error occurred: {err}')
						continue
					
						
					# for testing
					#print(getMyPackageRecords['package']['id'])
						
						
					#Set Variables if Data Available
					if len(str(getMyPackageRecords['package']['id'])) == 0:
						myCurrentPackageID = ''
					else:
						myCurrentPackageID = int(getMyPackageRecords['package']['id'])
					
					myCurrentPackageName =  getMyPackageRecords['package']['name']
					myPackageRecordsFileName = getMyPackageRecords['package']['filename']
					
					if len(str(policy['Policy ID'])) == 0:
						myCurrentPolicyID = ''
					else:
						myCurrentPolicyID = int(policy['Policy ID'])
					
					myCurrentPolicyName = policy['Policy Name']
					
					
					appendDataToCVS_JAMF_Package_To_Regular_Policy_Info = "{'Type':'Package Used',\
					\
					'Package List':'Regular Policy',\
					\
					'Package ID':myCurrentPackageID,\
					\
					'Package Name':myCurrentPackageName,\
					\
					'Package File Name':myPackageRecordsFileName,\
					\
					'Policy ID':myCurrentPolicyID,\
					\
					'Policy Name':myCurrentPolicyName}"
					
					appendJAMF_Package_To_Regular_Policy_Info = eval(appendDataToCVS_JAMF_Package_To_Regular_Policy_Info)
					appendPackageToRegularPolicyColumns = appendJAMF_Package_To_Regular_Policy_Info
					
					#Set Columns	
					Combined = appendPackageToRegularPolicyColumns
					
					#Set CSV File
					dataToCsvPackageToPolicy.append(Combined)
					
					# For Testing
					#print(f"Yes, Package ID: " + myCurrentPackageID + " with Package Name: " + myCurrentPackageName + " and Package File Name: " + myPackageRecordsFileName + ", is being used by Policy ID: " + str(myCurrentPolicyID) + " with Policy Name: " + myCurrentPolicyName)
					
					
		elif checkIfPackageIsUsedInPolicy(preStagePolicyPackagesList, key, value):
			
			for preStagePolicy in preStagePolicyPackagesList:
				
				preStagePolicyPackageID = preStagePolicy['Package ID']
				
				checkPreStagePolicyListID = str(preStagePolicyPackageID)
				checkPackageRecordsID = str(packageRecordsID)
				
				if checkPreStagePolicyListID == checkPackageRecordsID:
					
					# Set up url for getting information from each policy ID from JAMF API
					url = JAMF_url + "/JSSResource/packages/id/" + str(packageRecordsID)
					
					try:
						myPackageRecordsResponse = http.get(url, headers=btHeaders)
						
						myPackageRecordsResponse.raise_for_status()
						
						getMyPackageRecords = myPackageRecordsResponse.json()
						
					except HTTPError as http_err:
						# Process HTTP Error
						check_http_err = str(http_err)
						split_My_http_err = check_http_err.split()
						
						myHttpError = split_My_http_err[0]
						myMissingRecordID = str(packageRecordsID)
						myMissingRecordURL = split_My_http_err[5]
						
						if myHttpError == '404':
							print(f".......We found that Record: {myMissingRecordID}, does not exist in your JAMF Instance at URL: {myMissingRecordURL}")
							
						else:
							print(f'HTTP error occurred: {http_err}')
							
						continue
					except Exception as err:
						print(f'Other error occurred: {err}')
						continue
					
						
						
					#print(getMyPackageRecords['package']['id'])
					#print(getMyPackageRecords) 
						
						
					#Set Variables if Data Available
					if len(str(getMyPackageRecords['package']['id'])) == 0:
						myCurrentPackageID = ''
					else:
						myCurrentPackageID = int(getMyPackageRecords['package']['id'])
						
					myCurrentPackageName =  getMyPackageRecords['package']['name']
					myPackageRecordsFileName = getMyPackageRecords['package']['filename']
					
					if len(str(preStagePolicy['PreStage Policy ID'])) == 0:
						myCurrentPreStagePolicyID = ''
					else:
						myCurrentPreStagePolicyID = int(preStagePolicy['PreStage Policy ID'])
						
					myCurrentPreStagePolicyName = preStagePolicy['PreStage Policy Display Name']
					
					
					appendDataToCVS_JAMF_Package_To_PreStage_Policy_Info = "{'Type':'Package Used',\
					\
					'Package List':'PreStage Policy',\
					\
					'Package ID':myCurrentPackageID,\
					\
					'Package Name':myCurrentPackageName,\
					\
					'Package File Name':myPackageRecordsFileName,\
					\
					'PreStage Policy ID':myCurrentPreStagePolicyID,\
					\
					'PreStage Policy Name':myCurrentPreStagePolicyName}"
					
					
					appendJAMF_Package_To_PreStage_Policy_Info = eval(appendDataToCVS_JAMF_Package_To_PreStage_Policy_Info)
					appendPackageToPreStagePolicyColumns = appendJAMF_Package_To_PreStage_Policy_Info
					
					#Set Columns	
					Combined = appendPackageToPreStagePolicyColumns
					
					#Set CSV File
					dataToCsvPackageToPolicy.append(Combined)
					
					# For Testing
					#print(f"Yes, Package ID: " + myCurrentPackageID + " with Package Name: " + myCurrentPackageName + " and Package FileName: "+ myPackageRecordsFileName + " is being used in PreStage Policies ID: " + myCurrentPreStagePolicyID + " with PreStage Display Name: " + myCurrentPreStagePolicyName)
		
		
		elif checkIfPackageIsUsedInPolicy(patchManagementPolicyPackagesList, key, value):
			
			for patchManagementPolicy in patchManagementPolicyPackagesList:
				
				patchManagementPolicyPackageID = patchManagementPolicy['Package ID']
				
				checkPatchManagementPolicyListID = str(patchManagementPolicyPackageID)
				checkPackageRecordsID = str(packageRecordsID)
				
				if checkPatchManagementPolicyListID == checkPackageRecordsID:
					
					# Set up url for getting information from each policy ID from JAMF API
					url = JAMF_url + "/JSSResource/packages/id/" + str(packageRecordsID)
					
					try:
						myPackageRecordsResponse = http.get(url, headers=headers, auth = HTTPBasicAuth('jamf-api', 'J@MF@P!acc3s$'))
						
						myPackageRecordsResponse.raise_for_status()
						
						getMyPackageRecords = myPackageRecordsResponse.json()
						
					except HTTPError as http_err:
						# Process HTTP Error
						check_http_err = str(http_err)
						split_My_http_err = check_http_err.split()
						
						myHttpError = split_My_http_err[0]
						myMissingRecordID = str(packageRecordsID)
						myMissingRecordURL = split_My_http_err[5]
						
						if myHttpError == '404':
							print(f".......We found that Record: {myMissingRecordID}, does not exist in your JAMF Instance at URL: {myMissingRecordURL}")
							
						else:
							print(f'HTTP error occurred: {http_err}')
							
						continue
					except Exception as err:
						print(f'Other error occurred: {err}')
						continue
					
					
					
					#print(getMyPackageRecords['package']['id'])
					
					
					#Set Variables if Data Available
					if len(str(getMyPackageRecords['package']['id'])) == 0:
						myCurrentPackageID = ''
					else:
						myCurrentPackageID = int(getMyPackageRecords['package']['id'])
						
					myCurrentPackageName =  getMyPackageRecords['package']['name']
					myPackageRecordsFileName = getMyPackageRecords['package']['filename']
					
					if len(str(patchManagementPolicy['Patch Management ID'])) == 0:
						myCurrentPatchManagementPolicyID = ''
					else:
						myCurrentPatchManagementPolicyID = int(patchManagementPolicy['Patch Management ID'])
						
					myCurrentPatchManagementPolicyName = patchManagementPolicy['Patch Management Display Name']
					
					myCurrentPatchManagementPolicySoftwareVersionName = patchManagementPolicy['Patch Management Software Version Name']
					
					
					appendDataToCVS_JAMF_Package_To_Patch_Management_Policy_Info = "{'Type':'Package Used',\
					\
					'Package List':'Patch Management Policy',\
					\
					'Package ID':myCurrentPackageID,\
					\
					'Package Name':myCurrentPackageName,\
					\
					'Package File Name':myPackageRecordsFileName,\
					\
					'Patch Management Policy ID':myCurrentPatchManagementPolicyID,\
					\
					'Patch Management Policy Name':myCurrentPatchManagementPolicyName,	\
					\
					'Patch Management Policy Software Version Name':myCurrentPatchManagementPolicySoftwareVersionName}"
					
					
					appendJAMF_Package_To_Patch_Management_Policy_Info = eval(appendDataToCVS_JAMF_Package_To_Patch_Management_Policy_Info)
					appendPackageToPatchManagementPolicyColumns = appendJAMF_Package_To_Patch_Management_Policy_Info
					
					#Set Columns	
					Combined = appendPackageToPatchManagementPolicyColumns
					
					#Set CSV File
					dataToCsvPackageToPolicy.append(Combined)
					
					# For Testing
					#print(f"Yes, Package ID: " + myCurrentPackageID + " with Package Name: " + myCurrentPackageName + " and Package FileName: "+ myPackageRecordsFileName + " is being used in Patch Management Policies ID: " + myCurrentPatchManagementPolicyID + " with Patch Management Display Name: " + myCurrentPatchManagementPolicyID + " with Patch Management Display Software Version Name: " + myCurrentPatchManagementPolicySoftwareVersionName)
					
					
		else:
			
			# Set up url for getting information from each policy ID from JAMF API
			url = JAMF_url + "/JSSResource/packages/id/" + str(packageRecordsID)
			
			try:
				myPackageRecordsResponse = http.get(url, headers=btHeaders)
				
				myPackageRecordsResponse.raise_for_status()
				
				getMyPackageRecords = myPackageRecordsResponse.json()
				
			except HTTPError as http_err:
				print(f'HTTP error occurred: {http_err}')
			except Exception as err:
				print(f'Other error occurred: {err}')
				
			# for testing
			#print(getMyPackageRecords['package']['id'])
			
			
			#Set Variables if Data Available
			if len(str(getMyPackageRecords['package']['id'])) == 0:
				myUnusedCurrentPackageID = ''
			else:
				myUnusedCurrentPackageID = int(getMyPackageRecords['package']['id'])
				
			myUnusedPackageName =  getMyPackageRecords['package']['name']
			myUnusedPackageRecordsFileName = getMyPackageRecords['package']['filename']
			
			
			appendDataToCVS_JAMF_Package_Unused_Info = "{'Type':'Package Not Used',\
			\
			'Package List':'',\
			\
			'Package ID':myUnusedCurrentPackageID,\
			\
			'Package Name':myUnusedPackageName,\
			\
			'Package File Name':myUnusedPackageRecordsFileName}"
			
			
			appendJAMF_Package_Unused_Info = eval(appendDataToCVS_JAMF_Package_Unused_Info)
			appendPackageUnusedColumns = appendJAMF_Package_Unused_Info
			
			#Set Columns	
			Combined = appendPackageUnusedColumns
			
			#Set CSV File
			dataToCsvPackageToPolicy.append(Combined)
			
			#print(f"No, Package ID: " + str(packageRecordsID) + ", Package Name: " + packageRecordsName + " is not being used in any Policies")
			
			
##########################################################################################
# Script to Policies Section
##########################################################################################			
if get_JAMF_Script_To_Policy_Info == ("yes"):
	
	##########################################################################################
	# Process Script to Policies information for csv / Excel
	##########################################################################################
	# Set up url for getting a list of all Script to Regular Policies from JAMF API
	url = JAMF_url + "/JSSResource/policies"
	
	# Set up list
	policyScriptsList = []
	
	try:
		policyResponse = http.get(url, headers=btHeaders)
		
		policyResponse.raise_for_status()
		
		resp = policyResponse.json()
		
	except HTTPError as http_err:
		print(f'HTTP error occurred: {http_err}')
	except Exception as err:
		print(f'Other error occurred: {err}')	
		
	#For Testing
	#print(resp)
		
	policyRecords = resp['policies']
	policyRecords.sort(key=lambda item: item.get('id'), reverse=False)
	
	
	for policy in policyRecords:
		
		#Renew token because the report is a long process
		#renew token
		url = JAMF_url+"/api/v1/auth/keep-alive"
		
		token = http.post(url, headers=btHeaders)
		
		bearer = token.json()['token']
		
		btHeaders = {
			'Accept': 'application/json',
			'Authorization': 'Bearer '+bearer
		}
		
		# Get Policy ID to do JAMF API lookup 
		policyRecordsID = str(policy['id']) 
		
		#	For Testing
		#print(policyRecordsID)
		
		# Set up url for getting information from each policy ID from JAMF API
		url = JAMF_url + "/JSSResource/policies/id/" + policyRecordsID
		
		try:
			PolicyRecordsResponse = http.get(url, headers=btHeaders)
			
			PolicyRecordsResponse.raise_for_status()
			
			getPolicyRecords = PolicyRecordsResponse.json()
			
		except HTTPError as http_err:
			# Process HTTP Error
			check_http_err = str(http_err)
			split_My_http_err = check_http_err.split()
			
			myHttpError = split_My_http_err[0]
			myMissingRecordID = policyRecordsID
			myMissingRecordURL = split_My_http_err[5]
			
			if myHttpError == '404':
				print(f".......We found that Record: {myMissingRecordID}, does not exist in your JAMF Instance at URL: {myMissingRecordURL}")
				
			else:
				print(f'HTTP error occurred: {http_err}')
				
			continue
		except Exception as err:
			print(f'Other error occurred: {err}')
			continue
			
		# For Testing
		#print(getPolicyRecords)
			
		#Get policy ID and Name for report
		policyInfoID = getPolicyRecords['policy']['general']['id']
		policyInfoName = getPolicyRecords['policy']['general']['name']
		
		# Find the Script data in each policy
		policyScriptInfo = getPolicyRecords['policy']['scripts']
		
		
		# Individual Policy Info for each record
		getMyPolicyIDList = (str(policyInfoID) + " - " + policyInfoName)
		
		# Get info for Policies
		print("Gathering List for Script Info from Policy ID: " + getMyPolicyIDList)
		
		
		#Get Script ID from Policy to compare and find unused Scripts.
		for policyScript in policyScriptInfo:
			
			#get Script info for dict
			policyScriptsDict = {'Policy ID': policyInfoID, 'Policy Name': policyInfoName, 'Script ID': str(policyScript['id'])}
			
			policyScriptsList.append(policyScriptsDict)
			
			
	#For testing
	#print(policyScriptsList)	
			
			
	##########################################################################################
	# lookup Script information and compair to dict and list to find what is in use.
	##########################################################################################
	url = JAMF_url + "/JSSResource/scripts"
	
	try:
		ScriptResponse = http.get(url, headers=btHeaders)
		
		ScriptResponse.raise_for_status()
		
		resp = ScriptResponse.json()
		
	except HTTPError as http_err:
		print(f'HTTP error occurred: {http_err}')
	except Exception as err:
		print(f'Other error occurred: {err}')	
		
	#For Testing
	#print(resp)
		
	ScriptRecords = resp['scripts']
	ScriptRecords.sort(key=lambda item: item.get('id'), reverse=False)
	
	
	#print(ScriptRecords)
	
	
	#process Script records and set dict and list
	for Script in ScriptRecords:
		
		#Renew token because the report is a long process
		#renew token
		url = JAMF_url+"/api/v1/auth/keep-alive"
		
		token = http.post(url, headers=btHeaders)
		
		bearer = token.json()['token']
		
		btHeaders = {
			'Accept': 'application/json',
			'Authorization': 'Bearer '+bearer
		}
		
		ScriptRecordsID = Script['id']
		ScriptRecordsName = Script['name']
		
		key = 'Script ID' 
		value = str(ScriptRecordsID)
		
		# Individual Policy Info for each record
		getMyScriptList = (str(ScriptRecordsID) + " - " + ScriptRecordsName)
		
		# Get info for Policies
		print("Checking Policies that use Script: " + getMyScriptList) 
		
		#for testing
		#print(ScriptRecordsID)
		#print(policyScriptsList)
		#print(type(value))
		
		
		#Process Info for Scripts to policies
		if checkIfScriptIsUsedInPolicy(policyScriptsList, key, value):
			
			for policy in policyScriptsList:
				
				policyScriptID = policy['Script ID']
				
				checkPolicyListID = str(policyScriptID)
				checkScriptRecordsID = str(ScriptRecordsID)
				
				
				if checkPolicyListID == checkScriptRecordsID:
					
					# Set up url for getting information from each policy ID from JAMF API
					url = JAMF_url + "/JSSResource/scripts/id/" + str(ScriptRecordsID)
					
					try:
						myScriptRecordsResponse = http.get(url, headers=btHeaders)
						
						myScriptRecordsResponse.raise_for_status()
						
						getMyScriptRecords = myScriptRecordsResponse.json()
						
					except HTTPError as http_err:
						# Process HTTP Error
						check_http_err = str(http_err)
						split_My_http_err = check_http_err.split()
						
						myHttpError = split_My_http_err[0]
						myMissingRecordID = str(ScriptRecordsID)
						myMissingRecordURL = split_My_http_err[5]
						
						if myHttpError == '404':
							print(f".......We found that Record: {myMissingRecordID}, does not exist in your JAMF Instance at URL: {myMissingRecordURL}")
							
						else:
							print(f'HTTP error occurred: {http_err}')
							
						continue
					except Exception as err:
						print(f'Other error occurred: {err}')
						continue
						
					# for testing
					#print(getMyScriptRecords['script']['id'])
						
						
					#Set Variables if Data Available
					if len(str(getMyScriptRecords['script']['id'])) == 0:
						myCurrentScriptID = ''
					else:
						myCurrentScriptID = int(getMyScriptRecords['script']['id'])
						
					myCurrentScriptName =  getMyScriptRecords['script']['name']
					myScriptRecordsFileName = getMyScriptRecords['script']['filename']
					
					if len(str(policy['Policy ID'])) == 0:
						myCurrentPolicyID = ''
					else:
						myCurrentPolicyID = int(policy['Policy ID'])
						
					myCurrentPolicyName = policy['Policy Name']
					
					
					appendDataToCVS_JAMF_Script_To_Regular_Policy_Info = "{'Type':'Script Used',\
					\
					'Script ID':myCurrentScriptID,\
					\
					'Script Name':myCurrentScriptName,\
					\
					'Script File Name':myScriptRecordsFileName,\
					\
					'Policy ID':myCurrentPolicyID,\
					\
					'Policy Name':myCurrentPolicyName}"
					
					appendJAMF_Script_To_Regular_Policy_Info = eval(appendDataToCVS_JAMF_Script_To_Regular_Policy_Info)
					appendScriptToRegularPolicyColumns = appendJAMF_Script_To_Regular_Policy_Info
					
					#Set Columns	
					Combined = appendScriptToRegularPolicyColumns
					
					#Set CSV File
					dataToCsvScriptToPolicy.append(Combined)
					
					# For Testing
					#print(f"Yes, Script ID: " + myCurrentScriptID + " with Script Name: " + myCurrentScriptName + " and Script File Name: " + myScriptRecordsFileName + ", is being used by Policy ID: " + str(myCurrentPolicyID) + " with Policy Name: " + myCurrentPolicyName)
					
		else:
			
			# Set up url for getting information from each policy ID from JAMF API
			url = JAMF_url + "/JSSResource/scripts/id/" + str(ScriptRecordsID)
			
			try:
				myScriptRecordsResponse = http.get(url, headers=btHeaders)
				
				myScriptRecordsResponse.raise_for_status()
				
				getMyScriptRecords = myScriptRecordsResponse.json()
				
			except HTTPError as http_err:
				# Process HTTP Error
				check_http_err = str(http_err)
				split_My_http_err = check_http_err.split()
				
				myHttpError = split_My_http_err[0]
				myMissingRecordID = str(ScriptRecordsID)
				myMissingRecordURL = split_My_http_err[5]
				
				if myHttpError == '404':
					print(f".......We found that Record: {myMissingRecordID}, does not exist in your JAMF Instance at URL: {myMissingRecordURL}")
					
				else:
					print(f'HTTP error occurred: {http_err}')
					
				continue
			except Exception as err:
				print(f'Other error occurred: {err}')
				continue
				
			# for testing
			#print(getMyScriptRecords['script']['id'])
				
				
			#Set Variables if Data Available
			if len(str(getMyScriptRecords['script']['id'])) == 0:
				myUnusedCurrentScriptID = ''
			else:
				myUnusedCurrentScriptID = int(getMyScriptRecords['script']['id'])
				
			myUnusedScriptName =  getMyScriptRecords['script']['name']
			myUnusedScriptRecordsFileName = getMyScriptRecords['script']['filename']
			
			
			appendDataToCVS_JAMF_Script_Unused_Info = "{'Type':'Script Not Used',\
			\
			'Script ID':myUnusedCurrentScriptID,\
			\
			'Script Name':myUnusedScriptName,\
			\
			'Script File Name':myUnusedScriptRecordsFileName}"
			
			
			appendJAMF_Script_Unused_Info = eval(appendDataToCVS_JAMF_Script_Unused_Info)
			appendScriptUnusedColumns = appendJAMF_Script_Unused_Info
			
			#Set Columns	
			Combined = appendScriptUnusedColumns
			
			#Set CSV File
			dataToCsvScriptToPolicy.append(Combined)
			
			#print(f"No, Script ID: " + str(ScriptRecordsID) + ", Script Name: " + ScriptRecordsName + " is not being used in any Policies")
						

##########################################################################################
# Process data for Export to csv / Excel
##########################################################################################
# Check and make sure that either Policy or Config Profile was selected
if get_JAMF_Computers_Info == 'yes' or get_JAMF_Policy_Info == 'yes' or get_JAMF_Configuration_Profile_Info == 'yes' or get_JAMF_Package_To_Policy_Info == 'yes' or get_JAMF_Script_To_Policy_Info == 'yes':
	
	
	# Get export to csv file
	if get_JAMF_Computers_Info == ("yes"):
		df_computers_raw = pd.DataFrame(dataToCsvComputers)
		df_computers_sort = df_computers_raw.rename_axis('MyIdx').sort_values(by = ['Computer ID', 'MyIdx'])
		df_computers = df_computers_sort.reset_index(drop=True)
		
	if get_JAMF_Policy_Info == ("yes"):
		df_policy_raw = pd.DataFrame(dataToCsvPolicy)
		df_policy_sort = df_policy_raw.rename_axis('MyIdx').sort_values(by = ['Policy ID', 'MyIdx'])
		df_policy = df_policy_sort.reset_index(drop=True)
		
	if get_JAMF_Configuration_Profile_Info == ("yes"):	
		df_configProfile_raw = pd.DataFrame(dataToCsvConfigurationProfile)
		df_configProfile_sort = df_configProfile_raw.rename_axis('MyIdx').sort_values(by = ['Configuration Profile ID', 'MyIdx'])
		df_configProfile = df_configProfile_sort.reset_index(drop=True)
		
	if get_JAMF_Package_To_Policy_Info == ("yes"):	
		df_PackageToPolicy_raw = pd.DataFrame(dataToCsvPackageToPolicy)
		df_PackageToPolicy_sort = df_PackageToPolicy_raw.rename_axis('MyIdx').sort_values(by = ['Package ID', 'MyIdx'])
		df_PackageToPolicy = df_PackageToPolicy_sort.reset_index(drop=True)
		
	if get_JAMF_Script_To_Policy_Info == ("yes"):	
		df_ScriptToPolicy_raw = pd.DataFrame(dataToCsvScriptToPolicy)
		df_ScriptToPolicy_sort = df_ScriptToPolicy_raw.rename_axis('MyIdx').sort_values(by = ['Script ID', 'MyIdx'])
		df_ScriptToPolicy = df_ScriptToPolicy_sort.reset_index(drop=True)

	
	print('\n******************** Creating Jamf Instance Info file. ********************\n')
	
	
	# We'll define an Excel writer object and the target file
	pandas.io.formats.excel.ExcelFormatter.header_style = None
	
	Excelwriter = pd.ExcelWriter(excelReportFile, engine="xlsxwriter")
	
	
	# Function to set Column with similar to AutoFit in Excel
	def get_col_widths(dataframe):
		# First we find the maximum length of the index column   
		idx_max = max([len(str(s)) for s in dataframe.index.values] + [len(str(dataframe.index.name))])
		
		# Then, we concatenate this to the max of the lengths of column name and its values for each column, left to right
		return [idx_max] + [max([len(str(s)) for s in dataframe[col].values] + [len(col)]) + 16 for col in dataframe.columns]
	
	# Create Excel Sheets
	if get_JAMF_Computers_Info == ("yes"):
		df_computers.to_excel(Excelwriter, sheet_name='Jamf Computers Info')
		
		# Get the xlsxwriter workbook and worksheet objects.
		df_computers_workbook  = Excelwriter.book
		
		df_computers_worksheet = Excelwriter.sheets['Jamf Computers Info']
		
		TopRowFormat = df_computers_workbook.add_format()
		TopRowFormat.set_bold()
		TopRowFormat.set_font_size(16)
		TopRowFormat.set_align('center')
		TopRowFormat.set_align('vcenter')
		TopRowFormat.set_bottom(2)
		TopRowFormat.set_bg_color('#D5D8DC')
	
		df_computers_worksheet.set_row(0, 30, TopRowFormat)	
		
		
		if usingFilter == 'computerFilter':
			format1 = df_computers_workbook.add_format({'bg_color': '#D5D8DC'})
			format2 = df_computers_workbook.add_format({'bg_color': '#A3E4D7'})
			format3 = df_computers_workbook.add_format({'bg_color': '#AED6F1'})
			format4 = df_computers_workbook.add_format({'bg_color': '#F5B7B1'})
			format5 = df_computers_workbook.add_format({'bg_color': '#F9E79F'})
			
			df_computers_worksheet.conditional_format('$A2:$V$1048576', 
													{'type':'formula',
														'criteria': '=$B2="Computer Configuration Profile Membership Info"',
														'format': format1
														})
			
			df_computers_worksheet.conditional_format('$A2:$V$1048576', 
													{'type':'formula',
														'criteria': '=$B2="Computer Group Membership Info"',
														'format': format2
														})
			
			df_computers_worksheet.conditional_format('$A2:$V$1048576', 
													{'type':'formula',
														'criteria': '=$B2="Computer Hardware Local Account Info"',
														'format': format3
														})
			
			df_computers_worksheet.conditional_format('$A2:$V$1048576', 
													{'type':'formula',
														'criteria': '=$B2="Computer Hardware FileVault2 Info"',
														'format': format4
														})
			
			df_computers_worksheet.conditional_format('$A2:$V$1048576', 
													{'type':'formula',
														'criteria': '=$B2="Computer Hardware Info"',
														'format': format5
														})
			
		elif usingFilter == 'smartGroupFilter':
			format1 = df_computers_workbook.add_format({'bg_color': '#D5D8DC'})
			format2 = df_computers_workbook.add_format({'bg_color': '#A3E4D7'})
			format3 = df_computers_workbook.add_format({'bg_color': '#AED6F1'})
			format4 = df_computers_workbook.add_format({'bg_color': '#F5B7B1'})
			format5 = df_computers_workbook.add_format({'bg_color': '#F9E79F'})
			
			df_computers_worksheet.conditional_format('$A2:$V$1048576', 
													{'type':'formula',
														'criteria': '=$D2="Computer Configuration Profile Membership Info"',
														'format': format1
														})
				
			df_computers_worksheet.conditional_format('$A2:$V$1048576', 
													{'type':'formula',
														'criteria': '=$D2="Computer Group Membership Info"',
														'format': format2
														})
				
			df_computers_worksheet.conditional_format('$A2:$V$1048576', 
													{'type':'formula',
														'criteria': '=$D2="Computer Hardware Local Account Info"',
														'format': format3
														})
				
			df_computers_worksheet.conditional_format('$A2:$V$1048576', 
													{'type':'formula',
														'criteria': '=$D2="Computer Hardware FileVault2 Info"',
														'format': format4
														})
				
			df_computers_worksheet.conditional_format('$A2:$V$1048576', 
													{'type':'formula',
														'criteria': '=$D2="Computer Hardware Info"',
														'format': format5
														})
				
		elif usingFilter == 'noFilter':
			format1 = df_computers_workbook.add_format({'bg_color': '#D5D8DC'})
			format2 = df_computers_workbook.add_format({'bg_color': '#A3E4D7'})
			format3 = df_computers_workbook.add_format({'bg_color': '#AED6F1'})
			format4 = df_computers_workbook.add_format({'bg_color': '#F5B7B1'})
			format5 = df_computers_workbook.add_format({'bg_color': '#F9E79F'})
			
			df_computers_worksheet.conditional_format('$A2:$V$1048576', 
													{'type':'formula',
														'criteria': '=$B2="Computer Configuration Profile Membership Info"',
														'format': format1
														})
			
			df_computers_worksheet.conditional_format('$A2:$V$1048576', 
													{'type':'formula',
														'criteria': '=$B2="Computer Group Membership Info"',
														'format': format2
														})
			
			df_computers_worksheet.conditional_format('$A2:$AA$1048576', 
													{'type':'formula',
														'criteria': '=$B2="Computer Hardware Local Account Info"',
														'format': format3
														})
			
			df_computers_worksheet.conditional_format('$A2:$V$1048576', 
													{'type':'formula',
														'criteria': '=$B2="Computer Hardware FileVault2 Info"',
														'format': format4
														})
			
			df_computers_worksheet.conditional_format('$A2:$V$1048576', 
													{'type':'formula',
														'criteria': '=$B2="Computer Hardware Info"',
														'format': format5
														})
			
			
		for i, width in enumerate(get_col_widths(df_computers)):
			df_computers_worksheet.set_column(i, i, width)
			
		
	if get_JAMF_Policy_Info == ("yes"):
		df_policy.to_excel(Excelwriter, sheet_name='Jamf Policy Info')
		
		# Get the xlsxwriter workbook and worksheet objects.
		
		df_policy_workbook  = Excelwriter.book
		
		df_policy_worksheet = Excelwriter.sheets['Jamf Policy Info']
		
		format1 = df_policy_workbook.add_format({'bg_color': '#82E0AA'})
		
		TopRowFormat = df_policy_workbook.add_format()
		TopRowFormat.set_bold()
		TopRowFormat.set_font_size(16)
		TopRowFormat.set_align('center')
		TopRowFormat.set_align('vcenter')
		TopRowFormat.set_bottom(2)
		TopRowFormat.set_bg_color('#D5D8DC')
		
		df_policy_worksheet.set_row(0, 30, TopRowFormat)
		
		df_policy_worksheet.conditional_format('$A$2:$AA$1048576', 
												{'type':'formula',
												'criteria': '=ISODD(SUM(IF(FREQUENCY(MATCH($C$2:$C2,$C$2:$C2,0),MATCH($C$2:$C2,$C$2:$C2,0))>0,1)))',
												'format': format1
												})
		
		
		for i, width in enumerate(get_col_widths(df_policy)):
			df_policy_worksheet.set_column(i, i, width)	
	
	
	if get_JAMF_Configuration_Profile_Info == ("yes"):
		df_configProfile.to_excel(Excelwriter, sheet_name='Jamf Configuration Profile Info')
		
		# Get the xlsxwriter workbook and worksheet objects.
		
		df_configProfile_workbook  = Excelwriter.book
		
		df_configProfile_worksheet = Excelwriter.sheets['Jamf Configuration Profile Info']
		
		format1 = df_configProfile_workbook.add_format({'bg_color': '#82E0AA'})
		
		TopRowFormat = df_configProfile_workbook.add_format()
		TopRowFormat.set_bold()
		TopRowFormat.set_font_size(16)
		TopRowFormat.set_align('center')
		TopRowFormat.set_align('vcenter')
		TopRowFormat.set_bottom(2)
		TopRowFormat.set_bg_color('#D5D8DC')
		
		df_configProfile_worksheet.set_row(0, 30, TopRowFormat)
		
		df_configProfile_worksheet.conditional_format('$A$2:$P$1048576', 
													 {'type':'formula',
												      'criteria': '=ISODD(SUM(IF(FREQUENCY(MATCH($C$2:$C2,$C$2:$C2,0),MATCH($C$2:$C2,$C$2:$C2,0))>0,1)))',
												      'format': format1
												     })
		
		
		for i, width in enumerate(get_col_widths(df_configProfile)):
			df_configProfile_worksheet.set_column(i, i, width)	
			
	if get_JAMF_Package_To_Policy_Info == ("yes"):
		df_PackageToPolicy.to_excel(Excelwriter, sheet_name='Jamf Packages To Policy Info')
		
		# Get the xlsxwriter workbook and worksheet objects.
		
		df_PackageToPolicy_workbook  = Excelwriter.book
		
		df_PackageToPolicy_worksheet = Excelwriter.sheets['Jamf Packages To Policy Info']
		
		format1 = df_PackageToPolicy_workbook.add_format({'bg_color': '#82E0AA'})
		
		TopRowFormat = df_PackageToPolicy_workbook.add_format()
		TopRowFormat.set_bold()
		TopRowFormat.set_font_size(16)
		TopRowFormat.set_align('center')
		TopRowFormat.set_align('vcenter')
		TopRowFormat.set_bottom(2)
		TopRowFormat.set_bg_color('#D5D8DC')
		
		df_PackageToPolicy_worksheet.set_row(0, 30, TopRowFormat)
		
		df_PackageToPolicy_worksheet.conditional_format('$A2:$M$1048576', 
												 {'type':'formula',
												  'criteria': '=$B2="Package Not Used"',
												  'format': format1
												  })
		

		for i, width in enumerate(get_col_widths(df_PackageToPolicy)):
			df_PackageToPolicy_worksheet.set_column(i, i, width)	
		
	if get_JAMF_Script_To_Policy_Info == ("yes"):
		df_ScriptToPolicy.to_excel(Excelwriter, sheet_name='Jamf Scripts To Policy Info')
		
		# Get the xlsxwriter workbook and worksheet objects.
		
		df_ScriptToPolicy_workbook  = Excelwriter.book
		
		df_ScriptToPolicy_worksheet = Excelwriter.sheets['Jamf Scripts To Policy Info']
		
		format1 = df_ScriptToPolicy_workbook.add_format({'bg_color': '#82E0AA'})
		
		TopRowFormat = df_ScriptToPolicy_workbook.add_format()
		TopRowFormat.set_bold()
		TopRowFormat.set_font_size(16)
		TopRowFormat.set_align('center')
		TopRowFormat.set_align('vcenter')
		TopRowFormat.set_bottom(2)
		TopRowFormat.set_bg_color('#D5D8DC')
		
		df_ScriptToPolicy_worksheet.set_row(0, 30, TopRowFormat)
		
		df_ScriptToPolicy_worksheet.conditional_format('$A2:$G$1048576', 
													  {'type':'formula',
												       'criteria': '=$B2="Script Not Used"',
												       'format': format1
												      })
		
		
		for i, width in enumerate(get_col_widths(df_ScriptToPolicy)):
			df_ScriptToPolicy_worksheet.set_column(i, i, width)
	
		
	#And finally we save the file
	Excelwriter.save()
	
	print("\n******************** Jamf Instance Info file is now Complete. ********************\n")
	
else:
	
	print("\n******************** No Options Selected. No Report to Run. ********************\n")
	

# Invalidate Bearer Token

invalidateBearerTokenURL = JAMF_url + "/api/v1/auth/invalidate-token"
	
try:
	invalidateToken = http.post(invalidateBearerTokenURL, headers=btHeaders)
	
except HTTPError as http_err:
	print(f'HTTP error occurred: {http_err}')
except Exception as err:
	print(f'Other error occurred: {err}')