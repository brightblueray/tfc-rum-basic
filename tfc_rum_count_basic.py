# Quick script that will output the workspace ID, name and underlying version of TF.
# Imports
import logging
import requests
import os
import json
import getpass
import time

##
## tfapi_get: makes a single request and throttles in the case of a 429
##
def tfapi_get (url,headers,params=None):
    retry_delay = 0.5 # 500 ms delay
    while True:
        try:
            response = requests.get(url,headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            if response.status_code == 401:
                print("Authorization Error: 401 Unauthorized")
                break #Fatal
            elif response.status_code == 404:
                print("Forbidden Error: 404 Not Found")
                break #Fatal
            elif response.status_code == 429:
                print("Rate Limit Error: 429 Too Many Requests, throttling requests")
                time.sleep(retry_delay)
            else:
                print(f"HTTP Error: {response.status_code}")
                print(err)
                break #Fatal
        except requests.exceptions.RequestException as err:
            print("Error occurred during the request.")
            print(err)
            break #Fatal

##
## tfapi_get_data: iterates through all the pages of data before returning
##
def tfapi_get_data (url, headers, params):
    result = tfapi_get(url, headers, params)
    data = result['data']
    while (result['links']['next']):
        result = tfapi_get(result['links']['next'],headers)
        data += result['data']
    return data

##
## MAIN
##

#Get the TFC / TFE Organization and API
org = os.environ.get("TF_ORG") or input("Enter your organization name: ")

# Get API Token
try: 
    with open(os.path.expanduser("~/.terraform.d/credentials.tfrc.json")) as fp:
        token = json.load(fp)['credentials']['app.terraform.io']['token']
except FileNotFoundError:
    token = os.environ.get("TF_TOKEN") or getpass.getpass("Enter a TFC Token: ")

# set the base url
base_url = f"https://app.terraform.io/api/v2"

# Get workspaces
ws_url = f"{base_url}/organizations/{org}/workspaces"
headers = {"Authorization": "Bearer " + token}
params = {'page[size]': '100'}
workspaces = tfapi_get_data(ws_url, headers, params)

# Print Summary Table
total = 0
#print the report header
print (f"{'WS ID':20}{'Name':40}{'Version':10}{'Resources'}")
for ws in workspaces:
    print (f"{ws['id']:20}{ws['attributes']['name']:40}{ws['attributes']['terraform-version']:10}{ws['attributes']['resource-count']}")
    total = total + ws['attributes']['resource-count']
print (f"{'Total Resources: '}{total}")
