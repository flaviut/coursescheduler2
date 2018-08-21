from datetime import datetime
from itertools import groupby, product
from typing import List, Tuple

from coursescheduler.common import CourseOffering
from coursescheduler.load_classes import parse_file

CourseTimes = List[Tuple[datetime, datetime]]


class TimeSpanSet:
    def __init__(self):
        self._start_time = None
        self._backing_int = 0
        for i in range(1, 6):
            self.add_range(datetime(2018, 1, i, 0, 0),
                           datetime(2018, 1, i, 8, 59))

    def _datetime_to_index(self, time) -> int:
        time_range = (time.replace(second=0, microsecond=0) -
                      self._start_time)
        time_idx = time_range.total_seconds() / 60
        return int(time_idx)

    def add_range(self, start, end) -> bool:
        """Adds the range to the set. If there's an overlap, returns True,
        otherwise False"""
        start = start.replace(second=0, microsecond=0)
        end = end.replace(second=0, microsecond=0)
        assert end > start

        if self._start_time is None:
            self._start_time = start.replace(second=0, microsecond=0)

        if start < self._start_time:
            delta = int((self._start_time - start).total_seconds() / 60)
            self._start_time = start.replace(second=0, microsecond=0)
            self._backing_int = self._backing_int << delta

        start_idx = self._datetime_to_index(start)
        end_idx = self._datetime_to_index(end)
        idx_range = end_idx - start_idx
        range_mask = ((1 << (idx_range + 1)) - 1) << start_idx

        has_overlap = (self._backing_int & range_mask) > 0
        self._backing_int |= range_mask
        return has_overlap

    def __contains__(self, time):
        if self._start_time is None or time < self._start_time:
            return False
        time_idx = self._datetime_to_index(time)
        return (self._backing_int & (1 << time_idx)) > 0

    def copy(self):
        result = TimeSpanSet()
        result._start_time = self._start_time
        result._backing_int = self._backing_int
        return result


def is_valid(schedule: List[CourseOffering]) -> bool:
    timeset = TimeSpanSet()
    for i in range(1, 7):
        timeset.add_range(datetime(2018, 1, i, 0, 0),
                          datetime(2018, 1, i, 10, 0))

    for cls in schedule:
        for slot in cls.times:
            has_overlap = timeset.add_range(slot[0], slot[1])
            if has_overlap:
                # overlap occurred
                return False
    return True


def filter_my_courses(courselist: List[CourseOffering]) -> List[CourseOffering]:
    return [course for course in courselist
            if course.course in {
                'CSC 4310',
                'CSC 4330',
                'CSC 4210',
                'ECON 2100',
                'PHIL 1010'}]


def get_all_schedules(courses: List[CourseOffering]):
    grouped_schedules = [list(v[1]) for v in
                         groupby(courses, key=lambda a: a.course)]
    for schedule in sorted(product(*grouped_schedules),
                           key=lambda sch: sum(
                               (1 if v.remaining_capacity > 0 else 0) for v in
                               sch)):
        if is_valid(schedule):
            yield schedule


if __name__ == '__main__':
    results = sorted(
        get_all_schedules(
            filter_my_courses(
                parse_file('../resources/gsu courses.html'))))
    print("found {} unique schedules".format(len(results)))
    for schedule in results:
        for v in sorted(schedule, key=lambda v: v.times):
            print('''\
{course} {instructor} (#{crn}, {remaining_capacity} left)
{location}'''.format(**v._asdict()))
            for time in v.times:
                print('{:%a %H:%M}-{:%H:%M}'.format(*time))
        print('=' * 30)
