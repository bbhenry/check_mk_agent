#!/bin/bash

# Connection to Asterisk
connection=`/usr/sbin/asterisk -rx 'core show calls'`
if [ $? -ne 0 ]; then
        connection_status=2
        connection_result="Critical: Asterisk not responding!"
        echo "$connection_status Call_Count - $connection_result"
        exit 1
fi

# Check existing number of calls
number=`echo $connection|grep --color=never active|awk '{print $1}'|sed -r "s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]//g"`
call_count_status=0

# Build a message up
echo "$call_count_status Call_Count count=$number;;;; $number live calls"

exit 0
