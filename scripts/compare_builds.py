#!/usr/bin/python

err_file_2 = None
# RHEL
# dep_file = '/home/qduanmu/backup/openlcs/manifest/compare/rhel-8.6.0.z_nvrs'
# err_file = '/home/qduanmu/backup/openlcs/manifest/compare/rhel8.6_released_nvrs'

# OCP
# dep_file = '/home/qduanmu/backup/openlcs/manifest/compare/openshift-4.10.z_nvrs'
# err_file = '/home/qduanmu/backup/openlcs/manifest/compare/ocp-4.10-rhel8_released_nvrs'
# err_file_2 = '/home/qduanmu/backup/openlcs/manifest/compare/ocp-4.10-rhel7_released_nvrs'

# ACM 2.5
# dep_file = '/home/qduanmu/backup/openlcs/manifest/compare/rhacm-2.5_nvrs'
# err_file = '/home/qduanmu/backup/openlcs/manifest/compare/acm-2.5-rhel8_released_nvrs'

# ACM 2.4
# dep_file = '/home/qduanmu/backup/openlcs/manifest/compare/rhacm-2.4_nvrs'
# err_file = '/home/qduanmu/backup/openlcs/manifest/compare/acm-2.4-rhel8_released_nvrs'

# Ansible 2.2
# dep_file = '/home/qduanmu/backup/openlcs/manifest/compare/ansible_automation_platform-2.2_nvrs'
# err_file = '/home/qduanmu/backup/openlcs/manifest/compare/ansible-2.2-rhel9_released_nvrs'
## err_file_2 = '/home/qduanmu/backup/openlcs/manifest/compare/ansible-2.2-rhel8_released_nvrs'

# Ansible 2.1
dep_file = '/home/qduanmu/backup/openlcs/manifest/compare/ansible_automation_platform-2.1_nvrs'
err_file = '/home/qduanmu/backup/openlcs/manifest/compare/ansible-2.1-rhel8_released_nvrs'

dep_nvrs = []
err_nvrs = []
with open(dep_file, 'r') as sf:
    nvr_str = sf.read()
    dep_nvrs= list(filter(None, nvr_str.split('\n')))
print("Tocal deptopia nvrs: %s" % str(len(dep_nvrs)))

with open(err_file, 'r') as sf:
    nvr_str = sf.read()
    err_nvrs= list(filter(None, nvr_str.split('\n')))

if err_file_2:
    with open(err_file_2, 'r') as sf:
        nvr_str_2 = sf.read()
        err_nvrs_2= list(filter(None, nvr_str_2.split('\n')))
        err_nvrs += err_nvrs_2
print("Tocal errata nvrs: %s\n" % str(len(err_nvrs)))

dep_only = list(set(dep_nvrs) - set(err_nvrs))
err_only = list(set(err_nvrs) - set(dep_nvrs))
print("Only deptopia nvrs: %s" % str(len(dep_only)))
print('\n'.join(dep_only))
print("\nOnly errata nvrs: %s" % str(len(err_only)))
print('\n'.join(err_only))
