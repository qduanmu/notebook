#!/usr/bin/python

dep_file = '/tmp/ocp-4.10-rhel8_released_builds_errata_ids'

with open(dep_file, 'r') as sf:
    nvr_str = sf.read()
    dep_nvrs= list(set(list(filter(None, nvr_str.split('\n')))))
    print(dep_nvrs)
