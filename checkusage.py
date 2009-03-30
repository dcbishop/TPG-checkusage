#!/usr/bin/env python

import time
import calendar

onpeak = 60
offpeak = 140
rollover_day = 19

now = time.localtime()
year = now[0]
month = now[1]
day = now[2]

days_in_month = calendar.monthrange(year, month)[1] 

days_until_rollover = rollover_day-day
days_since_rollover = days_in_month-days_until_rollover

if days_until_rollover < 0:
	days_since_rollover = day-rollover_day
	days_until_rollover = days_in_month - days_since_rollover

print "Onpeak:",(float(onpeak) / days_in_month) * days_since_rollover
print "Offpeak:",(float(offpeak) / days_in_month) * days_since_rollover
print "Days untill rollover:",days_until_rollover, ", Days since rollover:", days_since_rollover, ", Days in month:", days_in_month
