# Used to get scan information from cumulative based on query filters
import requests
import concurrent.futures
from datetime import datetime,timedelta
import json
import re
import pandas as pd
requests.packages.urllib3.disable_warnings()



def get_failed_ip(repoID):
    url = rf"https://YOUR_IPADDRESS/rest/analysis"
    # Authentication
    headers = { "x-apikey" : 'accesskey=YOUR_ACCESSKEY; secretkey=YOUR_SECRETKEY'}
    # Data
    data = {
        'type' : 'vuln',
        "query": {
    "name": "",
    "description": "",
    "context": "",
    "createdTime": 0,
    "modifiedTime": 0,
    "groups": [],
    "type": "vuln",
    "tool": "vulnipdetail",
    "sourceType": "cumulative",
    "startOffset": 0,
    "endOffset": 100000,
    "filters": [
    {
    "filterName": "pluginID",
    "operator": "=",
    "value": "19506"
    },
    {
    "filterName": "repositoryIDs",
    "operator": "=",
    "value": repoID
    },
    {
    "filterName": "pluginText",
    "operator": "=",
    "value": "Credentialed checks : no"
    },
    {
    "filterName": "lastSeen",
    "operator": "=",
    "value": "0:30"
    },
    ]
    },
    "sourceType": "cumulative",
    "sortField": "severity",
    "sortDir": "desc",

    }
    # Get request
    res = requests.post(url, headers=headers, verify=False, data=json.dumps(data))
    # Convert request to json
    data = res.json()
    #print(len(data['response']['results']))
    if len(data['response']['results'])> 0 :
       
        c = 0
        osType = ""
        if repoID == "59":
            osType = "Windows 2019"
        if repoID == "47":
            osType = "Windows 2016"
        if repoID == "26":
            osType = "Windows 2012"
        if repoID == "4":
            osType = "Windows 2008"
        if repoID == "77":
            osType = "Rhel 9"
        if repoID == "53":
            osType = "Rhel 8"
        if repoID == "28":
            osType = "Rhel 7"
        if repoID == "6":
            osType = "Rhel 6"    
        failedIpList = data['response']['results'][0]['hosts'][0]['iplist']
        filteredFailedIpList = []
        for i in failedIpList:
            ip = failedIpList[c]['ip']
            dns = failedIpList[c]['dnsName']
            netbios = failedIpList[c]['netbiosName']
            filteredFailedIpList.append([ip,dns,netbios,osType])
            #print(filteredFailedIpList)
            c+=1
        return filteredFailedIpList
   
   



w2019,w2016,w2012,w2008 = ["59","47","26","4"]
windowsList = w2019,w2016,w2012,w2008
r9,r8,r7,r6 = ["77","53","28","6"]
rhelList = r9,r8,r7,r6

combinedOSList = windowsList + rhelList

finalWindowsList = []
for os in combinedOSList:
    test = get_failed_ip(os)
    if test is not None:
        finalWindowsList.append(test)

unnested_data = [item for sublist in finalWindowsList for item in sublist]


columns = ['IP','DNS', ' NetBios', 'OperatingSystem']
df = pd.DataFrame(unnested_data, columns=columns)
df.to_excel('output.xlsx', index=False)
