#!/usr/bin/python
#
# Don't forget to get your kerberos all setup (and run kinit first)
# also you'll want to install python2-simplejson and python2-requests-kerberos

import requests
from requests_kerberos import HTTPKerberosAuth
import operator
import sys

my_managers = ['aruizrui', 'cschalle', 'hhorak', 'jberan', 'jzeleny', 'jligon', 'petersen', 'jperrin', 'jeischma', 'jorton', 'kem', 'lnykryn', 'mclasen', 'msuchy', 'ovasik', 'pfrields', 'pthomas', 'sbueno', 'thozza', 'vondruch']

kerberosid = ""
args = len(sys.argv)
if args == 1:
    kerberosid = ""
elif args == 2:
    kerberosid = sys.argv[1]

total_count = 0
total_new_count = 0
total_inprogress_count = 0
total_done_count = 0
total_abandoned_count = 0
kerb_is_manager = False
manager_stats = {}
engineer_stats = {}

def dump_stats(total, new, inprogress, done, abandoned, manager="", indent=5):
    indent_str = " " * indent
    if indent == 0:
        indent2_str = " " * 5
    else:
        indent2_str = indent_str * 2

    if total != 0:
        done_pct = float(done)/float(total) * 100
        inprogress_pct = float(inprogress)/float(total) * 100
        new_pct = float(new)/float(total) * 100
        abandoned_pct = float(abandoned)/float(total) * 100
    else:
        done_pct = 0
        inprogress_pct = 0
        new_pct = 0
        abandoned_pct = 0
    
    print("{}Total {}: {} of which:\n{}Done: {} ({}%)\n{}In progress: {} ({}%)\n{}New: {} ({}%)\n{}Abandoned: {} ({}%)".format(indent_str, manager, total, indent2_str, done, int(done_pct), indent2_str, inprogress, int(inprogress_pct), indent2_str, new, int(new_pct), indent2_str, abandoned, int(abandoned_pct)))

print("\nNote:\n\nThis report only includes data from the latest review that was")
print("generated for each package. Past reviews are not reflected in")
print("the statistics below, no matter what state the past review is in")
print("(New, In-Progress, Done, Abandoned). This removes many duplicates")
print("from the report.")
print("\nIn addition, abandoned reviews are no longer printed individually")
print("(but they are accounted for in the statistics).")
print("\nHopefully, these changes make the report easier to read without")
print("losing any critical data.\n")

if kerberosid != "":
    print("Packages owned by {}:".format(kerberosid))

for manager in my_managers:
    team_count = 0
    done_count = 0
    inprogress_count = 0
    new_count = 0
    abandoned_count = 0
    if kerberosid == manager:
        kerb_is_manager = True

    if kerberosid == "":
        print(manager)
    elif kerberosid == manager:
        print("{} is a manager".format(manager))

    response = requests.get('https://pelc.engineering.redhat.com/reviews/search/json/?draw=1&columns%5B0%5D%5Bdata%5D=review&columns%5B0%5D%5Bname%5D=review&columns%5B0%5D%5Bsearchable%5D=true&columns%5B0%5D%5Borderable%5D=true&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=product_release&columns%5B1%5D%5Bname%5D=product_release&columns%5B1%5D%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=true&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=package_name&columns%5B2%5D%5Bname%5D=package_name&columns%5B2%5D%5Bsearchable%5D=true&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B3%5D%5Bdata%5D=manager&columns%5B3%5D%5Bname%5D=manager&columns%5B3%5D%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=true&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B4%5D%5Bdata%5D=reviewer&columns%5B4%5D%5Bname%5D=reviewer&columns%5B4%5D%5Bsearchable%5D=true&columns%5B4%5D%5Borderable%5D=true&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B5%5D%5Bdata%5D=created_at&columns%5B5%5D%5Bname%5D=created_at&columns%5B5%5D%5Bsearchable%5D=true&columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B6%5D%5Bdata%5D=review_state&columns%5B6%5D%5Bname%5D=review_state&columns%5B6%5D%5Bsearchable%5D=true&columns%5B6%5D%5Borderable%5D=true&columns%5B6%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B6%5D%5Bsearch%5D%5Bregex%5D=false&order%5B0%5D%5Bcolumn%5D=0&order%5B0%5D%5Bdir%5D=asc&start=0&length=5000&search%5Bvalue%5D=&search%5Bregex%5D=false&product_release=623&package_name=&manager=' + manager +'&reviewer=&review_state',
                         auth=HTTPKerberosAuth())
    data = response.json()
    for review in data['data']:
        if not review['reviewer']:
            review['reviewer'] = "NOT_DEFINED"
        if review['reviewer'] not in engineer_stats:
            engineer_stats[review['reviewer']] = { 'New': 0, 'In Progress': 0, 'Done':0, 'Total':0, 'Abandoned':0 }
        if kerberosid == "" or kerberosid == review['reviewer'] or kerberosid == manager:
            if not review['review']['is_latest']:
                continue
            if review['review_state']['name'] != "Abandoned":
                print("     " + review['reviewer'] + " " + review['package_name']['name'] + " " + review['review_state']['name'])
        team_count = team_count + 1
        total_count = total_count + 1
        if review['review_state']['name'] == "Done":
            done_count = done_count + 1
            total_done_count = total_done_count + 1
            engineer_stats[review['reviewer']]['Done'] = engineer_stats[review['reviewer']]['Done'] + 1
            engineer_stats[review['reviewer']]['Total'] = engineer_stats[review['reviewer']]['Total'] + 1
        elif review['review_state']['name'] == "In Progress":
            inprogress_count = inprogress_count + 1
            total_inprogress_count = total_inprogress_count + 1
            engineer_stats[review['reviewer']]['In Progress'] = engineer_stats[review['reviewer']]['In Progress'] + 1
            engineer_stats[review['reviewer']]['Total'] = engineer_stats[review['reviewer']]['Total'] + 1
        elif review['review_state']['name'] == "New":
            new_count = new_count + 1
            total_new_count = total_new_count + 1
            engineer_stats[review['reviewer']]['New'] = engineer_stats[review['reviewer']]['New'] + 1
            engineer_stats[review['reviewer']]['Total'] = engineer_stats[review['reviewer']]['Total'] + 1
        elif review['review_state']['name'] == "Abandoned":
            abandoned_count = abandoned_count + 1
            total_abandoned_count = total_abandoned_count + 1
            engineer_stats[review['reviewer']]['Abandoned'] = engineer_stats[review['reviewer']]['Abandoned'] + 1
            engineer_stats[review['reviewer']]['Total'] = engineer_stats[review['reviewer']]['Total'] + 1
        else:
            print("Unknown review state: ", review['review_state']['name'])
            exit(-1)

    manager_stats[manager] = {'New': new_count, 'In Progress': inprogress_count, 'Done':done_count, 'Abandoned':abandoned_count, 'Total': team_count}
    if kerberosid == "" or kerberosid == manager:
        dump_stats(team_count, new_count, inprogress_count, done_count, abandoned_count, "for " + manager)
    if kerberosid == manager:
        break
    

