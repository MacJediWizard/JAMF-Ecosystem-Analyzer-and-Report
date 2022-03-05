#!/usr/bin/env python3

##########################################################################################
# General Information
##########################################################################################
#
#	Script created By William Grzybowski March 3, 2022
#
#	Version 1.0	- Initial Creation of Script.
#
#	This script will call the JAMF API and get all Information related to a Policy.
#	It looks up all policies and then returns an csv / Excel spreadsheet.
#
#	Fields returned in csv / Excel are as follows below:
#
#   Policy ID
#	Policy Name
#
#	Policy Category ID
#	Policy Category Name
#
#	Policy Target All Computers
#	Policy Target Computer ID
#	Policy Target Computer Name
#
#	Policy Target Group ID
#	Policy Target Group Name
#	Policy Target Group is Smart
#
#	Policy Exclusion Group ID
#	Policy Exclusion Group Name
#	Policy Exclusion Group is Smart
#
#	Policy Scripts ID
#	Policy Scripts Name
#
#	Policy Package ID
#	Policy Package Name
#
#	Configuration Profile ID
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
#	Configuration Profile Exclusion Group ID
#	Configuration Profile Exclusion Group Name
#	Configuration Profile Exclusion Group is Smart
#
#
#
#
#
#	Jamf Variable Label Names
#
#	$4 -eq JAMF Instance URL (e.g. https://<YourJamf>.jamfcloud.com)
#	$5 -eq Your JAMF API Username
#	$6 -eq Your JAMF API Password
#
#	To test or use without using JAMF Policy you can just send 3 empty arguments 
#	to the script. See example below.
#	(e.g. Get-JIM-Server-Name-from-JAMF-API.sh empty1 empty2 empty3 $4 $5 $6)
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
# JAMF API information
##########################################################################################
JAMF_url = 'https://iqvia.jamfcloud.com'
username = 'jamf-api'
password = 'J@MF@P!acc3s$'

headers = {
	'accept': 'application/json',
}


##########################################################################################
# Imports
##########################################################################################
import requests
from requests.auth import HTTPBasicAuth

#For CSV processing
import pandas as pd
from os.path import exists

##########################################################################################
# Variables
##########################################################################################
#Set Variable for the Data	
dataToCsv = []


