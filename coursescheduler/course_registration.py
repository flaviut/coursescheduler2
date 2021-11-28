"""
course_registration.py

Prompts the user for a Middlebury College BannerWeb
ID number and PIN, accesses the Registration section,
and interfaces with it to select the desired term and
submit all desired CRNs at 7AM on the desired date.

Created by Daniel Trauner on 2013-11-09.
Copyright (c) 2013 Daniel Trauner. All rights reserved.
"""
import sys

import os
import time as t
import random
from datetime import datetime

import mechanize as m
from bs4 import BeautifulSoup


# t.sleep = lambda x: 1

# begin helper methods

def term_to_termcode(term):
    """
    Translates a human-readable term i.e. 'Fall 2010'
    into the 'termcode' parameter that the Middlebury
    Course Catalog database URL uses.
    """
    normalized_term = term.strip().lower()
    season, year = normalized_term.split(' ')[0], normalized_term.split(' ')[1]

    if season == 'winter' or season == 'jterm' or season == 'j-term':
        season = '1'
    elif season == 'spring':
        season = '2'
    elif season == 'summer':
        season = '5'
    elif season == 'fall':
        season = '9'
    else:
        season = 'UNKNOWN'
        print('Error in determining the season of the given term!')

    if 'practice' in normalized_term:
        season += '3'
    else:
        season += '0'

    return year + season


def wait_until_7am(date):
    """
    When called, delays the script until 7AM on the
    given date (day of registration) where date is a
    string of the form 'YYYY-MM-DD'.
    """
    # get current time and user's supplied date
    registration = datetime.strptime(date, '%Y-%m-%d') \
        .replace(hour=7, minute=0, second=20)

    while registration > datetime.now():
        t.sleep((registration - datetime.now()).total_seconds())


USERAGENT_HEADER = (
    'User-agent',
    'Mozilla/5.0 (X11; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0')


def check_bw_credentials(user_id, user_pin):
    """
    Checks whether or not the given user_id and
    user_pin are valid credentials for the
    Middlebury College BannerWeb system.
    """
    print('Validating credentials...')
    br = m.Browser()
    br.addheaders = [USERAGENT_HEADER]
    br.open('https://www.gosolar.gsu.edu/bprod/twbkwbis.P_WWWLogin')

    br.select_form('loginform')
    uid = br.form.find_control('sid')
    pin = br.form.find_control('PIN')

    uid.value = user_id
    pin.value = user_pin

    t.sleep(random.gauss(10, 4))
    br.submit()

    return 'P_ValLogin' not in br.geturl()


def register(user_id, user_pin, term_code, crn_list):
    """
    Logs in using the account with id num user_id_num and
    pin user_pin into Middlebury College's Bannerweb,
    navigates to the course registration page for the
    given term_code, and enters and submits the CRNs
    in crn_list.
    """
    print('Opening BannerWeb with a Mechanize browser...')
    br = m.Browser()
    br.addheaders = [USERAGENT_HEADER]
    br.open('https://www.gosolar.gsu.edu/bprod/twbkwbis.P_WWWLogin')

    br.select_form('loginform')
    uid = br.form.find_control('sid')
    pin = br.form.find_control('PIN')

    uid.value = user_id
    pin.value = user_pin

    print('Logging into BannerWeb...')
    t.sleep(random.gauss(10, 4))
    br.submit()

    br.open(br.find_link(text='Registration').url)
    br.open(br.find_link(text='Add/Drop/Withdraw Classes').url)

    br.form = list(br.forms())[1]
    term = br.form.find_control('term_in')
    term.value = [term_code]

    t.sleep(random.gauss(10, 4))
    br.submit()

    print('Entering in CRNs...')
    br.form = list(br.forms())[1]

    crn_fields = []
    for control in br.form.controls:
        if control.name == 'CRN_IN' and control.type == 'text':
            crn_fields.append(control)

    all_crn_fields = crn_fields[1:]

    for i, field in enumerate(all_crn_fields):
        if i < len(crn_list):
            try:
                field.value = str(crn_list[i])
            except AttributeError:
                print('Already registered for ' + str(crn_list[i]) + '!')

    t.sleep(random.gauss(10, 4))
    response = br.submit()

    soup = BeautifulSoup(response.read())

    print('Succeeded in registering for the following courses:')
    print('-' * 51)
    successful_table = soup.findAll(
        'table', {
            'class': 'datadisplaytable',
            'summary': 'Current Schedule'}
    )
    if successful_table:
        successful_courses = successful_table[0].findAll('tr')[1:]
    else:
        successful_courses = []

    successful_crns = set()

    for row in successful_courses:
        contents = [e.text for e in row.findAll('td', {'class': 'dddefault'})]
        print(contents[2] + ' ' + contents[3])
        successful_crns.add(int(contents[2]))

    if soup.findAll('span', {'class': 'errortext'}):
        print('Failed to register for the following courses:')
        print('-' * 45)
        failed_table = soup.findAll(
            'table', {
                'class': 'datadisplaytable',
                'summary': 'This layout table is used to present '
                           'Registration Errors.'}
        )[0]
        failed_courses = failed_table.findAll('tr')[1:]

        for row in failed_courses:
            contents = [e.text for e in
                        row.findAll('td', {'class': 'dddefault'})]
            print(contents[2] + ' ' + contents[3] + ' ' + contents[
                8] + ' ' + '(' + contents[0] + ')')

    return successful_crns


# begin main method

def main(reg_date, term, crns):
    # get user's info from them and login to bannerweb with it
    user_id = os.environ['USER']
    user_pin = os.environ['PASSWORD']

    if not check_bw_credentials(user_id, user_pin):
        print('Invalid BannerWeb ID or password.  Try again.')

    # wait until 7AM on the specified registration day
    wait_until_7am(reg_date)

    # continually try to register until at least one successful attempt has
    # occurred
    registered_courses = set()
    while crns not in registered_courses:
        # submit each crn in crn_list
        try:
            registered_courses = register(user_id, user_pin, term, list(crns))
            timesleep = (60 * 35) + random.gauss(3 * 60, 1 * 60)
            print('sleeping ', timesleep, ' seconds')
            t.sleep(timesleep)  # don't look TOO robotic...
        except Exception as e:
            t.sleep(30)
            print(e)
            print('Trying again')

    print('Done!')


if __name__ == '__main__':
    try:
        main(
            reg_date=sys.argv[1],  # date of registration
            term=sys.argv[2],  # term you're registering for
            crns=set([int(crn) for crn in sys.argv[3:]]),  # list of CRNs to register for
        )
    except IndexError:
        print('{} <registration open date, YYYY-MM-DD> <term, YYYYMM> <CRN>...')
        sys.exit(1)
