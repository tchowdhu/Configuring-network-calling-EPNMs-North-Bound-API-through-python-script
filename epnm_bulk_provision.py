#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Python example script showing proper use of the Cisco Sample Code header.
Copyright (c) 2020 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""


from __future__ import absolute_import, division, print_function


#Code starts here

from pprint import pprint
import requests
from requests.auth import HTTPBasicAuth
import urllib3
from electrical_service_template import *
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from epnm_credentials import *
import pandas as pd

"""
* Extract data from Excel
"""
df = pd.read_excel('tdm service list 100s.xlsx', sheet_name='electrical_controller')
df = df.fillna('')
total_service_to_create = len(df)
total_service_to_create = 2
print(total_service_to_create)

"""
* Request Parameters/Headers for EPNM RESTConf API
"""
login_url = "https://{}/restconf/operations/v1/cisco-service-activation:provision-service".format(EPNM_IP)
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
}

"""
* Optional: Open a simple text file for saving response status of proviosioning request
"""
f = open("Provision Status.txt", "w")

"""
* Main Section of the Script
"""
for i in range(total_service_to_create):

    print("+++++++++++++++++++ Provisioning : {} ++++++++++++++++++++++".format(df['pw_service_name'][i]))
    """
    Getting payload from provisioning template.
    * This is platfrom and service-type/provisioning content specific.
    * Primarily focusing on creating TDM services with NCS4200 Platform.
    * Similar concept can be applied to other platforms supported in EPNM.
    """
    payload = Create_Electrical_T3_T1_Service_Commands(pw_service_name=df['pw_service_name'][i],
                                             frame_type=df['frame_type'][i],
                                             service_sub_type=df['service_sub_type'][i],
                                             A_end=df['A_end'][i],
                                             A_controller_type=df['A_controller_type'][i],
                                             A_controller_name=df['A_controller_name'][i],
                                             A_clock_source=df['A_clock_source'][i],
                                             A_T1_channel=df['A_T1_Channel'][i].item(),
                                             Z_end=df['Z_end'][i],
                                             Z_controller_type=df['Z_controller_type'][i],
                                             Z_controller_name=df['Z_controller_name'][i],
                                             Z_clock_source=df['Z_clock_source'][i],
                                             Z_T1_channel=df['Z_T1_Channel'][i].item(),
                                             preferred_path_name=df['preferred_path_name'][i],
                                             is_create_new_path=False, # Looking forward to later implementation, Currently put False always
                                             pw_bandwidth=df['pw_bandwidth'][i].item())

    print(payload)

    #print(df['preferred_path_name'][i])

    """
    * Response from EPNM API 
    """
    response = requests.post(login_url,
                             auth=HTTPBasicAuth(username=USERNAME, password=PASSWORD),
                             headers=headers,
                             data=payload,
                             verify=False)
    response.raise_for_status()
    print("----Request submission response Status-----")
    print(response)
    pprint(response.json())

    """
    * Looking the at the response status for each service based on request-id.
    * For every service provisioning request, EPNM creates a unique request-d, 
      (POST Request used above).
    """
    request_id = response.json()["sa.provision-service-response"]["sa.request-id"]

    stat_response = requests.get(login_url + "?request-id={}".format(request_id),
                                 auth=HTTPBasicAuth(username=USERNAME, password=PASSWORD),
                                 headers=headers,
                                 verify=False)
    stat_response.raise_for_status()
    print("----Provisioning status of this request-----")
    print(stat_response)
    pprint(stat_response.json())

    """
    Saving response status code in a simple text file.
    * Look at the REST response codes (available online)
    * Expected Response is 200(OK) if request is valid and 
      successfully submitted (with no error/exception returned)
    """
    f.write(df['pw_service_name'][i] + ': request submission status = {}; provision-service response status = {}\n'.format(response.status_code,stat_response.status_code))

    """
    * Closing request sessions
    """
    response.close()
    stat_response.close()

"""
* Closing file opened
"""
f.close()


#Code ends here

__author__ = "Tahsin Chowdhury <tchowdhu@cisco.com>"
__contributors__ = [
    "Matthew Nouchi <mnouchi@cisco.com>"
]
__copyright__ = "Copyright (c) 2020 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

indent = 4
print(
    __doc__,
    "Author:",
    " " * indent + __author__,
    "Contributors:",
    "\n".join([" " * indent + name for name in __contributors__]),
    "",
    __copyright__,
    "Licensed Under: " + __license__,
    sep="\n"
)
