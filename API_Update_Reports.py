"""
Purpose: Update Tenable report paragraphs for scan dates and asset counts. This is because Tenable does not provide any efficient way of doing so. You have to manually click into each one update the dates and also screen refreshes and hard to tell which have been updated.

"""

import requests
requests.packages.urllib3.disable_warnings()
import json
import csv
from datetime import datetime, timedelta
import os


def get_weekly_id():
    """ Purpose: Get ID of each report scheduled to run weekly, return weekly_id_list to be used in other functions"""
    weekly_id_list = []
    with open(r"<temp_dir>/weekly_report_id.csv", mode ='r') as file:
        csv_reader = csv.reader(file)
        for line in csv_reader:
            weekly_id_list = weekly_id_list + line

    return weekly_id_list

def get_date_range():
    """ Purpose: Get the dates formatted showing from the previous thursday to the current wednesday """
    # Get todays date
    today = datetime.today()
    # Get days until last thursday by finding out today weekday value (0,1,2,3,4,5,6) -3 because thursday is three days before sunday
    days_until_previous_thursday = (today.weekday() - 3)%7
    # Get the date of previous thursday by taking away the amount of days found in days_until_previous_thursday from today and then format to correct format.
    previous_thursday = (today - timedelta(days=days_until_previous_thursday)).strftime("%b %d, %Y")
    # Get days until last thursday by finding out today weekday value (0,1,2,3,4,5,6) 9 because wednesday is 9 days after sunday
    days_until_upcoming_wednesday = (9 - today.weekday()) %7
    # Get the date of previous thursday by taking away the amount of days found in days_until_previous_thursday from today and then format to correct format.
    upcoming_wednesday = (today + timedelta(days=days_until_upcoming_wednesday)).strftime("%b %d, %Y")
    date_range = f"{previous_thursday} - {upcoming_wednesday}"
    return date_range


def get_report(report_id):
    """ Purpose: Get request to pull the data from API, return in json format under data var"""
    # Get request URL
    url = rf"https://<IP_ADDRESS>/rest/reportDefinition/{report_id}?fields=definition"
    # Authentication
    headers = { "x-apikey" : 'accesskey=<ACCESS_KEY>; secretkey=<SECRET_KEY>'}
    # Get request
    res = requests.get(url, headers=headers, verify=False)
    # Convert request to json
    data = res.json()
    #print(data)
    return data

def patch_report(report_id,json_data):
    """ Purpose: Patch request using data, after json data has been manipulated in replace_text function"""
    # Get request URL
    url = rf"https://<IP_ADDRESS>/rest/reportDefinition/{report_id}?fields=definition"
    # Authentication
    headers = { "x-apikey" : 'accesskey=<ACCESS_KEY>; secretkey=<SECRET_KEY>'}
    updated_res = requests.patch(url, data=json.dumps(json_data), headers=headers, verify=False)
    #print(updated_res.content)
   
def replace_text(data):
    """ Purpose: Loop through each of the values in data, if it meets the critera defined, update the values and return"""
    date_range = get_date_range()
    if isinstance(data, dict):
        for key, value in data.items():
            #print(value)
            if isinstance(value,(dict,list)):
                replace_text(value)
            elif isinstance(value ,str) and '<TEXT_VALUE>' in value.lower():
                data[key] = f"<TEXT_VALUE> {date_range}"  
            elif isinstance(value ,str) and '<TEXT_VALUE>' in value.lower():
                #print(g_report_id)
                if(g_report_id == '<REPORT_ID>'):
                    count = ip_counts_dict['Windows2019']
                    data[key] = f"<STRING_VALUE>: {count}"
                elif(g_report_id == '<REPORT_ID>'):
                    count = ip_counts_dict['RedHat8']
                    data[key] = f"<STRING_VALUE> {count}"
    elif isinstance(data, list):
        for item in data:
            replace_text(item)

def get_asset_count():
    """ Purpose: Get request to pull count data from asset API to be used in patch requests"""
    asset_ids = {'RedHat8':'<REPORT_ID>','Windows2019':'<REPORT_ID>'}
    asset_ip_counts_dict={}
    headers = { "x-apikey" : 'accesskey=<ACCESS_KEY>; secretkey=<SECRET_KEY>'}
    for key,value in asset_ids.items():
        asset_id = value
        url = rf"https://<IP_ADDRESS>/rest/asset/{asset_id}?fields=ipCount"
        asset_response = requests.get(url, headers=headers, verify=False)
        asset_response_json = (json.loads(asset_response.content))
        if key == 'Redhat8':
            r8_ipcount = (asset_response_json['response']['ipCount'])
            asset_ip_counts_dict['Redhat8'] = Redhat8_ipcount
        if key == 'Windows2019':
            Windows2019_ipcount = (asset_response_json['response']['ipCount'])
            asset_ip_counts_dict['Windows2019'] = Windows2019_ipcount
    return(asset_ip_counts_dict)
def main():  
    # Get weekly ID list
    weekly_id_list = get_weekly_id()
    # Get Date Range for reports
    date_range = get_date_range()
    global ip_counts_dict
    ip_counts_dict = get_asset_count()
    for i in weekly_id_list:
        global g_report_id
        g_report_id = i
        data = get_report(i)
        replace_text(data)
        json_data = (data['response'])
        patch_report(i,json_data)
   
       
if __name__ == "__main__":
        # Call the main function
        main()
