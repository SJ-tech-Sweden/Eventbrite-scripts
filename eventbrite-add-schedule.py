from datetime import datetime
import yaml
import requests
import pendulum
import json
import re

from eventbrite import Eventbrite

import logging
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', filename='EventScheduleAdd.log', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')

with open('config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

eventbrite_api_token = config['eventbrite']['api_token']
eventbrite_event_id = config['eventbrite']['event_id']
eventbrite_timezone = config['eventbrite']['event_timezone']
eventbrite_event_time = config['eventbrite']['event_time']

regex_time = "(?P<year>\d\d\d\d)-(?P<month>\d\d)-(?P<day>\d\d)T(?P<hour>\d\d):(?P<minutes>\d\d):(?P<seconds>\d\d)"

eventbrite = Eventbrite(eventbrite_api_token)

sunday = pendulum.now(eventbrite_timezone).next(pendulum.SUNDAY).at(eventbrite_event_time)
next_sunday_utc = sunday.in_tz('UTC')
next_sunday_utc = re.search(regex_time, next_sunday_utc.to_iso8601_string())
next_sunday_utc_regex = "{}{}{}T{}{}{}Z".format(
    next_sunday_utc.group('year'), next_sunday_utc.group('month'), next_sunday_utc.group('day'), next_sunday_utc.group('hour'), next_sunday_utc.group('minutes'), next_sunday_utc.group('seconds'))
next_sunday_utc = next_sunday_utc_regex
logging.info(next_sunday_utc)
values_dict = {
    "schedule": {
        "occurrence_duration": 5400,
        "recurrence_rule": 'DTSTART:{}\nRRULE:FREQ=WEEKLY;COUNT=1'.format(next_sunday_utc)
    }
}
values_json = json.dumps(values_dict, indent=2)

headers = {
    'Authorization': 'Bearer {}'.format(eventbrite_api_token),
    'Content-Type': 'application/json'
}

request = requests.post(
    'https://www.eventbriteapi.com/v3/events/{}/schedules/'.format(eventbrite_event_id), data=values_json, headers=headers)

logging.info(request.text)