##########################################################################################
# Core Script
##########################################################################################

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
#	print(PolicyID)
	
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
	myPolicyScopeLimitationsUsers = getPolicy['policy']['scope']['limitations']['users']
	myPolicyScopeLimitationsUserGroups = getPolicy['policy']['scope']['limitations']['user_groups']
		
	#Scope Element For Exclusions
	myPolicyScopeExclusionsComputers = getPolicy['policy']['scope']['exclusions']['computers']
	myPolicyScopeExclusionsComputerGroups = getPolicy['policy']['scope']['exclusions']['computer_groups']
	
		
		
	#Package Element
	myPackagesInfo = getPolicy['policy']['package_configuration']['packages']
	

	#Script Elements
	myScriptInfo = getPolicy['policy']['scripts']
	
	
	##########################################################################################
	# Process Policy information for csv / Excel
	##########################################################################################
	
	# Individual Policy Info for each record
	getMyPolicyID = (str(myPolicyGeneral['id']) + " - " + myPolicyGeneral['name'])
	getMyPolicyGeneralCatagory = (str(myPolicyGeneralCatagory['id']) + " - " + myPolicyGeneralCatagory['name'])
	
	# Get info for Policies
	print("Working on Policy ID: " + getMyPolicyID)
	
	dataToCsv.append({'Policy ID':str(myPolicyGeneral['id']),\
		\
		'Policy Name':myPolicyGeneral['name'],\
		\
		'Policy Category ID':str(myPolicyGeneralCatagory['id']),\
		\
		'Policy Category Name':f"\"{myPolicyGeneralCatagory['name']}\"",\
		\
		'Type':'Policy',\
		\
		'Policy Target All Computers':str(myPolicyScopeTargetsAllComputers),\
		\
		'Policy Target Computer ID':'',\
		\
		'Policy Target Computer Name':'',\
		\
		'Policy Target Group ID':'',\
		\
		'Policy Target Group Name':'',\
		\
		'Policy Target Group is Smart':'',\
		\
		'Policy Exclusion Computer ID':'',\
		\
		'Policy Exclusion Computer Name':'',\
		\
		'Policy Exclusion Group id':'',\
		\
		'Policy Exclusion Group Name':'',\
		\
		'Policy Exclusion Group is Smart':'',\
		\
		'Policy Package ID':'',\
		\
		'Policy Package Name':'',\
		\
		'Policy Package Category Name':'',\
		\
		'Policy Package Filename':'',\
		\
		'Policy Script ID':'',\
		\
		'Policy Script Name':'',\
		\
		'Policy Script Category Name':'',\
		\
		'Policy Script Filename':'',\
		\
		'Configuration Profile ID':'',\
		\
		'Configuration Profile Name':'',\
		\
		'Configuration Profile Category ID':'',\
		\
		'Configuration Profile Category Name':'',\
		\
		'Configuration Profile Target Computer ID':'',\
		\
		'Configuration Profile Target Computer Name':'',\
		\
		'Configuration Profile Target Group ID':'',\
		\
		'Configuration Profile Target Group Name':'',\
		\
		'Configuration Profile Target Group is Smart':'',\
		\
		'Configuration Profile Exclusion Group id':'',\
		\
		'Configuration Profile Exclusion Group Name':'',\
		\
		'Configuration Profile Exclusion Group is Smart':''})
	
	
	##########################################################################################		
	# Get info for Target Computers	
	##########################################################################################
	for computer in myPolicyScopeTargetsComputers:
		
		dataToCsv.append({'Policy ID':str(myPolicyGeneral['id']),\
			\
			'Policy Name':myPolicyGeneral['name'],\
			\
			'Policy Category ID':str(myPolicyGeneralCatagory['id']),\
			\
			'Policy Category Name':f"\"{myPolicyGeneralCatagory['name']}\"",\
			\
			'Type':'Target Computers',\
			\
			'Policy Target All Computers':'',\
			\
			'Policy Target Computer ID':str(computer['id']),\
			\
			'Policy Target Computer Name':computer['name'],\
			\
			'Policy Target Group ID':'',\
			\
			'Policy Target Group Name':'',\
			\
			'Policy Target Group is Smart':'',\
			\
			'Policy Exclusion Computer ID':'',\
			\
			'Policy Exclusion Computer Name':'',\
			\
			'Policy Exclusion Group id':'',\
			\
			'Policy Exclusion Group Name':'',\
			\
			'Policy Exclusion Group is Smart':'',\
			\
			'Policy Package ID':'',\
			\
			'Policy Package Name':'',\
			\
			'Policy Package Category Name':'',\
			\
			'Policy Package Filename':'',\
			\
			'Policy Script ID':'',\
			\
			'Policy Script Name':'',\
			\
			'Policy Script Category Name':'',\
			\
			'Policy Script Filename':'',\
			\
			'Configuration Profile ID':'',\
			\
			'Configuration Profile Name':'',\
			\
			'Configuration Profile Category ID':'',\
			\
			'Configuration Profile Category Name':'',\
			\
			'Configuration Profile Target Computer ID':'',\
			\
			'Configuration Profile Target Computer Name':'',\
			\
			'Configuration Profile Target Group ID':'',\
			\
			'Configuration Profile Target Group Name':'',\
			\
			'Configuration Profile Target Group is Smart':'',\
			\
			'Configuration Profile Exclusion Group id':'',\
			\
			'Configuration Profile Exclusion Group Name':'',\
			\
			'Configuration Profile Exclusion Group is Smart':''})
	
	
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
		
		
		# Get info for Target Computer Group
		dataToCsv.append({'Policy ID':str(myPolicyGeneral['id']),\
			\
			'Policy Name':myPolicyGeneral['name'],\
			\
			'Policy Category ID':str(myPolicyGeneralCatagory['id']),\
			\
			'Policy Category Name':f"\"{myPolicyGeneralCatagory['name']}\"",\
			\
			'Type':'Target Computer Group',\
			\
			'Policy Target All Computers':'',\
			\
			'Policy Target Computer ID':'',\
			\
			'Policy Target Computer Name':'',\
			\
			'Policy Target Group ID':str(myTargetsComputerGroupInfo['id']),\
			\
			'Policy Target Group Name':myTargetsComputerGroupInfo['name'],\
			\
			'Policy Target Group is Smart':str(myTargetsComputerGroupInfo['is_smart']),\
			\
			'Policy Exclusion Computer ID':'',\
			\
			'Policy Exclusion Computer Name':'',\
			\
			'Policy Exclusion Group id':'',\
			\
			'Policy Exclusion Group Name':'',\
			\
			'Policy Exclusion Group is Smart':'',\
			\
			'Policy Package ID':'',\
			\
			'Policy Package Name':'',\
			\
			'Policy Package Category Name':'',\
			\
			'Policy Package Filename':'',\
			\
			'Policy Script ID':'',\
			\
			'Policy Script Name':'',\
			\
			'Policy Script Category Name':'',\
			\
			'Policy Script Filename':'',\
			\
			'Configuration Profile ID':'',\
			\
			'Configuration Profile Name':'',\
			\
			'Configuration Profile Category ID':'',\
			\
			'Configuration Profile Category Name':'',\
			\
			'Configuration Profile Target Computer ID':'',\
			\
			'Configuration Profile Target Computer Name':'',\
			\
			'Configuration Profile Target Group ID':'',\
			\
			'Configuration Profile Target Group Name':'',\
			\
			'Configuration Profile Target Group is Smart':'',\
			\
			'Configuration Profile Exclusion Group id':'',\
			\
			'Configuration Profile Exclusion Group Name':'',\
			\
			'Configuration Profile Exclusion Group is Smart':''})


	##########################################################################################
	# Get info for exclusion Computers
	##########################################################################################
	for exclusion in myPolicyScopeExclusionsComputers:
		
		dataToCsv.append({'Policy ID':str(myPolicyGeneral['id']),\
			\
			'Policy Name':myPolicyGeneral['name'],\
			\
			'Policy Category ID':str(myPolicyGeneralCatagory['id']),\
			\
			'Policy Category Name':f"\"{myPolicyGeneralCatagory['name']}\"",\
			\
			'Type':'Target Computers',\
			\
			'Policy Target All Computers':myPolicyScopeTargetsAllComputers,\
			\
			'Policy Target Computer ID':'',\
			\
			'Policy Target Computer Name':'',\
			\
			'Policy Target Group ID':'',\
			\
			'Policy Target Group Name':'',\
			\
			'Policy Target Group is Smart':'',\
			\
			'Policy Exclusion Computer ID':str(exclusion['id']),\
			\
			'Policy Exclusion Computer Name':exclusion['name'],\
			\
			'Policy Exclusion Group id':'',\
			\
			'Policy Exclusion Group Name':'',\
			\
			'Policy Exclusion Group is Smart':'',\
			\
			'Policy Package ID':'',\
			\
			'Policy Package Name':'',\
			\
			'Policy Package Category Name':'',\
			\
			'Policy Package Filename':'',\
			\
			'Policy Script ID':'',\
			\
			'Policy Script Name':'',\
			\
			'Policy Script Category Name':'',\
			\
			'Policy Script Filename':'',\
			\
			'Configuration Profile ID':'',\
			\
			'Configuration Profile Name':'',\
			\
			'Configuration Profile Category ID':'',\
			\
			'Configuration Profile Category Name':'',\
			\
			'Configuration Profile Target Computer ID':'',\
			\
			'Configuration Profile Target Computer Name':'',\
			\
			'Configuration Profile Target Group ID':'',\
			\
			'Configuration Profile Target Group Name':'',\
			\
			'Configuration Profile Target Group is Smart':'',\
			\
			'Configuration Profile Exclusion Group id':'',\
			\
			'Configuration Profile Exclusion Group Name':'',\
			\
			'Configuration Profile Exclusion Group is Smart':''})
	
	
	##########################################################################################
	#Get Info for Computer Exclusions groups
	##########################################################################################
	for exclusion in myPolicyScopeExclusionsComputerGroups:
		
		exclusionGroupID = str(exclusion['id'])
		
		#Get Group Info from JAMF API
		url = JAMF_url + "/JSSResource/computergroups/id/" + exclusionGroupID
		
		exclusionGroupData = requests.request("GET", url, headers=headers, auth = HTTPBasicAuth(username, password))
		
		getExclusionGroupData = exclusionGroupData.json()
		
		myExclusionsComputerGroupInfo = getExclusionGroupData['computer_group']
		
		
		dataToCsv.append({'Policy ID':str(myPolicyGeneral['id']),\
			\
			'Policy Name':myPolicyGeneral['name'],\
			\
			'Policy Category ID':str(myPolicyGeneralCatagory['id']),\
			\
			'Policy Category Name':f"\"{myPolicyGeneralCatagory['name']}\"",\
			\
			'Type':'Exclusion Computer Groups',\
			\
			'Policy Target All Computers':'',\
			\
			'Policy Target Computer ID':'',\
			\
			'Policy Target Computer Name':'',\
			\
			'Policy Target Group ID':'',\
			\
			'Policy Target Group Name':'',\
			\
			'Policy Target Group is Smart':'',\
			\
			'Policy Exclusion Computer ID':'',\
			\
			'Policy Exclusion Computer Name':'',\
			\
			'Policy Exclusion Group id':str(myExclusionsComputerGroupInfo['id']),\
			\
			'Policy Exclusion Group Name':myExclusionsComputerGroupInfo['name'],\
			\
			'Policy Exclusion Group is Smart':str(myExclusionsComputerGroupInfo['is_smart']),\
			\
			'Policy Package ID':'',\
			\
			'Policy Package Name':'',\
			\
			'Policy Package Category Name':'',\
			\
			'Policy Package Filename':'',\
			\
			'Policy Script ID':'',\
			\
			'Policy Script Name':'',\
			\
			'Policy Script Category Name':'',\
			\
			'Policy Script Filename':'',\
			\
			'Configuration Profile ID':'',\
			\
			'Configuration Profile Name':'',\
			\
			'Configuration Profile Category ID':'',\
			\
			'Configuration Profile Category Name':'',\
			\
			'Configuration Profile Target Computer ID':'',\
			\
			'Configuration Profile Target Computer Name':'',\
			\
			'Configuration Profile Target Group ID':'',\
			\
			'Configuration Profile Target Group Name':'',\
			\
			'Configuration Profile Target Group is Smart':'',\
			\
			'Configuration Profile Exclusion Group id':'',\
			\
			'Configuration Profile Exclusion Group Name':'',\
			\
			'Configuration Profile Exclusion Group is Smart':''})
	
	
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
		
		
		dataToCsv.append({'Policy ID':str(myPolicyGeneral['id']),\
			\
			'Policy Name':myPolicyGeneral['name'],\
			\
			'Policy Category ID':str(myPolicyGeneralCatagory['id']),\
			\
			'Policy Category Name':f"\"{myPolicyGeneralCatagory['name']}\"",\
			\
			'Type':'Packages',\
			\
			'Policy Target All Computers':'',\
			\
			'Policy Target Computer ID':'',\
			\
			'Policy Target Computer Name':'',\
			\
			'Policy Target Group ID':'',\
			\
			'Policy Target Group Name':'',\
			\
			'Policy Target Group is Smart':'',\
			\
			'Policy Exclusion Computer ID':'',\
			\
			'Policy Exclusion Computer Name':'',\
			\
			'Policy Exclusion Group id':'',\
			\
			'Policy Exclusion Group Name':'',\
			\
			'Policy Exclusion Group is Smart':'',\
			\
			'Policy Package ID':str(myPackageInfo['id']),\
			\
			'Policy Package Name':myPackageInfo['name'],\
			\
			'Policy Package Category Name':f"\"{myPackageInfo['category']}\"",\
			\
			'Policy Package Filename':myPackageInfo['filename'],\
			\
			'Policy Scripts ID':'',\
			\
			'Policy Scripts Name':'',\
			\
			'Configuration Profile ID':'',\
			\
			'Configuration Profile Name':'',\
			\
			'Configuration Profile Category ID':'',\
			\
			'Configuration Profile Category Name':'',\
			\
			'Configuration Profile Target Computer ID':'',\
			\
			'Configuration Profile Target Computer Name':'',\
			\
			'Configuration Profile Target Group ID':'',\
			\
			'Configuration Profile Target Group Name':'',\
			\
			'Configuration Profile Target Group is Smart':'',\
			\
			'Configuration Profile Exclusion Group id':'',\
			\
			'Configuration Profile Exclusion Group Name':'',\
			\
			'Configuration Profile Exclusion Group is Smart':''})
	
	
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
		
		
		dataToCsv.append({'Policy ID':str(myPolicyGeneral['id']),\
			\
			'Policy Name':myPolicyGeneral['name'],\
			\
			'Policy Category ID':str(myPolicyGeneralCatagory['id']),\
			\
			'Policy Category Name':f"\"{myPolicyGeneralCatagory['name']}\"",\
			\
			'Type':'Scripts',\
			\
			'Policy Target All Computers':'',\
			\
			'Policy Target Computer ID':'',\
			\
			'Policy Target Computer Name':'',\
			\
			'Policy Target Group ID':'',\
			\
			'Policy Target Group Name':'',\
			\
			'Policy Target Group is Smart':'',\
			\
			'Policy Exclusion Computer ID':'',\
			\
			'Policy Exclusion Computer Name':'',\
			\
			'Policy Exclusion Group id':'',\
			\
			'Policy Exclusion Group Name':'',\
			\
			'Policy Exclusion Group is Smart':'',\
			\
			'Policy Package ID':'',\
			\
			'Policy Package Name':'',\
			\
			'Policy Package Category Name':'',\
			\
			'Policy Package Filename':'',\
			\
			'Policy Script ID':str(myScriptInfo['id']),\
			\
			'Policy Script Name':myScriptInfo['name'],\
			\
			'Policy Script Category Name':f"\"{myScriptInfo['category']}\"",\
			\
			'Policy Script Filename':myScriptInfo['filename'],\
			\
			'Configuration Profile ID':'',\
			\
			'Configuration Profile Name':'',\
			\
			'Configuration Profile Category ID':'',\
			\
			'Configuration Profile Category Name':'',\
			\
			'Configuration Profile Target Computer ID':'',\
			\
			'Configuration Profile Target Computer Name':'',\
			\
			'Configuration Profile Target Group ID':'',\
			\
			'Configuration Profile Target Group Name':'',\
			\
			'Configuration Profile Target Group is Smart':'',\
			\
			'Configuration Profile Exclusion Group id':'',\
			\
			'Configuration Profile Exclusion Group Name':'',\
			\
			'Configuration Profile Exclusion Group is Smart':''})
		
		
