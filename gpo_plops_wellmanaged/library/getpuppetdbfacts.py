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
module: getpuppetdbfacts

short_description: Get facts from the Puppet DB for a particular agent.

version_added: "1.0.0"

description: I think you get the gist.

options:
    puppetdb_url:
        description: URL to the PuppetDB API. Typically https://puppet.company.com:8081/pdb/query/v4/inventory
        required: true
        type: str
    cert_file:
        description: Path to public key cert. 
        required: false
        type: str
    pkey_file:
        description: Path to private key file.
        required: false
        type: str
    query_by:
        description: How to retrieve your host, ie: facts.hostname or certname. {"query":["=","$query_by","$query_equals"]}
        required: true
        type: str
    query_equals:
        description: What query_by should equal to, typically a server name. {"query":["=","$query_by","$query_equals"]}
        required: true
        type: str
    validate_certs:
        description: Whether or not to validate certs.
        required: false
        type: bool



author:
    - Matt Cengic (@mcen1)
'''

EXAMPLES = r'''
# tbd
  tasks:
    - name: Get puppet output
      getpuppetdbfacts:
        puppetdb_url: https://puppet.company.com:8081/pdb/query/v4/inventory
        cert_file: '{{puppetdb_public}}'
        pkey_file: '{{puppetdb_private}}'
        query_by: 'facts.hostname'
        query_equals: 'servername'
        validate_certs: no
      register: puppetfact
    - name: print debug
      debug:
        msg: "{{puppetfact}}"

'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
ok: [127.0.0.1] => {
    "msg": {
        "changed": false,
        "failed": false,
        "message": "",
        "original_message": "",
        "output": [
            {
                "certname": "servername.company.com",
                "environment": "dev",
                "facts": {
                    "agent_specified_environment": "dev",
                    "aio_agent_version": "5.5.22",
                    "architecture": "x86_64",
           [...]

'''

from ansible.module_utils.basic import AnsibleModule

import requests
def getPuppetDBFact(queryby,thingname,puppetdbhost,cert_file,pkey_file,doverify):
  url = puppetdbhost
  myobj='{"query":["=","'+queryby+'","'+thingname+'"]}'
#  raise Exception(myobj)
  cert = (cert_file,pkey_file)
  x = requests.post(url, data = myobj,verify=doverify,cert=cert)
  myret=""
  try:
    myret=json.loads(x.text)
    return myret
  except Exception as e:
    return "Exception: "+str(e)+" "+str(x.text)
  return "" 


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        puppetdb_url=dict(type='str', required=True),
        cert_file=dict(type='str', required=False, default=""),
        pkey_file=dict(type='str', required=False, no_log=True, default=""),
        query_by=dict(type='str', required=True),
        query_equals=dict(type='str', required=False),
        validate_certs=dict(type='bool', required=False, default=True),
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
    
    puppetout=getPuppetDBFact(module.params['query_by'],module.params['query_equals'],module.params['puppetdb_url'],module.params['cert_file'],module.params['pkey_file'],module.params['validate_certs']) 

    result['output']=puppetout
    if len(result['output'])==0 or result['output']=="Not Found":
      result['failed'] = True

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
