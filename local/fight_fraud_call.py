#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import re
import sys
import time
from tabulate import tabulate
from collections import Counter

## Define thresholds
npa_count_crit = 15
npa_cost_crit = 10

international_count_crit = 17
international_cost_crit = 15

## Initialize values
epoch_now = int(time.time())
total_accum_cost = 0
total_current_cost = 0
npa_count = 0
npa_accum_cost = 0
npa_current_cost = 0
national_count = 0
national_accum_cost = 0
national_current_cost = 0
international_count = 0
international_accum_cost = 0
international_current_cost =0

## Initialize Collections
national_digits_collection = []
international_digits_collection = []
npa_digits_collection = []

## Define connection to Freeswitch database
con_fs = mdb.connect('freeswitch.db.host', 'db_user', 'db_password', 'freeswitch')

with con_fs:

## Get outbound call records from freeswitch database
    cur_fs = con_fs.cursor(mdb.cursors.DictCursor)
    cur_fs.execute("SELECT * FROM detailed_calls where b_callstate='ACTIVE' and application_data like '%lcr%'")
    rows = cur_fs.fetchall()

## Function to calculate call cost
def cost(now, start, rate):
        return (now - start) * rate / 60


## Identify call type and get lcr rate to calculate cost
for row in rows:
#	print row["uuid"], row["name"], row["application_data"], row["context"], row["b_cid_num"]

	### Get LCR rate for the call
	rate = re.search('(?<=lcr_rate=)\d+.\d+(?=,)', row["application_data"])
	current_rate = float(rate.group(0))

	### Get voip id
	voip_id = re.search('(?<=voip_id=\')\d+', row["application_data"])

	### Get LCR dial prefix
	lcr_digits = max(re.findall('(?<=lcr_digits=)\d+', row["application_data"]))

	### Combine LCR prefix with voip_id for further processing
	if voip_id:
		lcr_id = str(lcr_digits) + '-v' + str(voip_id.group(0))
	else:
		lcr_id = str(lcr_digits)

	### Get start time of the call
	start_time = row["call_created_epoch"]

	### Classify type of calls
	national_calls = re.match('1\d+|1', lcr_digits)
	npa_calls = ""

	if national_calls:
		npa_calls = re.match('1(242|246|264|268|284|340|345|441|473|649|664|670|671|684|721|758|767|784|787|809|829|849|868|869|876|939)', lcr_digits)
	else:
		international_calls = re.match('[2-9]\d+', lcr_digits)


	### Calculate call cost and accumulate to total cost
	accum_call_cost = cost(epoch_now, start_time, current_rate)
	if npa_calls:
		npa_count += 1
		npa_accum_cost += accum_call_cost
		npa_digits_collection.append(lcr_id)
		continue
	if national_calls:
		national_count += 1
		national_accum_cost += accum_call_cost
		national_digits_collection.append(lcr_id)
		continue
	if international_calls:
		international_count += 1
		international_accum_cost += accum_call_cost
		international_digits_collection.append(lcr_id)
		continue



#print Counter(lcr_digits_collection).most_common(15)[:-1]
print "You can use the call kill script on any of the above offending numbers to kill those fraud calls"
print "\n"

print tabulate(Counter(international_digits_collection).most_common(), headers=["International Prefix - voip_id", "Occurrence"])
print "\n"

print tabulate(Counter(national_digits_collection).most_common(15), headers=["National Prefix - voip_id", "Occurrence (Top 15)"])
print "\n"

print tabulate(Counter(npa_digits_collection).most_common(), headers=["NPA Prefix - voip_id", "Occurrence"])
print "\n"
