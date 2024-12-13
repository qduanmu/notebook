#!/bin/bash

# for ((i=1; i<287; i++))
# do
#   curl -k -H 'Content-Type: application/json' -H 'Authorization: Token b6d785fc25314392156d717b881475ea2fe561a2' -X PATCH https://pelc.stage.engineering.redhat.com/rest/v1/license_variants/$i/ -d '{"approved": true}'
# done

# licenses=(1 2 3)
# for i in ${licenses[*]} 
# do
#   echo $i
#   # curl -H 'Content-Type: application/json' -H 'Authorization: Token 5f4a5b5a594a315ea00b70d2d21343435b88f3f2' -X PATCH https://pelc.engineering.redhat.com/rest/v1/licenses/$i/update_state/ -d '{"state": "Approved"}'
# done

current_date_time=`date +%s`;
rescan_dir='/home/qduanmu/backup/pelc/timeout/rescan_files/files'
result_dir='$rescan_dir/results'
# for entry in `ls $rescan_dir`
# do
#   echo $rescan_dir/$entry
#   start=$current_date_time
#   scancode --license --license-score 20 --only-findings --timeout 1200 --timing --json-pp $result_dir/$entry.result $rescan_dir/$entry 
#   end=$current_date_time
#   echo `expr $end - $start`
# done
scancode --license --license-score 20 --only-findings --timeout 600 --timing --json-pp /tmp/proto.h $rescan_dir/proto.h
