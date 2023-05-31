# Quick script that will output the workspace ID, name and underlying version of TF.
# Imports
import logging
import requests
import os
import json
import getpass
import time
import concurrent.futures

##
## tfapi_get: makes a single request and throttles in the case of a 429
##
def tfapi_get (url,headers,params=None):
    retry_delay = 0.2 # 200 ms delay
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
## Function to call tfapi_get_data
##
def call_tfapi_get_data(ws):
    rs_url = f"{base_url}/workspaces/{ws['id']}/resources"
    return tfapi_get_data(rs_url, headers, params)


##
## MAIN
##

#Get the TFC / TFE Organization and API
org = os.environ.get("TF_ORG") or input("Enter your TFC organization: ")

# Set API Token
token = os.environ.get("TF_TOKEN")
if token == None:
    try: 
        with open(os.path.expanduser("~/.terraform.d/credentials.tfrc.json")) as fp:
            token = json.load(fp)['credentials']['app.terraform.io']['token']
    except FileNotFoundError:
        getpass.getpass("Enter a TFC Token: ")


# set the base url
base_url = f"https://app.terraform.io/api/v2"

# Get workspaces
ws_url = f"{base_url}/organizations/{org}/workspaces"
headers = {"Authorization": "Bearer " + token}
params = {'page[size]': '100'}
workspaces = tfapi_get_data(ws_url, headers, params)

# Print Summary Table
total = 0
print (f"{'WS ID':24}{'Name':30}{'Version':10}{'Resources':10}")
for ws in workspaces:
    print (f"{ws['id']:24}{ws['attributes']['name']:30}{ws['attributes']['terraform-version']:10}{ws['attributes']['resource-count']:10}")
    total = total + ws['attributes']['resource-count']
print (f"{'Total Resources: '}{total}\n\n")

# Get Resources
start_time = time.perf_counter()
max_threads = 100

# Create Thread Pool Executor
with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
    # Submit API Call to executor
    futures = [executor.submit(call_tfapi_get_data, ws) for ws in workspaces]
    
    resources = []
    
    for future, ws in zip(concurrent.futures.as_completed(futures), workspaces):
        try:
            result = future.result()
            resources += result
            print(f"API Call successful for workspace {ws['id']}")
        except Exception as e:
            print(f"API Call failed for workspace {ws['id']}")

rum = 0
null_rs = 0
data_rs = 0

for rs in resources:
    if rs['attributes']['provider-type'] == "null_resource":
        null_rs += 1
    elif rs['attributes']['provider-type'].startswith("data"):
        data_rs += 1
    else:
        rum += 1
end_time = time.perf_counter()
elapsed_time = end_time - start_time

print (f"RUM: {rum}\nData Resources: {data_rs}\nNull Resources: {null_rs}")
print(f"Elapsed time: {elapsed_time} seconds")