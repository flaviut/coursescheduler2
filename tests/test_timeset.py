from datetime import datetime

from coursescheduler.calculate_schedules import TimeSpanSet


def test_add():
    spanset = TimeSpanSet()

    spanset.add_range(datetime(2018, 1, 1, 0, 15),
                      datetime(2018, 1, 1, 0, 30))

    assert datetime(2018, 1, 1, 0, 15) in spanset
    assert datetime(2018, 1, 1, 0, 20) in spanset
    assert datetime(2018, 1, 1, 0, 30) in spanset

    assert datetime(2018, 1, 1, 0, 31) not in spanset
    assert datetime(2018, 1, 1, 0, 14) not in spanset

    assert datetime(2019, 1, 1, 0, 15) not in spanset
    assert datetime(2019, 1, 1, 0, 30) not in spanset

    assert spanset.add_range(datetime(2017, 1, 1, 0, 15),
                             datetime(2017, 1, 1, 0, 30)) is False
    assert spanset.add_range(datetime(2016, 1, 1, 0, 0),
                             datetime(2017, 1, 1, 0, 14)) is False
    assert spanset.add_range(datetime(2015, 12, 31, 0, 0),
                             datetime(2016, 1, 1, 0, 14)) is True
    assert spanset.add_range(datetime(2018, 1, 1, 0, 15),
                             datetime(2018, 1, 1, 0, 30)) is True
    assert spanset.add_range(datetime(2018, 1, 1, 0, 30),
                             datetime(2018, 1, 1, 0, 35)) is True
    assert spanset.add_range(datetime(2018, 1, 1, 13, 00),
                             datetime(2018, 1, 1, 13, 55)) is False
    assert spanset.add_range(datetime(2018, 1, 1, 13, 55),
                             datetime(2018, 1, 1, 14, 00)) is True
    assert spanset.add_range(datetime(2018, 1, 1, 13, 55),
                             datetime(2018, 1, 1, 14, 40)) is True
