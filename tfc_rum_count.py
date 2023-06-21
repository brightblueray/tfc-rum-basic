# Imports
import argparse
import concurrent.futures
import datetime
import getpass
import json
import logging
import os
import requests
import time
from urllib.parse import urlparse

##
## tfapi_get: makes a single request and throttles thread in the case of a 429
##
def tfapi_get (url,headers,params=None):
    retry_delay = 0.2 # 200 ms delay
    while True:
        try:
            response = requests.get(url,headers=headers, params=params)
            # logging.info(f"Trying: {response.url}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            if response.status_code == 401:
                logging.error("Authorization Error: 401 Unauthorized: {response.url}")
                # break #Actually not fatal ;-)
            elif response.status_code == 404:
                logging.error(f"Forbidden Error: 404 Not Found: {response.url}")
                break #Fatal
            elif response.status_code == 429:
                # print("Rate Limit Error: 429 Too Many Requests, throttling requests")
                logging.warning("Rate Limit Error: 429 Too Many Requests, throttling requests")
                time.sleep(retry_delay)
            else:
                logging.error(f"HTTP Error: {response.status_code}")
                logging.error(err)
                break #Fatal
        except requests.exceptions.RequestException as err:
            logging.error("Error occurred during the request.")
            logging.error(err)
            break #Fatal



##
## tfapi_get_data: iterates through all the pages of data before returning
##
def tfapi_get_data (url, headers, params):
    result = tfapi_get(url, headers, params)
    data = []
    data += result['data']
    while (result['links']['next']):
        result = tfapi_get(result['links']['next'],headers)
        data += result['data']
    return data



def tfapi_get_state (url, headers, params):
    resources = []
    result = tfapi_get(url, headers, params)
    data = result['data']
    resources += data['attributes']['resources']
    return resources


def get_resources(ws):
    rum = 0
    null_rs = 0
    data_rs = 0
    total = 0
    rs_url = f"{base_url}{api_ver}/workspaces/{ws['id']}/resources"
    state_url = f"{base_url}{api_ver}/workspaces/{ws['id']}/current-state-version"
    
    # attempt to get resources
    resources = tfapi_get_data(rs_url, headers, params)
    # if no resources, try the state file
    if resources != []:
        for rs in resources:
            if rs['attributes']['provider-type'] == "null_resource":
                null_rs += 1
            elif rs['attributes']['provider-type'].startswith("data") or rs['attributes']['provider-type'] == "terraform_data":
                data_rs += 1
            else:
                rum += 1
    else: 
        resources = tfapi_get_state(state_url, headers, params)
        for rs in resources:
            if rs['type'] == 'null_resource':
                null_rs += rs['count']
            elif rs['type'].startswith("data") or rs['type'] == "terraform_data":
                data_rs += rs['count']
            else:
                rum += rs['count']
    
    return {'rum': rum , 'null_rs':null_rs, 'data_rs': data_rs, 'total':rum+null_rs+data_rs}    



##
## Function Set-up Logging
##
def setup_logging(log_level):
    log_format = "%(levelname)s:%(asctime)s %(message)s"
    logging.basicConfig(format=log_format, level=log_level)


##
## Function Parse command line args
##
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Script to output basic Workspace Info (workspace ID, name, version, # resources) as well as an accurate RUM count."
    )
    parser.add_argument(
        "-l",
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="ERROR",
        help="Set the logging level (default: ERROR)",
    )
    parser.add_argument(
        "-a",
        "--addr",
        default="https://app.terraform.io",
        help="URL for your TFE Server (default: 'https://app.terraform.io')",
    )
    parser.add_argument(
        '-v', 
        '--verbose',
        help="Verbose will print details for every organization, otherwise only a summary table will appear.",
        action='store_true')

    return parser.parse_args()



# def print_summary(rum_sum):
#     print ("Header")
#     for org in rum_sum:
#         for ws in org['workspaces']:
#             print (f"{org['id']:<26}{ws['id']:<20}{ws['name']:<40}{ws['terraform-version']:<10}{datetime.datetime.strptime(ws['last-updated'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d'):13} \
#               {ws['resource-count']:<10}{ws['resources']['rum']:<10}{ws['resources']['data_rs']:<10}{ws['resources']['null_rs']:<10}{ws['resources']['total']:<10}")


