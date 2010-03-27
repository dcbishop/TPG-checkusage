#!/usr/bin/env python

from __future__ import division
from __future__ import print_function

import time
import calendar
import re

import urllib
import urllib2
from cookielib import CookieJar

username = "yourusername"
password = "yourpassword"

max_onpeak = 80000.0
max_offpeak = 80000.0
rollover_day = 12

def getCurrentUsage():


    url = "https://cyberstore.tpg.com.au/your_account/index.php?function=checkaccountusage"

    data = {}
    values = {'check_username': username, 'password': password}

    data = urllib.urlencode(values)
    request = urllib2.Request(url, data)
    response = urllib2.urlopen(request)

    cookies = CookieJar()
    cookies.extract_cookies(response, request)
    cookie_handler = urllib2.HTTPCookieProcessor(cookies)
    redirect_handler = urllib2.HTTPRedirectHandler()
    opener = urllib2.build_opener(redirect_handler,cookie_handler)
    response = opener.open(request)

    the_page = response.read()

    found = re.search('(<BR>Peak\ Downloads\ used:\ )(.+)( MB<br>Off-Peak Downloads used: )(.+)( MB</td>)', the_page)

    if not found:
        print("ERROR: Could not find quota information.");

    #print(the_page)
    onpeak_used = found.group(2)
    offpeak_used = found.group(4)

    return float(onpeak_used), float(offpeak_used)

def getCurrentTarget():
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

    target_onpeak = (float(max_onpeak) / days_in_month) * days_since_rollover
    target_offpeak = (float(max_offpeak) / days_in_month) * days_since_rollover

    return target_onpeak, target_offpeak, days_until_rollover, days_since_rollover


def printUsage():
    target_onpeak, target_offpeak, days_until_rollover, days_since_rollover = getCurrentTarget()
    onpeak_used, offpeak_used = getCurrentUsage()

    print("Peak: %1f / %f, (%f MB)" % (onpeak_used, max_onpeak, target_onpeak))
    print("Offpeak: %f / %f, (%f MB)" % (offpeak_used, max_offpeak, target_offpeak))
    print("Days untill rollover:", days_until_rollover, ", Days since rollover:", days_since_rollover)

if __name__ == '__main__':
    printUsage()
