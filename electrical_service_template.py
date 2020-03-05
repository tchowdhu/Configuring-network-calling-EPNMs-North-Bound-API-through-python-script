"""
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



import json
import numpy as np

"""
* Pre and Post Config Templates
"""
POST_CONFIG_TEMPLATE_BW = "WS_PSEUDOWIRE_BANDWIDTH"
PRE_CONFIG_TEMPLATE_CTR_PARAMS = "SET_CEM_CONTROLLER_PARAMETERS"

"""
* Template module for service end-points
"""
def electrical_end_point_template(service_sub_type,
                                  end_point,
                                  end_point_controller_type,
                                  end_point_controller_name,
                                  end_point_clock_source,
                                  end_point_lower_channel):

    """ Parameters' name are self descriptive
    :param service_sub_type:
    :param end_point:
    :param end_point_controller_type:
    :param end_point_controller_name:
    :param end_point_clock_source:
    :param end_point_lower_channel:
    :return: template
    """

    template = {
        "sa.tp-ref": "MD=CISCO_EPNM!ND={}!PTP=name={} {};lr=lr-{}".format(end_point, end_point_controller_type.upper(), end_point_controller_name, end_point_controller_type.lower()),
        "sa.cem-data": {
            "sa.clock-source": end_point_clock_source,
            "sa.working-path": {
                "sa.auto-allocate-path": False
            }
        }
    }
    if (service_sub_type.upper() == 'T1' and end_point_controller_type.upper() == 'T3'):
        template["sa.cem-data"]["sa.working-path"]["sa.lower-order-path"] = {
            "sa.available-path-ref": "T1 {}".format(end_point_lower_channel)
        }

    return template

"""
* Template module for adding forwarding path for the target service.
  - In this case, it is MPLS FlexLSP
"""
def forwarding_path_template(preferred_path_name, is_create_new_path=False):

    """ Parameters' name are self descriptive
    :param preferred_path_name:
    :param is_create_new_path:
    :return: template
    """

    if is_create_new_path == False:
        template = {
            "sa.mpls-te-data": {
                "sa.preferred-path-ref": "MD=CISCO_EPNM!VC={}".format(preferred_path_name)
            },
            "sa.pseudowire-settings": {
                "sa.enable-control-word": "true",
                "sa.fallback-to-ldp": "true"
            }
        }
        return template
    else:
        pass  # Will implement later
        #########
        ### Code to be added
        #########

"""
* Template for adding EPNM-Templates
  - This is a post-config template for adjusting service (pseudowire) bandwidth
"""
def post_config_pw_bw_template(template_name, pw_bandwidth):

    """ Parameters' name are self descriptive
    :param template_name:
    :param pw_bandwidth:
    :return: template
    """

    template = {
        "sa.service-template": {
            "sa.type": "postconfig",
            "sa.name": template_name,
            "sa.usage": "Service Create Modify",
            "sa.variables": {
                "sa.variable": [
                    {
                        "sa.name": "Bandwidth",
                        "sa.value": pw_bandwidth
                    }
                ]
            }
        }
    }

    return template

"""
* This is a pre-config template for adjusing electrical (T1/T3) controller parameters
*** Will add later.
"""
#########
### Code to be added
#########

"""
Combining different Template modules defined above to create a final template for the target service
"""
def Create_Electrical_T3_T1_Service_Commands(pw_service_name,
                                   frame_type,
                                   service_sub_type,
                                   A_end,
                                   A_controller_type,
                                   A_controller_name,
                                   A_clock_source,
                                   A_T1_channel,
                                   Z_end,
                                   Z_controller_type,
                                   Z_controller_name,
                                   Z_clock_source,
                                   Z_T1_channel,
                                   preferred_path_name = None,
                                   is_create_new_path = False,
                                   pw_bandwidth = None):

    """ Parameters' name are self descriptive
    :param pw_service_name:
    :param frame_type:
    :param service_sub_type:
    :param A_end:
    :param A_controller_type:
    :param A_controller_name:
    :param A_clock_source:
    :param A_T1_channel:
    :param Z_end:
    :param Z_controller_type:
    :param Z_controller_name:
    :param Z_clock_source:
    :param Z_T1_channel:
    :param preferred_path_name:
    :param is_create_new_path:
    :param pw_bandwidth:
    :return: serialized form of json template
    """

    """
    * Electrical_T3_T1_Template; defining with common key-values
    * 
    """
    Electrical_T3_T1_Template = {
        "sa.service-order-data": {
            "sa.customer-ref": "MD=CISCO_EPNM!CUSTOMER=Infrastructure",
            "sa.service-name": pw_service_name,
            "sa.service-description": pw_service_name,
            "sa.service-type": "tdm-cem",
            "sa.service-subtype": service_sub_type.lower(),
            "sa.service-activate": True,
            "sa.cem-data": {
                "sa.transport-settings": {
                    "sa.frame-type": frame_type
#                    "sa.payload-size":"192",
#                    "sa.dejitter-buffer-size":"6"

                }
            }
        }
    }

    """
    * Adding A and Z end points in the Template 
    """
    termination_ends = list()
    termination_ends.append(
        electrical_end_point_template(service_sub_type,
                                      A_end,
                                      A_controller_type,
                                      A_controller_name,
                                      A_clock_source,
                                      A_T1_channel)
    )
    termination_ends.append(
        electrical_end_point_template(service_sub_type,
                                      Z_end,
                                      Z_controller_type,
                                      Z_controller_name,
                                      Z_clock_source,
                                      Z_T1_channel)
    )

    termination_ends_config_list = {}
    termination_ends_config_list["sa.termination-point-config"] = termination_ends
    Electrical_T3_T1_Template["sa.service-order-data"]["sa.termination-point-list"] = termination_ends_config_list

    """
    * Adding forwarding path section in the template
    """
    if (preferred_path_name != None and preferred_path_name != '' and preferred_path_name != ""):
        path_data = forwarding_path_template(preferred_path_name, is_create_new_path)
        if path_data != None: Electrical_T3_T1_Template["sa.service-order-data"]["sa.forwarding-path"] = path_data

    """
    * Adding EPNM-templates (post-config) section in the template
    """
    if (pw_bandwidth != None and pw_bandwidth != '' and pw_bandwidth != ""):
        Electrical_T3_T1_Template["sa.service-order-data"]["sa.service-templates"] = post_config_pw_bw_template(POST_CONFIG_TEMPLATE_BW, pw_bandwidth)

    """
    * Adding EPNM-templates (pre-config) section in the template
    """
    #########
    ### Code to be added
    #########

    """
    * Returning serialized template.
    """
    return json.dumps(Electrical_T3_T1_Template)