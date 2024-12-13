#!/usr/bin/env python
import psycopg2

conn = psycopg2.connect("dbname=public user=qduanmu password='tpr6Dp(T9' host=virtualdb.engineering.redhat.com port=5432")
# Teiid does not support setting this value at all and unless we
# specify ISOLATION_LEVEL_AUTOCOMMIT (zero), psycopg2 will send a
# SET command the teiid server doesn't understand.
#conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
conn.set_isolation_level(0)
   
cursor = conn.cursor()
   
#query = '''select bugs.priority, bugs.bug_severity, count(bugs.bug_id)
#      from Bugzilla.bugs bugs, Bugzilla.products products
#     where bugs.product_id = products.id
#       and products.name like 'Red Hat Enterprise Linux %'
#       and bugs.bug_status != 'CLOSED'
#  group by bugs.priority, bugs.bug_severity'''
query = '''select * from COMPONENT''' 
   
cursor.execute(query)
rows = cursor.fetchall()
cols = [t[0] for t in cursor.description]
for row in rows:
 print ", ".join(["%s = %s" % (col, value) for col, value in zip(cols, row)])
   
conn.close()

# PELC BUG URL: https://projects.engineering.redhat.com/secure/CreateIssueDetails!init.jspa?pid=10700&issuetype=1&priority=3
