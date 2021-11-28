from datetime import datetime
from itertools import groupby, product
from typing import List, Tuple, Set

from coursescheduler.common import CourseOffering
from coursescheduler.load_classes import parse_file

CourseTimes = List[Tuple[datetime, datetime]]


def _normalize_datetime(time_in: datetime):
    if time_in.second != 0 or time_in.microsecond != 0:
        return time_in.replace(second=0, microsecond=0)
    return time_in


class TimeSpanSet:
    def __init__(self):
        self._start_time = None
        self._backing_int = 0

    def _datetime_to_index(self, time_in) -> int:
        time_range = _normalize_datetime(time_in) - self._start_time
        return int(time_range.total_seconds() / 60)

    def add_range(self, start, end) -> bool:
        """Adds the range to the set. If there's an overlap, returns True,
        otherwise False"""
        start = _normalize_datetime(start)
        end = _normalize_datetime(end)
        assert end > start

        if self._start_time is None:
            self._start_time = start

        if start < self._start_time:
            delta = int((self._start_time - start).total_seconds() / 60)
            self._start_time = start
            self._backing_int = self._backing_int << delta

        start_idx = self._datetime_to_index(start)
        end_idx = self._datetime_to_index(end)
        idx_range = end_idx - start_idx
        range_mask = ((1 << (idx_range + 1)) - 1) << start_idx

        has_overlap = (self._backing_int & range_mask) > 0
        self._backing_int |= range_mask
        return has_overlap

    def __contains__(self, time):
        time = _normalize_datetime(time)
        if self._start_time is None or time < self._start_time:
            return False
        time_idx = self._datetime_to_index(time)
        return (self._backing_int & (1 << time_idx)) > 0

    def copy(self):
        result = TimeSpanSet()
        result._start_time = self._start_time
        result._backing_int = self._backing_int
        return result


def is_valid(schedule: List[CourseOffering],
             dead_zones: TimeSpanSet) -> bool:
    timeset = dead_zones.copy()

    for cls in schedule:
        for slot in cls.times:
            has_overlap = timeset.add_range(slot[0], slot[1])
            if has_overlap:
                # overlap occurred
                return False
    return True


def filter_my_courses(courselist: List[CourseOffering],
                      intersting_courses: Set[str]) -> List[CourseOffering]:
    return [course for course in courselist
            if course.course in intersting_courses]


def get_all_schedules(courses: List[CourseOffering],
                      dead_zones: TimeSpanSet):
    grouped_schedules = [list(v[1]) for v in
                         groupby(courses, key=lambda a: a.course)]
    for schedule in sorted(product(*grouped_schedules),
                           key=lambda sch: sum(
                               (1 if v.remaining_capacity > 0 else 0)
                               for v in sch)):
        if is_valid(schedule, dead_zones):
            yield schedule


def print_schedules(schedules: List[List[CourseOffering]]):
    print("found {} unique schedules".format(len(schedules)))
    for schedule in schedules:
        for v in sorted(schedule, key=lambda v: v.times):
            print('''\
{course} {instructor} (#{crn}, {remaining_capacity} left)
{location}'''.format(**v._asdict()))
            for time in v.times:
                print('{:%a %H:%M}-{:%H:%M}'.format(*time))
        print('=' * 30)


def main():
    course_list = parse_file('../resources/gsu courses.html')
    relevant_courses = filter_my_courses(course_list, intersting_courses={
        'CSC 4320',
        'CSC 4110',
        'CSC 4520',
    })

    time_set = TimeSpanSet()
    for i in range(1, 7):
        time_set.add_range(datetime(2018, 1, i, 0, 0),
                           datetime(2018, 1, i, 10, 0))

    schedules = sorted(get_all_schedules(relevant_courses, time_set))
    print_schedules(schedules)


if __name__ == '__main__':
    main()