def print_summary(rum_sum):
    print("Header")

    # Initialize variables for subtotal and grand total
    org_subtotal = {'rum': 0, 'null_rs': 0, 'data_rs': 0, 'total': 0}
    grand_total = {'rum': 0, 'null_rs': 0, 'data_rs': 0, 'total': 0}

    # Define the column headers with right-justification
    headers = ["ID", "Name", "Version", "Last Updated", "Resource Count", "RUM", "Data RS", "Null RS", "Total"]
    header_format = "{:<20}{:<40}{:<10}{:<13}{:<15}{:>10}{:>10}{:>10}{:>10}"
    print(header_format.format(*headers))

    for org in rum_sum:
        print(f"\nOrg ID: {org['id']}")
        for ws in org['workspaces']:
            # Define the row values with right-justification
            row_values = [
                ws['id'], ws['name'], ws['terraform-version'],
                datetime.datetime.strptime(ws['last-updated'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d'),
                ws['resource-count'], ws['resources']['rum'],
                ws['resources']['data_rs'], ws['resources']['null_rs'], ws['resources']['total']
            ]
            row_format = "{:<20}{:<40}{:<10}{:<13}{:<15}{:>10}{:>10}{:>10}{:>10}"
            print(row_format.format(*row_values))

            # Accumulate subtotal for the organization
            org_subtotal['rum'] += ws['resources']['rum']
            org_subtotal['null_rs'] += ws['resources']['null_rs']
            org_subtotal['data_rs'] += ws['resources']['data_rs']
            org_subtotal['total'] += ws['resources']['total']

            # Accumulate grand total
            grand_total['rum'] += ws['resources']['rum']
            grand_total['null_rs'] += ws['resources']['null_rs']
            grand_total['data_rs'] += ws['resources']['data_rs']
            grand_total['total'] += ws['resources']['total']

        # Print subtotal row for the organization
        print(f"Org Subtotal:")
        print(row_format.format('', '', '', '', '', org_subtotal['rum'], org_subtotal['data_rs'], org_subtotal['null_rs'], org_subtotal['total']))
        # Reset subtotal for the next organization
        org_subtotal = {'rum': 0, 'null_rs': 0, 'data_rs': 0, 'total': 0}

    # Print grand total row
    print(f"\nGrand Total:")
    print(row_format.format('', '', '', '', '', grand_total['rum'], grand_total['data_rs'], grand_total['null_rs'], grand_total['total']))



##########################################
## MAIN
##########################################

# Parse command line arguments
args = parse_arguments()
verbose = args.verbose
setup_logging(args.log_level)

# set the base url
base_url = os.environ.get("TF_ADDR") or f"{args.addr}"  #ENV Variable overrides commandline
logging.info(f"Using Base URL: {base_url}")
server = urlparse(base_url).netloc  # Need the server to parse the token from helper file

# Set API Token
token = os.environ.get("TF_TOKEN")     #ENV Variable first
if token is None:
    try: 
        with open(os.path.expanduser("~/.terraform.d/credentials.tfrc.json")) as fp:
            credentials = json.load(fp)['credentials']
            if server in credentials:
                token = credentials[server]['token']
            else:
                default_server = "app.terraform.io"  # Default server value
                token = credentials.get(default_server, {}).get('token')
            logging.info(f"Using Token from ~/.terraform.d/credentials.tfrc.json")
    except FileNotFoundError:
        token = getpass.getpass("Enter a TFC Token: ")
        logging.info(f"Using Token from user prompt")
else:
    logging.info(f"Using Token from $TF_TOKEN")

# Set Headers & Params
headers = {"Authorization": "Bearer " + token}
params = {'page[size]': '100'}
api_ver = "/api/v2"

# from packaging import version
# old_ver = version.parse("0.12")
orgs_url = f"{base_url}{api_ver}/organizations"
org_response = tfapi_get_data(orgs_url, headers, params)
rum_sum = []  # rum_sum a list of organization results

# Iterate over each org
for o in org_response:
    logging.info(f"Processing Org: {o['id']}")
    org_sum = {}  # Initialize org summary
    org_sum['id'] = o['id'] # Set the id to org_id being processed
    org_sum['workspaces'] = [] # Initialize the list of workspaces for the org
    ws_url = f"{base_url}{api_ver}/organizations/{o['id']}/workspaces" # build the url for ws list
    workspaces = tfapi_get_data(ws_url, headers, params) # Get all the workspaces for the org
    
    for ws in workspaces:
        logging.info(f"Processing ws: {ws['id']}")
        ws_sum = {}
        ws_sum['id'] = ws['id']
        ws_sum['name'] = ws['attributes']['name']
        ws_sum['resource-count'] = ws['attributes']['resource-count']
        ws_sum['terraform-version'] = ws['attributes']['terraform-version']
        ws_sum['last-updated'] = ws['attributes']['latest-change-at']
        rs_sum = {'rum':0 , 'null_rs':0, 'data_rs':0, 'total': 0}
        if ws_sum['resource-count'] > 0:
            rs_sum = get_resources(ws)
        ws_sum['resources'] = rs_sum
            
        org_sum['workspaces'].append(ws_sum)
        
    rum_sum.append(org_sum)
print_summary(rum_sum)