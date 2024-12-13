#!/bin/bash

# for ((i=1; i<287; i++))
# do
#   curl -k -H 'Content-Type: application/json' -H 'Authorization: Token b6d785fc25314392156d717b881475ea2fe561a2' -X PATCH https://pelc.stage.engineering.redhat.com/rest/v1/license_variants/$i/ -d '{"approved": true}'
# done

licenses=(1 2 3)
for i in ${licenses[*]} 
do
  echo $i
  # curl -H 'Content-Type: application/json' -H 'Authorization: Token 5f4a5b5a594a315ea00b70d2d21343435b88f3f2' -X PATCH https://pelc.engineering.redhat.com/rest/v1/licenses/$i/update_state/ -d '{"state": "Approved"}'
done
