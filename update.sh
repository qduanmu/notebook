#!/bin/bash

CT="Content-Type: application/json"
TOKEN="Authorization: Token b6d785fc25314392156d717b881475ea2fe561a2"
DATA='{"approved": true}'
for (( i = 3; i < 5 ; i ++ ))
do
  #curl -k -H '$CT' -H '$TOKEN' -X PATCH https://pelc.stage.engineering.redhat.com/rest/v1/license_variants/$i/ -d '$DATA'
  approve="curl -k -H '$CT' -H '$TOKEN' -X PATCH https://pelc.stage.engineering.redhat.com/rest/v1/license_variants/$i/ -d '$DATA'"
  echo $approve
done
