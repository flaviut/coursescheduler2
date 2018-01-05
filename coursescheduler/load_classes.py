import sys
from datetime import datetime
from time import strptime, mktime
from typing import Tuple, List

from lxml import html
from lxml.html import HtmlElement

from coursescheduler.common import CourseOffering

"""
Importing a new set of classes:

1. Navigate to GoSOLAR (actually Ellucian Banner, but every college insists on
   giving their instance a stupid name). You get to this by going through the
   steps to register for classes.
2. Click on the "Registration" tab -> "Look-Up Classes to Add" -> Current
   Semester -> "Submit"
3. Select your degree level
4. Click on the first thing under "Subject". Scroll to the bottom and
   shift-click the bottom item,
5. Click "Section Search".
6. This will take a while to load since Banner is a piece of shit (and also the
   page is about 10MB).
"""

LETTER_TO_DAY = {
    'M': datetime(2018, 1, 1),
    'T': datetime(2018, 1, 2),
    'W': datetime(2018, 1, 3),
    'R': datetime(2018, 1, 4),
    'F': datetime(2018, 1, 5),
    'S': datetime(2018, 1, 6),
}


def day_string_to_date_list(date_string: str) -> List[datetime]:
    """converts from a date short code to a list of datetimes.
     Valid dates are M, MF, MW, MWF, R, S, T, TR, TRF, W, WF, TBA"""
    if date_string == 'TBA':
        return []

    return [LETTER_TO_DAY[letter] for letter in date_string]


def parse_simple_time(time: str) -> datetime:
    return datetime.fromtimestamp(mktime(strptime(time, '%I:%M %p')))


def date_time_strings_to_schedule(
        date: str, time: str
) -> List[Tuple[datetime, datetime]]:
    if date == 'TBA' or time == 'TBA':
        return []
    start_str, end_str = time.split('-')
    start = parse_simple_time(start_str)
    end = parse_simple_time(end_str)

    days = day_string_to_date_list(date)

    result = []
    for day in days:
        result.append((
            day.replace(hour=start.hour, minute=start.minute),
            day.replace(hour=end.hour, minute=end.minute)
        ))
    return result


def parse_file(filename: str):
    document = html.parse(filename)
    rows = document.xpath(
        '//table[@class="datadisplaytable"]/tbody/tr[td[@class="dddefault"]]')
    course_list = []
    for row in rows:
        assert isinstance(row, HtmlElement)

        if row[2].text_content().strip() == '':
            course_list[-1].times.extend(
                date_time_strings_to_schedule(row[9].text_content(),
                                              row[10].text_content()))
            continue

        course_list.append(CourseOffering(
            closed=row[0].text_content() == 'Closed',
            crn=int(row[2].text_content().strip()),
            course=(row[3].text_content().strip() + ' ' +
                    row[4].text_content().strip()),
            campus=row[6].text_content(),
            title=row[8].text_content(),
            capacity=int(row[11].text_content().strip()),
            remaining_capacity=int(row[13].text_content().strip()),
            xlist_capacity=int(row[14].text_content().strip()),
            xlist_remaining_capacity=int(row[16].text_content().strip()),
            comments=row[17].text_content().strip(),
            instructor=row[18].text_content().replace('(P)', '').strip(),
            location=row[20].text_content().strip(),
            times=date_time_strings_to_schedule(row[9].text_content(),
                                                row[10].text_content()),
        ))
    return course_list


if __name__ == '__main__':
    courses = parse_file(sys.argv[1])
    for c in courses:
        print(c)
