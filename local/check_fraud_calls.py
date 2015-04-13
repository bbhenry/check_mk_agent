#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import re
import sys
import datetime
import time

## Define thresholds
national_accum_cost_day_crit = 22
national_count_day_crit = 600
national_accum_cost_night_crit = 7
national_count_night_crit = 100
national_start = datetime.time(19, 0, 0)
national_end = datetime.time(5, 30, 0)

npa_accum_cost_day_crit = 8
npa_count_day_crit = 12
npa_accum_cost_night_crit = 5
npa_count_night_crit = 8
npa_start = datetime.time(20, 0, 0)
npa_end = datetime.time(5, 30, 0)

international_accum_cost_day_crit = 15
international_count_day_crit = 17
international_accum_cost_night_crit = 6
international_count_night_crit = 7
international_start = datetime.time(17, 0, 0)
international_end = datetime.time(5, 30, 0)

## Initialize values
epoch_now = int(time.time())
current_time = datetime.datetime.now().time()
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

## Define connection to Freeswitch database
con_fs = mdb.connect('freeswitch.db.host', 'db_user', 'db_password', 'freeswitch');

with con_fs:

## Get outbound call records from freeswitch database
    cur_fs = con_fs.cursor(mdb.cursors.DictCursor)
    cur_fs.execute("SELECT * FROM detailed_calls where b_callstate='ACTIVE' and application_data like '%lcr%'")
    rows = cur_fs.fetchall()

## Function to calculate call cost
def cost(now, start, rate):
        return (now - start) * rate / 60

## Function to compare time range of day
def time_range(start, end, now):
    """Return true if 'now' is in the range [start, end]"""
    if start <= end:
        return start <= now <= end
    else:
        return start <= now or now <= end

## Identify call type and get lcr rate to calculate cost
for row in rows:
#        print row["dest"], row["application_data"], row["call_created_epoch"]
	rate = re.search('(?<=lcr_rate=)\d+.\d+(?=,)', row["application_data"])
	current_rate = float(rate.group(0))
#	rate_all = max(re.findall('(?<=lcr_rate=)\d+.\d+(?=,)', row["application_data"]))
#	lcr_digits = re.search('(?<=lcr_digits=)\d+', row["application_data"])
	lcr_digits_all = max(re.findall('(?<=lcr_digits=)\d+', row["application_data"]))
#	print row["application_data"]
#	print lcr_digits_all
#	print rate.group(0)
#	print "================="
	start_time = row["call_created_epoch"]
	national_calls = re.match('1\d+|1', lcr_digits_all)
	npa_calls = ""
	if national_calls:
		npa_calls = re.match('1(242|246|264|268|284|340|345|441|473|649|664|670|671|684|721|758|767|784|787|809|829|849|868|869|876|939)', lcr_digits_all)
#	national_calls = re.match('\+?1\d{10}|\d{10}|\d{7}|\d{3}-\d{3}-\d{4}|cor.*\d{10}', row["dest"])
	else:
		international_calls = re.match('[2-9]\d+', lcr_digits_all)

## Calculate call cost and accumulate to total cost
	accum_call_cost = cost(epoch_now, start_time, current_rate)
	total_accum_cost += accum_call_cost
	total_current_cost += current_rate

	if npa_calls:
		npa_count += 1
		npa_accum_cost += accum_call_cost
		npa_current_cost += current_rate
		continue
	if national_calls:
		national_count += 1
		national_accum_cost += accum_call_cost
		national_current_cost += current_rate
		continue
	if international_calls:
		international_count += 1
		international_accum_cost += accum_call_cost
		international_current_cost += current_rate
		continue

	with open('unknown-pattern.txt', 'a') as f:
		f.write("%s \n" % row["application_data"])
	f.closed

## Determine threshold
if time_range(national_start, national_end, current_time):
        national_accum_cost_crit = national_accum_cost_night_crit
        national_count_crit = national_count_night_crit
else:
        national_accum_cost_crit = national_accum_cost_day_crit
        national_count_crit = national_count_day_crit

if time_range(npa_start, npa_end, current_time):
	npa_accum_cost_crit = npa_accum_cost_night_crit
	npa_count_crit = npa_count_night_crit
else:
	npa_accum_cost_crit = npa_accum_cost_day_crit
	npa_count_crit = npa_count_day_crit

if time_range(international_start, international_end, current_time):
        international_accum_cost_crit = international_accum_cost_night_crit
        international_count_crit = international_count_night_crit
else:
        international_accum_cost_crit = international_accum_cost_day_crit
        international_count_crit = international_count_day_crit


## Reports
### Total report
print "0 Fraud_Detect_Total_Cost total_accum_oubound_cost=%.6f|total_current_cost=%.6f Total accumulated live outbound call costing Phone.com $%.6f so far" % (total_accum_cost, total_current_cost, total_accum_cost)

### National report
if national_accum_cost < national_accum_cost_crit and national_count < national_count_crit:
	print "0 Fraud_Detect_National national_accum_cost=%.6f;;%d|national_count=%d;;%d|national_current_cost=%.6f %d accumulated live US national calls costing Phone.com $%.6f so far" % (national_accum_cost, national_accum_cost_crit, national_count, national_count_crit, national_current_cost, national_count, national_accum_cost)
else:
	print "2 Fraud_Detect_National national_accum_cost=%.6f;;%d|national_count=%d;;%d|national_current_cost=%.6f %d accumulated live US national calls costing Phone.com $%.6f already, please check for fraud activity" % (national_accum_cost, national_accum_cost_crit, national_count, national_count_crit, national_current_cost, national_count, national_accum_cost)

### NPA report
if npa_accum_cost < npa_accum_cost_crit and npa_count < npa_count_crit:
	print "0 Fraud_Detect_NPA npa_accum_cost=%.6f;;%d|npa_count=%d;;%d|npa_current_cost=%.6f %d accumulated live NPA calls costing Phone.com $%.6f so far" % (npa_accum_cost, npa_accum_cost_crit, npa_count, npa_count_crit, npa_current_cost, npa_count, npa_accum_cost)
else:
	print "2 Fraud_Detect_NPA npa_accum_cost=%.6f;;%d|npa_count=%d;;%d|npa_current_cost=%.6f %d accumulated live NPA calls costing Phone.com $%.6f already, please check for fraud activity" % (npa_accum_cost, npa_accum_cost_crit, npa_count, npa_count_crit, npa_current_cost, npa_count, npa_accum_cost)

### International report
if international_accum_cost < international_accum_cost_crit and international_count < international_count_crit:
	print "0 Fraud_Detect_International international_accum_cost=%.6f;;%d|international_count=%d;;%d|international_current_cost=%.6f %d accumulated live international calls costing Phone.com $%.6f so far" % (international_accum_cost, international_accum_cost_crit, international_count, international_count_crit, international_current_cost, international_count, international_accum_cost)
else:
	print "2 Fraud_Detect_International international_accum_cost=%.6f;;%d|international_count=%d;;%d|international_current_cost=%.6f %d accumulated live international calls costing Phone.com $%.6f already, please check for fraud activity" % (international_accum_cost, international_accum_cost_crit, international_count, international_count_crit, international_current_cost, international_count, international_accum_cost)
