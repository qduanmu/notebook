#!/usr/bin/python

unique_pkgs = []
with open('/tmp/rhv4-1-white', 'r') as sf:
    p_str = sf.read()
    packages = p_str.split(',')
    print len(packages)

for p in packages:
    p=p.strip('\n')
    if p not in unique_pkgs:
        unique_pkgs.append(p)

print len(unique_pkgs)
print unique_pkgs
print ",".join(unique_pkgs)
