#!/usr/bin/env python3

import requests
from requests.auth import HTTPBasicAuth


JAMF_url = "https://qaiqvia.jamfcloud.com"
headers = {
	'accept': 'application/json',
	'Cookie': 'APBALANCEID=aws.usw2-std-parker3-tc-15'
}

	
dataToCsv = []


url = JAMF_url + "/JSSResource/policies"

response = requests.request("GET", url, headers=headers, auth = HTTPBasicAuth('jamf-api', 'J@MF@P!acc3s$'))

resp = response.json()

policies = resp['policies']

policies.sort(key=lambda item: item.get('id'), reverse=False)

#print(response.json())

for policy in policies:
	
	#print(str(policy['id']) + " " + policy['name'])
	PolicyID = str(policy['id']) 
	
#	print(PolicyID)
	
	url = JAMF_url + "/JSSResource/policies/id/" + PolicyID
	
	PolicyData = requests.request("GET", url, headers=headers, auth = HTTPBasicAuth('jamf-api', 'J@MF@P!acc3s$'))
	
	getPolicy = PolicyData.json()
	
	
	#General Element
	myPolicyGeneral = getPolicy['policy']['general']
	myPolicyGeneralCatagory = getPolicy['policy']['general']['category']
	
	#Scope element
	myPolicyScopeTargetsComputers = getPolicy['policy']['scope']['computers']
	myPolicyScopeTargetsComputerGroups = getPolicy['policy']['scope']['computer_groups']

	#Limitation Element
	myPolicyScopeLimitationsUserGroups = getPolicy['policy']['scope']['limitations']['user_groups']
		
	#Exclusions Element
	myPolicyScopeExclusionsComputerGroups = getPolicy['policy']['scope']['exclusions']['computer_groups']
	myPolicyScopeExclusionsUserGroups = getPolicy['policy']['scope']['exclusions']['user_groups']
		
		
		
	#Package Element
	myPackagesInfo = getPolicy['policy']['package_configuration']['packages']
	
	#Script Elements
	myScriptInfo = getPolicy['policy']['scripts']
		
		
		
	# Process information
	
	#Policy Info
	getMyPolicyID = (str(myPolicyGeneral['id']) + " - " + myPolicyGeneral['name'])
	getMyPolicyGeneralCatagory = (str(myPolicyGeneralCatagory['id']) + " - " + myPolicyGeneralCatagory['name'])
	
	
	# Get Scope Computers
	for computer in myPolicyScopeTargetsComputers:
		dataToCsv.append({'Policy ID':str(myPolicyGeneral['id']),\
			'Policy Name':myPolicyGeneral['name'],\
			'Policy Category ID':str(myPolicyGeneralCatagory['id']),\
			'Policy Category Name':f"\"{myPolicyGeneralCatagory['name']}\"",\
			'Policy Target Computer ID':str(computer['id']),\
			'Policy Target Computer Name':computer['name'],\
			'Policy Target Group ID':'',\
			'Policy Target Group Name':'',\
			'Policy Exclusion Group id':'',\
			'Policy Exclusion Group Name':'',\
			'Policy Scripts ID':'',\
			'Policy Scripts Name':'',\
			'Policy Package ID':'',\
			'Policy Package Name':'',\
			'Configuration Profile ID':'',\
			'Configuration Profile Name':'',\
			'Configuration Profile Category':'',\
			'Configuration Profile Target Computer ID':'',\
			'Configuration Profile Target Computer Name':'',\
			'Configuration Profile Target Group ID':'',\
			'Configuration Profile Target Group Name':'',\
			'Configuration Profile Exclusion Group id':'',\
			'Configuration Profile Exclusion Group Name':'',\
			'is-smart':'',\
			'type':'Policy Target Computers'})
		
		getMyPolicyScopeTargetsComputer = "   ***   The Computer Target ID is: " + (str(computer['id']) + " - " + computer['name'])
		print("The Policy ID is: " + getMyPolicyID + getMyPolicyScopeTargetsComputer)
		
		# Get Scope Compouters
		for target in myPolicyScopeTargetsComputerGroups:
			dataToCsv.append({'Policy ID':str(myPolicyGeneral['id']),\
				'Policy Name':myPolicyGeneral['name'],\
				'Policy Category ID':str(myPolicyGeneralCatagory['id']),\
				'Policy Category Name':f"\"{myPolicyGeneralCatagory['name']}\"",\
				'Policy Target Computer ID':'',\
				'Policy Target Computer Name':'',\
				'Policy Target Group ID':str(target['id']),\
				'Policy Target Group Name':str(target['name']),\
				'Policy Exclusion Group id':'',\
				'Policy Exclusion Group Name':'',\
				'Policy Scripts ID':'',\
				'Policy Scripts Name':'',\
				'Policy Package ID':'',\
				'Policy Package Name':'',\
				'Configuration Profile ID':'',\
				'Configuration Profile Name':'',\
				'Configuration Profile Category':'',\
				'Configuration Profile Target Computer ID':'',\
				'Configuration Profile Target Computer Name':'',\
				'Configuration Profile Target Group ID':'',\
				'Configuration Profile Target Group Name':'',\
				'Configuration Profile Exclusion Group id':'',\
				'Configuration Profile Exclusion Group Name':'',\
				'is-smart':'',\
				'type':'Policy Target Group'})
			
			getMyPolicyScopeTargetsComputerGroups = "   ***   The Computer Target Groups ID is: " + (str(target['id']) + " - " + target['name'])
			print("The Policy ID is: " + getMyPolicyID + getMyPolicyScopeTargetsComputerGroups)
			
			
			
			#Get Scope Computer Exclusions
		for exclusion in myPolicyScopeExclusionsComputerGroups:
			dataToCsv.append({'Policy ID':str(myPolicyGeneral['id']),\
				'Policy Name':myPolicyGeneral['name'],\
				'Policy Category ID':str(myPolicyGeneralCatagory['id']),\
				'Policy Category Name':f"\"{myPolicyGeneralCatagory['name']}\"",\
				'Policy Target Computer ID':'',\
				'Policy Target Computer Name':'',\
				'Policy Target Group ID':'',\
				'Policy Target Group Name':'',\
				'Policy Exclusion Group id':str(exclusion['id']),\
				'Policy Exclusion Group Name':exclusion['name'],\
				'Policy Scripts ID':'',\
				'Policy Scripts Name':'',\
				'Policy Package ID':'',\
				'Policy Package Name':'',\
				'Configuration Profile ID':'',\
				'Configuration Profile Name':'',\
				'Configuration Profile Category':'',\
				'Configuration Profile Target Computer ID':'',\
				'Configuration Profile Target Computer Name':'',\
				'Configuration Profile Target Group ID':'',\
				'Configuration Profile Target Group Name':'',\
				'Configuration Profile Exclusion Group id':'',\
				'Configuration Profile Exclusion Group Name':'',\
				'is-smart':'',\
				'type':'Policy Exclusion Group'})
			
			getMyPolicyScopeExclusionsComputerGroups = "   ***   The Computer Exclusion Groups ID is: " + (str(exclusion['id']) + " - " + exclusion['name'])
			print("The Policy ID is: " + getMyPolicyID + getMyPolicyScopeExclusionsComputerGroups)
			
			
			
			
			

			
			
			# Get Sexport to csv file

import pandas as pd
from os.path import exists

df = pd.DataFrame(dataToCsv)

if exists('comps.csv'):
	print('file exists')
	df.to_csv('comps.csv',index=False, mode='a', header=False)
else:
	print('file does not exist')
	df.to_csv('comps.csv', index=False)
	
print("complete")