#		##########################################################################################
#		# Process Configuration Profilesinformation for csv / Excel
#		##########################################################################################
#		# Set up url for getting a list of all Configuration Profiles from JAMF API
#url = JAMF_url + "/JSSResource/osxconfigurationprofiles"
#
#response = requests.request("GET", url, headers=headers, auth = HTTPBasicAuth(username, password))
#
#resp = response.json()
#
## For Testing
##print(response.json())
#
#configurationProfiles = resp['os_x_configuration_profiles']
#
#configurationProfiles.sort(key=lambda item: item.get('id'), reverse=False)
#
## Process Configuration Profile List and get information linked to Configuration Profiles
#for configurationProfile in configurationProfiles:
#	
#	# Get configurationProfile ID to do JAMF API lookup
#	configurationProfileID = str(configurationProfile['id']) 
#	
#	#	For Testing
#	#	print(configurationProfileID)
#	
#	# Set up url for getting information from each configurationProfile ID from JAMF API
#	url = JAMF_url + "/JSSResource/osxconfigurationprofiles/id/" + configurationProfileID
#	
#	configurationProfileData = requests.request("GET", url, headers=headers, auth = HTTPBasicAuth(username, password))
#	
#	getconfigurationProfile = configurationProfileData.json()
#	
#	# For Testing
#	#print(getconfigurationProfile)
#	
#	#General Element for ID and Catagory
#	myconfigurationProfileGeneral = getconfigurationProfile['os_x_configuration_profile']['general']
#	myconfigurationProfileGeneralCatagory = getconfigurationProfile['os_x_configuration_profile']['general']['category']
#	
#	#Scope Element for Computer Targets
#	myconfigurationProfileScopeTargetsAllComputers = getconfigurationProfile['os_x_configuration_profile']['scope']['all_computers']
#	myconfigurationProfileScopeTargetsComputers = getconfigurationProfile['os_x_configuration_profile']['scope']['computers']
#	myconfigurationProfileScopeTargetsComputerGroups = getconfigurationProfile['os_x_configuration_profile']['scope']['computer_groups']
#	
#	#Scope Element For Limitation
#	myconfigurationProfileScopeLimitationsUsers = getconfigurationProfile['os_x_configuration_profile']['scope']['limitations']['users']
#	myconfigurationProfileScopeLimitationsUserGroups = getconfigurationProfile['os_x_configuration_profile']['scope']['limitations']['user_groups']
#	
#	#Scope Element For Exclusions
#	myconfigurationProfileScopeExclusionsComputerGroups = getconfigurationProfile['os_x_configuration_profile']['scope']['exclusions']['computers']
#	myconfigurationProfileScopeExclusionsComputerGroups = getconfigurationProfile['os_x_configuration_profile']['scope']['exclusions']['computer_groups']
	
	
		
		
		
		
##########################################################################################
# Process data for Export to csv / Excel
##########################################################################################
# Get export to csv file
df = pd.DataFrame(dataToCsv)

if exists('comps.csv'):
	print('file exists')
	df.to_csv('comps.csv',index=False, mode='a', header=False)
else:
	print('file does not exist')
	df.to_csv('comps.csv', index=False)
	
print("complete")