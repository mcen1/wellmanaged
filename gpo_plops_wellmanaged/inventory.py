#!/bin/env python3
import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
def getFromITOP(citype):
  ITOP_URL = 'https://itop.sherwin.com/itop/web/'
  ITOP_USER = "linuxapi"
  ITOP_PWD = "api"
  osowner="(osowner='GCD Linux' OR osowner='Stores Unix' OR osowner='HPUX Support')"
  if citype=="Hypervisor":
    osowner="(osowner='HPUX Support')"
  if citype!="VirtualMachine":
    json_data = {
                  'operation': 'core/get',
                  'class': citype,
                  "key": "SELECT "+citype+" WHERE "+osowner+" AND status!='decommissioned'",
                  'output_fields': 'name, canonicalos,  finalclass, fqdn, osowner, aka',
    }
  else:
    json_data = {
                  'operation': 'core/get',
                  'class': citype,
                  "key": "SELECT "+citype+" WHERE "+osowner+" AND status!='decommissioned'",
                  'output_fields': 'name, canonicalos,  finalclass, fqdn, osowner, aka, buildtype',
    }
  encoded_data = json.dumps(json_data)
  r = requests.post(ITOP_URL+'/webservices/rest.php?version=1.0', verify=False, data={'auth_user': ITOP_USER, 'auth_pwd': ITOP_PWD, 'json_data': encoded_data})
  result = json.loads(r.text);
  if result['code'] != 0:
    print(result['message']+"\n")
  if result["message"]!='Found: 0':
    return result["objects"]
  return []
def allOurServers():
  allservers={}
  allservers.update(getFromITOP("VirtualMachine"))
  allservers.update(getFromITOP("Server"))
  #hypervisor contains redundant entries for solaris

  try:
    allservers.update(getFromITOP("Hypervisor"))
  except:
    pass
  return allservers
mymeta={}
serversan={"linuxservers":{"hosts":[]},"solarisservers":{"hosts":[]},"hpuxservers":{"hosts":[]},"_meta":mymeta}
ourservers=allOurServers()
for server in ourservers:
  if ourservers[server]["fields"]["osowner"]=="GCD Linux":
    if len(ourservers[server]["fields"]["fqdn"])>2:
      serversan["linuxservers"]["hosts"].append(ourservers[server]["fields"]["fqdn"])
    else:
      serversan["linuxservers"]["hosts"].append(ourservers[server]["fields"]["name"])
  if ourservers[server]["fields"]["osowner"]=="Stores UNIX":
    if len(ourservers[server]["fields"]["fqdn"])>2:
      serversan["solarisservers"]["hosts"].append(ourservers[server]["fields"]["fqdn"])
    else:
      serversan["solarisservers"]["hosts"].append(ourservers[server]["fields"]["name"])
  if ourservers[server]["fields"]["osowner"]=="HPUX Support":
    if len(ourservers[server]["fields"]["fqdn"])>2:
      serversan["hpuxservers"]["hosts"].append(ourservers[server]["fields"]["fqdn"])
    else:
      serversan["hpuxservers"]["hosts"].append(ourservers[server]["fields"]["name"])
#print(json.dumps(serversan))
print("[linuxservers]")
for server in serversan["linuxservers"]["hosts"]:
  print(server)

print("\n[solarisservers]")
for server in serversan["solarisservers"]["hosts"]:
  print(server)

print("\n[hpuxservers]")
for server in serversan["hpuxservers"]["hosts"]:
  print(server)

