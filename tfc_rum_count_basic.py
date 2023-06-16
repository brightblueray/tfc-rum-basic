# Quick script that will output the workspace ID, name and underlying version of TF.
# Imports
import argparse
import logging
import requests
import os
import json
import getpass
import time
import concurrent.futures
from urllib.parse import urlparse



##
## tfapi_get: makes a single request and throttles thread in the case of a 429
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
                logging.error("Authorization Error: 401 Unauthorized")
                # break #Actually not fatal ;-)
            elif response.status_code == 404:
                logging.error("Forbidden Error: 404 Not Found")
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



##########################################
## MAIN
##########################################

# Parse command line arguments
args = parse_arguments()
verbose = args.verbose
setup_logging(args.log_level)

# set the base url
base_url = os.environ.get("TF_ADDR") or f"{args.addr}/api/v2"  #ENV Variable overrides commandline
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

# Get Organizations
orgs_url = f"{base_url}/organizations"
org_response = requests.get(orgs_url,headers=headers, params=params)
organizations = tfapi_get_data(orgs_url, headers, params)

summary = {}
est_total = 0

for o in organizations:
    org = o['attributes']['name']
    print(f"\nProcessing organization: {org}")

    # Get workspaces
    ws_url = f"{base_url}/organizations/{org}/workspaces"
    workspaces = tfapi_get_data(ws_url, headers, params)

    # Print WS Detail Table
    total = 0
    if verbose: print (f"{'WS ID':24}{'Name':40}{'Version':10}{'Resources':10}")
    for ws in workspaces:
        if verbose: print (f"{ws['id']:24}{ws['attributes']['name']:40}{ws['attributes']['terraform-version']:10}{ws['attributes']['resource-count']:10}")
        total = total + ws['attributes']['resource-count']
    print (f"{'Total Resources: '}{total}\n\n")
    est_total += total

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
                logging.info(f"API Call successful for workspace {ws['id']}")
            except Exception as e:
                logging.error(f"API Call failed for workspace {ws['id']}")

    rum = 0
    null_rs = 0
    data_rs = 0

    for rs in resources:
        if rs['attributes']['provider-type'] == "null_resource" or rs['attributes']['provider-type'] == "terraform_data":
            null_rs += 1
        elif rs['attributes']['provider-type'].startswith("data"):
            data_rs += 1
        else:
            rum += 1
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    # Create the organization dictionary with the metrics
    org_summary = {
        'workspaces': len(workspaces),
        'RUM': rum,
        'data_resources': data_rs,
        'null_resources': null_rs,
        'elapsed_time': elapsed_time    
    }

    # Add the organization summary to the main summary dictionary
    summary[org] = org_summary


#Print Estimated Total
print(f"Estimated Total: {est_total:,}\n")

# Print the header row
header_row = f"{'Organization':<30}{'Workspaces':<12}{'RUM':<8}{'Data Resources':<16}{'Null Resources':<16}{'Elapsed Time':<15}"
print(header_row)

# Print data for each organization
for org, org_summary in summary.items():
    workspace_count = str(org_summary['workspaces'])
    rum_count = str(org_summary['RUM'])
    data_resources_count = str(org_summary['data_resources'])
    null_resources_count = str(org_summary['null_resources'])
    elapsed_time = f"{org_summary['elapsed_time']:.3f}"

    org_row = f"{org:<30}{workspace_count:12}{rum_count:8}{data_resources_count:16}{null_resources_count:16}{elapsed_time:15}"
    print(org_row)

# Print the totals row
totals = [
    'Total',
    sum(org_summary['workspaces'] for org_summary in summary.values()),
    sum(org_summary['RUM'] for org_summary in summary.values()),
    sum(org_summary['data_resources'] for org_summary in summary.values()),
    sum(org_summary['null_resources'] for org_summary in summary.values()),
    sum(org_summary['elapsed_time'] for org_summary in summary.values())
]
totals_row = f"{'Total':<30}{totals[1]:<12}{totals[2]:<8}{totals[3]:<16}{totals[4]:<16}{totals[5]:.3f}"
print(totals_row)
