from datetime import datetime
from typing import NamedTuple, Tuple, List


class CourseOffering(NamedTuple):
    closed: bool
    crn: int
    course: str
    title: str
    times: List[Tuple[datetime, datetime]]
    campus: str
    capacity: int
    remaining_capacity: int
    xlist_capacity: int
    xlist_remaining_capacity: int
    comments: str
    instructor: str
    location: str
