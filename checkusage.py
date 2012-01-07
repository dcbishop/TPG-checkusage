#!/usr/bin/env python

# TPG Usage Checker - Retrieves the data quota usage from the TPG website.
#
# Written in 2010 by David C. Bishop <david@davidbishop.org>
#
# To the extent possible under law, the author(s) have dedicated all copyright
# and related and neighboring rights to this software to the public domain
# worldwide. This software is distributed without any warranty.
#
# You should have received a copy of the CC0 Public Domain Dedication along with
# this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

from __future__ import division
from __future__ import print_function

import time
import calendar
import re
import urllib
import urllib2
from cookielib import CookieJar
import pickle
import os

# [TODO]: Stored Username/Password could do with some simple encryption.

# [TODO] Extract rollover from the usage page. This might be the day befoure
# the date listed on the usage page as 'Expiry Date'.

# [TODO]: Maybe work out peak quotas from the plan information on the page
# (although there are people still on older plans that don't list the data on
# the website so I don't have data, but in those cases people should be
# encouraged to change to a newer plan since they are generally cheaper or offer
# more data, otherise manual override).

homedir = os.path.expanduser('~')
config_filename = homedir + '/.config/tpg-usage.cfg'

def getCurrentUsage(username, password):
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

def getCurrentTarget(settings):
    now = time.localtime()
    year = now[0]
    month = now[1]
    day = now[2]

    days_in_month = calendar.monthrange(year, month)[1] 

    days_until_rollover = settings['rollover_day']-day
    days_since_rollover = days_in_month-days_until_rollover

    if days_until_rollover < 0:
        days_since_rollover = day-settings['rollover_day']
        days_until_rollover = days_in_month - days_since_rollover

    target_onpeak = (float(settings['max_onpeak']) / days_in_month) * days_since_rollover
    target_offpeak = (float(settings['max_offpeak']) / days_in_month) * days_since_rollover

    return target_onpeak, target_offpeak, days_until_rollover, days_since_rollover


def printUsage():
    settings = None
    try:    
        f = open(config_filename, 'rb')
        settings = pickle.load(f)
    except:
        print("Could not load settings '" + config_filename + "'")

    if not settings:
        print("Configuration:")
        username = raw_input("Enter your username: ")
        password = raw_input("Enter your password: ")
        print("Quotas are entered in MB, ie 150GB = 150000.")
        max_onpeak = float(raw_input("Enter your maximum onpeak quota: "))
        max_offpeak = float(raw_input("Enter your maximum offpeak quota: "))
        rollover_day = int(raw_input("Enter the roll over day (final day of the month for your plan): "))
        settings = {'username':username, 'password':password, 'max_onpeak':max_onpeak, 'max_offpeak':max_offpeak, 'rollover_day':rollover_day}
        print("Saving settings to '" + config_filename + "'");
        output = open(config_filename, 'wb')
        pickle.dump(settings, output)
        output.close()
        os.chmod(config_filename, 0600)
        print("Getting usage...")

    target_onpeak, target_offpeak, days_until_rollover, days_since_rollover = getCurrentTarget(settings)    
    try:
        onpeak_used, offpeak_used = getCurrentUsage(settings['username'], settings['password'])
    except:
        print("Could not get usage data...")
        return

    print("Peak: %1f / %f, (%f MB)" % (onpeak_used, settings['max_onpeak'], target_onpeak))
    print("Offpeak: %f / %f, (%f MB)" % (offpeak_used, settings['max_offpeak'], target_offpeak))
    print("Days untill rollover:", days_until_rollover, ", Days since rollover:", days_since_rollover)

if __name__ == '__main__':
    printUsage()
