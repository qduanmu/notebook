#!/usr/bin/python

import json
from kobo.shortcuts import run
import subprocess

ct = "Content-Type: application/json"
auth_token = "Authorization: Token 5f4a5b5a594a315ea00b70d2d21343435b88f3f2"
# # Step 1: get all asdas's failed imports in openshift-4.14
# # output: failed_id_params
# get_url ="https://pelc.engineering.redhat.com/rest/v1/tasks/?owner__username=asdas&status=FAILURE&params=openshift-4.14"  
# all_urls = []
# while get_url != 'null':
#     all_urls.append(get_url)
#     cmd = f"curl --silent -k -H '{ct}' -H '{auth_token}' -X GET '{get_url}' |jq -r '.next'"
#     # print(cmd)
#     ret, output = run(cmd)
#     get_url = output.decode('utf-8').rstrip('\n').replace('http', 'https')
# 
# # print(all_urls)
# for url in all_urls:
#     # cmd = f"curl --silent -k -H '{ct}' -H '{auth_token}' -X GET '{url}' |jq -r '.results[] | .id'"
#     cmd = f"curl --silent -k -H '{ct}' -H '{auth_token}' -X GET '{url}' |jq -r '.results[] | [.id, .params]'"
#     proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
#                             stderr=subprocess.PIPE)
#     output, error = proc.communicate()
#     print(output.decode('utf-8'))

# # Step 2: get all asdas's duplicate imports in openshift-4.14
# # output: duplicate_id_params 
# get_url ="https://pelc.engineering.redhat.com/rest/v1/tasks/?owner__username=asdas&status=DUPLICATE&params=openshift-4.14"  
# all_urls = []
# while get_url != 'null':
#     all_urls.append(get_url)
#     cmd = f"curl --silent -k -H '{ct}' -H '{auth_token}' -X GET '{get_url}' |jq -r '.next'"
#     # print(cmd)
#     ret, output = run(cmd)
#     get_url = output.decode('utf-8').rstrip('\n').replace('http', 'https')
# 
# # print(all_urls)
# for url in all_urls:
#     # cmd = f"curl --silent -k -H '{ct}' -H '{auth_token}' -X GET '{url}' |jq -r '.results[] | .id'"
#     cmd = f"curl --silent -k -H '{ct}' -H '{auth_token}' -X GET '{url}' |jq -r '.results[] | [.id, .params]'"
#     proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
#                             stderr=subprocess.PIPE)
#     output, error = proc.communicate()
#     print(output.decode('utf-8'))

# # Step 3: get all asdas's success imports in openshift-4.14

# Step 4: generate noneedretry_nvrs(NOTE: via package NVR)
# The data is from grepping package_nvr from duplicate_id_params
# and add success nvrs via vim
# output: noneedretry_nvrs
noneedretry_nvrs = []
with open('/tmp/noneedretry_nvrs', 'r') as sf:
    lines = sf.read()
    for line in filter(None, lines.split('\n')):
        noneedretry_nvrs.append(line)
# print(len(noneedretry_nvrs))

# Step 5: get the task id of retry tasks(failed with no duplicate/success)
# remove noneedretry_nvrs related item from failed_id_params
import re
retry_ids = []
with open('/tmp/failed_id_params', 'r') as sf:
    lines = sf.read()
    for line in filter(None, lines.split('\n')):
        if line.startswith('[') or line.startswith(']'):
            continue
        if re.match(r'^[ 0-9]+,$', line):
            retry_ids.append(line.replace(',', '').strip())
            continue
        for nvr in noneedretry_nvrs:
            if nvr in line:
                retry_ids.pop()
print(len(retry_ids))
# print(retry_ids)

# Step 6: retry the tasks in retry_ids
for tid in retry_ids:
    print(tid)
    retry_url = f"https://pelc.engineering.redhat.com/rest/v1/tasks/{tid}/retry/" 
    cmd = f"curl --silent -H '{ct}' -H '{auth_token}' -X POST '{retry_url}'"
    ret, output = run(cmd)
    print(output)

