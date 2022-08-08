#!/usr/bin/python
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import ast
import sys
import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


DOCUMENTATION = r'''
---
module: ansible2itop

short_description: Get or create info from iTOP

version_added: "1.0.0"

description: I think you get the gist.

options:
    action:
        description: Whether to get or create the CI.
        required: true
        type: str
    itop_url:
        description: URL to the iTOP API. Typically https://itop.company.com/itop/web/webservices/rest.php?version=1.3
        required: true
        type: str
    username:
        description: Username that has API access. 
        required: true
        type: str
    password:
        description: We love our passwords don't we folks? 
        required: true
        type: str
    itop_class:
        description: The class we're searching for. Case-sensitive. Examples: VirtualMachine, Server, ApplicationSolution.
        required: true
        type: str
    validate_certs:
        description: Whether or not we validate SSL certs. Defaults to no
        required: false
        type: bool
    itop_fields:
        description: For 'get' actions, what fields we want to receive. For 'create', fields we wish to put into our new CI we're creating. You may get warnings about type conversions for the 'create' action. This is expected. Unsure how to fix it, sorry.
        required: true
        type: str
    oql_query:
        description: The OQL to execute in iTOP. Reminder, this is case-sensitive. Only used for 'get' actions.
        required: false
        type: str
    comment:
        description: Comment when creating a CI. Only used for 'create' actions. Will default to 'created by ansible'.
        required: false
        type: str


author:
    - Matt Cengic (@mcen1)
'''

EXAMPLES = r'''
# Create a new CI
    - name: Create newvm in iTop
      ansible2itop:
        action: "create"
        itop_url: "https://itop.company.com/itop/web/webservices/rest.php?version=1.3"
        username: "someone"
        password: "secret"
        itop_class: "VirtualMachine"
        itop_fields:
          name: "newvm"
          org_id: 1
          virtualhost_id: 9999
          status: "implementation"
      register: testout
    - name: dump test output
      debug:
        msg: "{{ testout }}"

# Look up ApplicationSolution
    - name: Look up Application Solution in iTOP 
      ansible2itop:
        action: "get"
        itop_url: "https://itop.company.com/itop/web/webservices/rest.php?version=1.3"
        username: "someone"
        password: "secret"
        itop_class: 'ApplicationSolution'
        oql_query: "SELECT ApplicationSolution WHERE name = 'Garbage App We Paid A Lot Of Money For'"
        itop_fields: '*'
      register: testout
    - name: dump test output
      debug:
        msg: "{{ testout }}"
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
        "class": "ApplicationSolution",
        "code": 0,
        "fields": {
            "abbrev": "",
            "applicationsolution_list": [],
            "business_criticity": "low",
            "businessprocess_list": [],
            "costcenter": "9999999",
            "description": "",
            "documents_list": [],
         [...]

# here's a creation example
        "output": {
            "code": 0,
            "message": null,
            "objects": {
                "VirtualMachine::1234": {
                    "class": "VirtualMachine",
                    "code": 0,
                    "fields": {
                        "id": "1234"
                    },
                    "key": "1234",
                    "message": "created"
                }
            }
        }

'''

from ansible.module_utils.basic import AnsibleModule

def createItop(itopurl,field,classname,validate_certs,authuser,authpass,comment):
  fielda=ast.literal_eval(field)
  fieldsan=json.loads(json.dumps(fielda))
  json_data = {
   "operation": "core/create",
   "class": classname,
   "output_fields": "id",
   "comment": comment,
   "fields": fieldsan
  }
  encoded_data = json.dumps(json_data)
  r = requests.post(itopurl, verify=validate_certs, data={'auth_user': authuser, 'auth_pwd': authpass, 'json_data': encoded_data})
  result = json.loads(r.text)
  return result 



def getItop(itopurl,myquery,field,classname,validate_certs,authuser,authpass):
  json_data = {
                  "operation": "core/get",
                  "class": classname,
                  "key": myquery,
                  "output_fields": field
                }
  encoded_data = json.dumps(json_data)
  r = requests.post(itopurl, verify=validate_certs, data={'auth_user': authuser, 'auth_pwd': authpass, 'json_data': encoded_data})
  result = json.loads(r.text)
  try:
    rezobjs={"code":result['code'],"items":[]}
    if result['code']!=0:
      return json.loads(r.text)
    if "objects" in result:
      for item in result["objects"]:
        rezobjs["items"].append(result['objects'][item])
    return rezobjs
  except:
    return json.loads(r.text)
  return json.loads(r.text)



def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        action=dict(type='str', required=True),
        itop_url=dict(type='str', required=True),
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        itop_class=dict(type='str', required=True),
        oql_query=dict(type='str', required=False),
        validate_certs=dict(type='bool', required=False, default=True),
        comment=dict(type='str', required=False, default="Added by ansible"),
        itop_fields=dict(type='str', required=True)
    )

    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(**result)
    
    # only two actions supported at time of writing
    if module.params['action']=="get":
      itopoutput=getItop(module.params['itop_url'],module.params['oql_query'],module.params['itop_fields'],module.params['itop_class'],module.params['validate_certs'],module.params['username'],module.params['password'])
    elif module.params['action']=="create":
      itopoutput=createItop(module.params['itop_url'],module.params['itop_fields'],module.params['itop_class'],module.params['validate_certs'],module.params['username'],module.params['password'],module.params['comment'])

    result['output']=itopoutput
    if result['output']['code']!=0:
      result['failed'] = True

    if result['output']['code']==0 and  module.params['action']=="create":
      result['changed'] = True


    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
