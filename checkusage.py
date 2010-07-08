#!/usr/bin/env python
from __future__ import division
from __future__ import print_function

import time
import calendar
import re

import urllib
import urllib2
from cookielib import CookieJar

# You need to set the folloing values values
username = "yourusername"
password = "yourpassword"

# In MB (1G = 1000.0), sample values are for the "ADSL2+ Super Fast / 500GB" one
max_onpeak = 150000.0 
max_offpeak = 350000.0

# What the final day of the month for your plan
rollover_day = 17

# [TODO]: Username/Password should probably be stored in a seperate config file to ensure
# people passing the file around don't pass their password too, maybe some basic
# encryption (rot13?).

# ['TODO'] Extract rollover from the usage page. This might be the day befoure
# the date listed on the usage page as 'Expiry Date'.

# [TODO]: Maybe work out peak quotas from the plan information on the page
# (although there are people still on older plans that don't list the data on
# the website so I don't have data, but in those cases people should be
# encouraged to change to a newer plan since they are generally cheaper or offer
# more data, otherise manual override).

def getCurrentUsage():
    url = "https://cyberstore.tpg.com.au/your_account/index.php?function=checkaccountusage"

    data = {}
    values = {'check_username': username, 'password': password}

    data = urllib.urlencode(values)
    request = urllib2.Request(url, data)

    try:
        response = urllib2.urlopen(request)
    except:
        print("ERROR: Could not retrieve TPG website...");
        raise

    cookies = CookieJar()
    cookies.extract_cookies(response, request)
    cookie_handler = urllib2.HTTPCookieProcessor(cookies)
    redirect_handler = urllib2.HTTPRedirectHandler()
    opener = urllib2.build_opener(redirect_handler,cookie_handler)

    try:
        response = opener.open(request)
    except:
        print("ERROR: Could not retrieve account usage website...");
        raise

    the_page = response.read()


    # For accounts that count upload and download
    found = re.search('(<BR>Peak\ Downloads\ used:\ )(.+)( MBPeak\ Uploads\ used:\ )(.+)( MBPeak Total used: )(.+)( MB<br>Off-Peak Downloads used: )(.+)( MB<br>Off-Peak Uploads used: )(.+)( MBOff-Peak Total used: )(.+)( MB</td>)', the_page)
    if found:
        onpeak_downloads_used = found.group(2)
        onpeak_uploads_used = found.group(4)
        onpeak_used = found.group(6)
        offpeak_downloads_used = found.group(8)
        offpeak_uploads_used = found.group(10)
        offpeak_used = found.group(12)
        return float(onpeak_used), float(offpeak_used)

    # For accounts that only count download
    found = re.search('(<BR>Peak\ Downloads\ used:\ )(.+)( MB<br>Off-Peak Downloads used: )(.+)( MB</td>)', the_page)
    if found:
        onpeak_used = found.group(2)
        offpeak_used = found.group(4)
        return float(onpeak_used), float(offpeak_used)

    print("ERROR: Could not find quota information in returned site. Check login details.");
    #print(the_page)
    raise

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
    
    try:
        onpeak_used, offpeak_used = getCurrentUsage()
    except:
        print("Could not get usage data...")
        return

    print("Peak: %1f / %f, (%f MB)" % (onpeak_used, max_onpeak, target_onpeak))
    print("Offpeak: %f / %f, (%f MB)" % (offpeak_used, max_offpeak, target_offpeak))
    print("Days untill rollover:", days_until_rollover, ", Days since rollover:", days_since_rollover)

if __name__ == '__main__':
    printUsage()