if kerberosid == "" or not kerb_is_manager:
    print("")
    print("Engineer stats:")

for engineer_key in engineer_stats:
    if kerberosid == "" or kerberosid == engineer_key:
        dump_stats(engineer_stats[engineer_key]['Total'], engineer_stats[engineer_key]['New'], engineer_stats[engineer_key]['In Progress'], engineer_stats[engineer_key]['Done'], engineer_stats[engineer_key]['Abandoned'], "for " + engineer_key)

if kerberosid == "" or kerb_is_manager:
    print("")
    print("Manager stats:")

if kerberosid == "" or kerb_is_manager:
    for manager_key in manager_stats:
        if kerberosid == "" or kerberosid == manager_key:
            dump_stats(manager_stats[manager_key]['Total'], manager_stats[manager_key]['New'], manager_stats[manager_key]['In Progress'], manager_stats[manager_key]['Done'], manager_stats[manager_key]['Abandoned'], "for " + manager_key)

if kerberosid == "":
    print("")
    
if kerberosid == "":
    dump_stats(total_count, total_new_count, total_inprogress_count, total_done_count, total_abandoned_count, "for all managers", 0)

# number of entries to print in lists
n = 10

if kerberosid == "":
    print("")
    print("Top {} engineers by pending reviews:".format(n))

pending_reviews = {}
for engineer_key in engineer_stats:
    pending = engineer_stats[engineer_key]['Total'] - engineer_stats[engineer_key]['Done'] - engineer_stats[engineer_key]['Abandoned']
    pending_reviews[engineer_key] = pending
sorted_pending = sorted(pending_reviews.items(), key=lambda x: x[1], reverse=True)
# sorted_pending = sorted(pending_reviews.items(), key=operator.itemgetter(1))
if kerberosid == "":
    for engineer_tuple in sorted_pending[0:n]:
        print("     {}: {}".format(engineer_tuple[0], engineer_tuple[1]))

if kerberosid == "":
    print("")
    print("Top {} managers by pending reviews:".format(n))

pending_reviews = {}
for manager_key in manager_stats:
    pending = manager_stats[manager_key]['Total'] - manager_stats[manager_key]['Done'] - manager_stats[manager_key]['Abandoned']
    pending_reviews[manager_key] = pending
sorted_pending = sorted(pending_reviews.items(), key=lambda x: x[1], reverse=True)
# sorted_pending = sorted(pending_reviews.items(), key=operator.itemgetter(1))
if kerberosid == "":
    for manager_tuple in sorted_pending[0:n]:
        print("     {}: {}".format(manager_tuple[0], manager_tuple[1]))

print("\nDone")
