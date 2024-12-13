#!/usr/bin/env python

import sys
import re
import MySQLdb

market_skus = []
market_names = []
market_eng_pids = []

init_file = open("content_markets", "r")
markets = init_file.readlines()
init_file.close()
for market in markets:
    paras =market.split(";")
    market_skus.append(paras[0])
    market_names.append(paras[1])
    market_eng_pids.append(paras[2])

try:
    conn = MySQLdb.connect(host='localhost',user='qduanmu',passwd='redhat',db='content')
except Exception, e:
    print e
    sys.exit()
cursor = conn.cursor()

sql = "insert into projects(name, version) values('RHEL', '6.2')"
cursor.execute(sql)

for index in range(len(market_skus)):
    sql = "insert into market_products(sku, name) values('%s', '%s')" % (market_skus[index], market_names[index])
    try:
        cursor.execute(sql)
    except Exception, e:
        print e
    
    sql = "select id from market_products where sku='%s'" % market_skus[index]
    cursor.execute(sql)
    item = cursor.fetchone()
    #recs = cursor.fetchall()
    pid_list = market_eng_pids[index].split(",")
    if (len(pid_list) > 0):
	for pid in pid_list:
	    if re.match(r"(\d+)", pid):
	        sql = "insert into market_products_eng_products_map(market_pid, eng_pid) values(%d, %d)" % (item[0], int(pid))
	    #else: 
		#sql = "insert into market_products_eng_products_map(market_pid, eng_pid) values(%d, %d)" % (item[0], 0)
	    try:
	        cursor.execute(sql)
            except Exception, e:
	        print e

cursor.close()
conn.commit()
conn.close()
