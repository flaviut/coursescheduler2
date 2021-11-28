# coursescheduler2

Simple application to help figure out acceptable schedules, as well as a tool
to automatically register for courses. Note: Banner typically limits you to
just a few thousand registration attempts, so you may want to be careful using
this tool.

You give this program a list of the courses you'd like, and this program will
give you a list of all non-overlapping schedules.

## Usage

Requires Python 3.6.

```commandline
virtualenv -p python3.6 venv
source venv/bin/activate
pip install -r requiremnts.txt
python -m coursescheduler.calculate_schedules
```

To change the classes that you'd like to register for, change line 69 in
`coursescheduler/calculate_schedules.py`.

To change the way that the results are presented, change line 78.

To make this work for other schools, check out the docstring in
`coursescheduler/load_classes.py` and see if you can adapt it to your school's
system.