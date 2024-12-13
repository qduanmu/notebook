#!/usr/bin/python

import sys
import json
import psycopg2
from psycopg2.extras import RealDictCursor

def usage():
    print "    Usage: python " + sys.argv[0] + " tablename"

def get_dumps():
    conn_params = "host='localhost' dbname='pkgwrangler' user='pkgwrangler' password='pkgwrangler'"
    conn = psycopg2.connect(conn_params)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""SELECT * FROM %s""" % sys.argv[1])
    print json.dumps(cur.fetchall(), indent=2)

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        usage()
        sys.exit()

    get_dumps()
