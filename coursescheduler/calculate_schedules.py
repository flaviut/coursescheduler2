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

        result = False
        if self._backing_int & range_mask:
            result = True

        self._backing_int |= range_mask

        return result

    def __contains__(self, time):
        if self._start_time is None or time < self._start_time:
            return False
        time_idx = self._datetime_to_index(time)
        return (self._backing_int & (1 << time_idx)) > 0


def is_valid(schedule: List[CourseOffering]) -> bool:
    timeset = TimeSpanSet()
    for cls in schedule:
        for slot in cls.times:
            if timeset.add_range(slot[0], slot[1]):
                # overlap occurred
                return False
    return True


def filter_my_courses(courselist: List[CourseOffering]) -> List[CourseOffering]:
    return [course for course in courselist
            if course.course in {'CSC 4350', 'MATH 3030', 'CSC 3320',
                                 'CSC 4330', 'CSC 4520'}]


def get_all_schedules(courses: List[CourseOffering]):
    grouped_schedules = [list(v[1]) for v in
                         groupby(courses, key=lambda a: a.course)]
    for schedule in product(*grouped_schedules):
        if is_valid(schedule):
            print([(v.crn, v.course, v.remaining_capacity) for v in schedule])


if __name__ == '__main__':
    get_all_schedules(
        filter_my_courses(parse_file('../resources/gsu courses.html')))
