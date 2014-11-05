# Copyright 2014 Dave Kludt
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from dateutil import tz, parser, relativedelta
from datetime import datetime, timedelta, date
from flask import g
from operator import itemgetter
from isoweek import Week

import re
import forms
import pymongo


MONTHS = [
    '', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
]
SORT_FIELD = 'completed_at'
QUERY_FIELD = 'Completed At'


def unslug(value):
    text = re.sub('_', ' ', value)
    return text.title()


def slugify(data):
        temp_string = re.sub(' +', ' ', str(data.strip()))
        return re.sub(' ', '_', temp_string)


def parse_field_data(value):
        choices = re.sub('\r\n', ',', value)
        return choices.split(',')


def get_reporting_collection():
    report_settings = g.db.settings.find_one({}, {'reporting': 1})
    if report_settings:
        return report_settings.get('reporting').get('collection')
    return None


def generate_field_choices(all_items, field):
    temp = []
    for choice in all_items:
        test = field.split('.')
        if len(test) > 1:
            data = choice.get(test[0]).get(test[1])
        else:
            if field == 'region':
                data = choice.get(field)
                if not data:
                    data = choice.get('data_center')
            else:
                data = choice.get(field)

        if data and data not in temp:
            temp.append(data)

    if field == 'region':
        temp_choices = [
            (item, item.upper()) for item in temp
        ]
    elif field == 'request.verb':
        temp_choices = [
            (item, item.upper()) for item in temp
        ]
    else:
        temp_choices = [
            (item, unslug(item)) for item in temp
        ]

    temp_choices.insert(0, ('', ''))
    return temp_choices


def generate_reporting_form(settings):
    collection = get_reporting_collection()

    class F(forms.Reporting):
        pass

    fields = g.db.reporting.find({'searchable': True})
    for field in fields:
        if field.get('field_display_label'):
            label = field.get('field_display_label')
        else:
            label = unslug(field.get('field_name'))

        if field.get('data_type') == 'boolean':
            if field.get('field_display') == 'SelectField':
                choices = [('', ''), (1, 'True'), (0, 'False')]
                setattr(
                    F,
                    unslug(field.get('field_name')),
                    forms.SelectField(
                        '%s:' % label,
                        choices=choices
                    )
                )
            else:
                setattr(
                    F,
                    unslug(field.get('field_name')),
                    forms.BooleanField('%s:' % label)
                )
        elif field.get('data_type') == 'datetime':
            setattr(
                F,
                '%s-start' % unslug(field.get('field_name')),
                forms.TextField(
                    'Start Date:',
                    id='date_time_start'
                )
            )
            setattr(
                F,
                '%s-end' % unslug(field.get('field_name')),
                forms.TextField(
                    'End Date:',
                    id='date_time_end'
                )
            )
        elif field.get('data_type') == 'user_select':
            setattr(
                F,
                unslug(field.get('field_name')),
                forms.TextField(
                    '%s:' % label,
                    description='user_select'
                )
            )
        elif field.get('field_display') == 'TextField':
            setattr(
                F,
                unslug(field.get('field_name')),
                forms.TextField(
                    '%s:' % label
                )
            )
        elif field.get('field_display') == 'SelectField':
            all_fields = getattr(g.db, collection).find()
            if field.get('field_display_data'):
                select_items = parse_field_data(
                    field.get('field_display_data')
                )
                select_items.insert(0, '')
                choices = [(item, item) for item in select_items]
            else:
                choices = generate_field_choices(
                    all_fields,
                    field.get('field_name')
                )

            setattr(
                F,
                unslug(field.get('field_name')),
                forms.SelectField(
                    '%s:' % label,
                    choices=choices
                )
            )

    setattr(
        F,
        'submit',
        forms.SubmitField('Generate Report')
    )
    return F()


def check_for_field(field, collection):
    data = getattr(g.db, collection).find_one({field: {'$exists': True}})
    if data:
        return True
    else:
        return False


def generate_reporting_query(request):
    query, form_data = {}, {}
    fields = g.db.reporting.find({'searchable': True})
    if request.form:
        for key, value in request.form.iteritems():
            form_data[key] = value

    elif request.json:
        for key, value in request.json.iteritems():
            form_data[key] = value

    for field in fields:
        form_field = field.get('field_name')
        title_field = unslug(form_field)
        if form_data.get(title_field):
            data = form_data.get(title_field)
            if field.get('field_display') == 'TextField':
                query[form_field] = {
                    '$regex': data,
                    '$options': 'i'
                }
            elif field.get('field_display') == 'SelectField':
                if field.get('data_type') == 'boolean':
                    query[form_field] = bool(int(data))
                else:
                    if form_field == 'request.verb':
                        query[form_field] = data
                    else:
                        query[form_field] = data.lower()

            elif field.get('field_display') == 'BooleanField':
                query[form_field] = bool(data)

        if (
            field.get('field_display') == 'TextField' and
            field.get('data_type') == 'datetime'
        ):
            start_name = '%s-start' % title_field
            end_name = '%s-end' % title_field
            if (
                form_data.get(start_name) and
                form_data.get(end_name) and
                form_data.get(start_name) != '' and
                form_data.get(end_name) != ''
            ):
                after_date = parser.parse(form_data.get(start_name))
                before_date = parser.parse(form_data.get(end_name))
                before_date = before_date + timedelta(days=1)
                query[form_field] = {'$gte': after_date, '$lt': before_date}

            elif (
                form_data.get(start_name) and
                form_data.get(start_name) != ''
            ):
                after_date = parser.parse(form_data.get(start_name))
                query[form_field] = {'$gte': after_date}

            elif (
                form_data.get(end_name) and
                form_data.get(end_name) != ''
            ):
                before_date = parser.parse(form_data.get(end_name))
                before_date = before_date + timedelta(days=1)
                query[form_field] = {'$lt': before_date}

    return query


def generate_reporting_trend_query(request):
    label_keys = ['region']
    query = generate_reporting_query(request)
    key = request.json.get('graph_key')
    value = request.json.get('search_on')
    if key in label_keys:
        value = slugify(value.lower())
    else:
        query[key] = value

    return query


def getFromDict(dataDict, mapList):
    return reduce(lambda d, k: d[k], mapList, dataDict)


def generate_graph_data(results):
    data, graph_keys, graph_labels = {}, [], []
    fields = g.db.reporting.find({'graphable': True})
    for field in fields:
        if field.get('field_display_label'):
            graph_labels.append(field.get('field_display_label'))
        else:
            graph_labels.append(field.get('field_name'))
        graph_keys.append(field.get('field_name'))

    for key in graph_keys:
        key_test = key.split('.')
        if not data.get(key):
            data[key] = {}
        for item in results.rewind():
            if len(key_test) > 1:
                key_test = [x for x in key_test]
                try:
                    temp_data_val = getFromDict(item, key_test)
                except:
                    temp_data_val = 'None'

            else:
                if key == 'region':
                    temp_data_val = item.get(key)
                    if not temp_data_val:
                        temp_data_val = item.get('data_center')
                else:
                    temp_data_val = item.get(key)

            try:
                data[key][temp_data_val] += 1
            except:
                data[key][temp_data_val] = 1

    plot_data = {}
    label_keys = ['region']
    for key, value in data.iteritems():
        sorted_data = sorted(value.items(), key=itemgetter(1), reverse=True)
        points, labels = [], []
        for label, data_point in sorted_data:
            if key in label_keys:
                if label is not None:
                    labels.append(label.upper())
            else:
                labels.append(label)
            points.append(data_point)

        if len(points) > 10:
            points = points[:10]
            labels = labels[:10]

        plot_data[key] = {
            'labels': labels,
            'points': points
        }

    return plot_data, graph_keys, graph_labels


def generate_graph_trending_data(results, request):
    temp_data, data, labels = {}, [], []
    start_date, end_date = None, None
    if request.json.get('%s-start' % QUERY_FIELD):
        start_date = get_iso_week_date_attributes(
            request.json.get('%s-start' % QUERY_FIELD),
            'days'
        )

    if request.json.get('%s-end' % QUERY_FIELD):
        end_date = get_iso_week_date_attributes(
            request.json.get('%s-end' % QUERY_FIELD),
            'days'
        )

    for item in results.get('result'):
        date_info = item.get('_id')
        if date_info:
            year = date_info.get('year')
            month = date_info.get('month')
            day = date_info.get('day')

        if temp_data.get(year):
            if temp_data[year].get(month):
                if temp_data[year][month].get(day):
                    temp_data[year][month][day] += item.get('count')
                else:
                    temp_data[year][month][day] = item.get('count')
            else:
                temp_data[year][month] = {}
                temp_data[year][month][day] = item.get('count')
        else:
            temp_data[year] = {}
            temp_data[year][month] = {}
            temp_data[year][month][day] = item.get('count')

    if start_date and end_date:
        loop_start = start_date
        loop_end = end_date
    elif start_date:
        loop_start = start_date
        loop_end = datetime.now()
    elif end_date:
        year = sorted(temp_data)[0]
        month = sorted(temp_data[year])[0]
        day = sorted(temp_data[year][month])[0]
        loop_start = datetime(year, month, day)
        loop_end = end_date
    else:
        year = sorted(temp_data)[0]
        month = sorted(temp_data[year])[0]
        day = sorted(temp_data[year][month])[0]
        loop_start = datetime(year, month, day)
        loop_end = datetime.now()

    day_delta = (loop_end - loop_start).days
    for day in range(0, day_delta + 1):
        loop_date = loop_start + relativedelta.relativedelta(days=day)
        if not temp_data.get(loop_date.year):
            temp_data[loop_date.year] = {}
            temp_data[loop_date.year][loop_date.month] = {}
            temp_data[loop_date.year][loop_date.month][loop_date.day] = 0
        elif not temp_data[loop_date.year].get(loop_date.month):
            temp_data[loop_date.year][loop_date.month] = {}
            temp_data[loop_date.year][loop_date.month][loop_date.day] = 0
        elif not temp_data[loop_date.year][loop_date.month].get(loop_date.day):
            temp_data[loop_date.year][loop_date.month][loop_date.day] = 0

    for year in sorted(temp_data):
        for month in sorted(temp_data[year]):
            for day in sorted(temp_data[year][month]):
                data.append(temp_data[year][month][day])
                temp_date = datetime(year, month, day)
                labels.append(temp_date.strftime('%b %d, %Y'))

    return data, labels


def get_delta_days_for_trending(request, collection):
    todays_date = datetime.now(tz.tzlocal())
    start_date = request.json.get('%s-start' % QUERY_FIELD)
    end_date = request.json.get('%s-end' % QUERY_FIELD)

    if start_date and end_date:
        delta = parser.parse(end_date) - parser.parse(start_date)
    elif start_date:
        delta = todays_date - parser.parse(start_date).replace(
            tzinfo=tz.tzlocal()
        )
    elif end_date:
        first_element = getattr(g.db, collection).find().sort(
            SORT_FIELD,
            pymongo.ASCENDING
        ).limit(1)
        start_date = first_element[0].get(SORT_FIELD)
        delta = parser.parse(end_date).replace(
            tzinfo=tz.tzlocal()
        ) - start_date
    else:
        first_element = getattr(g.db, collection).find().sort(
            SORT_FIELD, pymongo.ASCENDING
        ).limit(1)
        start_date = first_element[0].get(SORT_FIELD)
        delta = todays_date - start_date

    return delta.days


def generate_monthly_trend(results, request):
    label, data, temp_data = [], [], {}
    for item in results.get('result'):
        year = item.get('_id').get('year')
        month = item.get('_id').get('month')
        if temp_data.get(year):
            if temp_data[year].get(month):
                temp_data[year][month]['count'] += item.get('count')
            else:
                temp_data[year][month] = {
                    'count': item.get('count')
                }
        else:
            temp_data[year] = {}
            temp_data[year][month] = {
                'count': item.get('count')
            }

    start_date, end_date = None, None
    today = get_iso_week_date_attributes(datetime.now(), 'month')
    if request.json.get('%s-start' % QUERY_FIELD):
        start_date = get_iso_week_date_attributes(
            request.json.get('%s-start' % QUERY_FIELD),
            'month'
        )
    if request.json.get('%s-end' % QUERY_FIELD):
        end_date = get_iso_week_date_attributes(
            request.json.get('%s-end' % QUERY_FIELD),
            'month'
        )

    if start_date and end_date:
        loop_start = start_date
        loop_end = end_date
    elif start_date:
        loop_start = start_date
        loop_end = today
    elif end_date:
        year = sorted(temp_data)[0]
        month = sorted(temp_data[year])[0]
        loop_start = datetime(year, month, 1)
        loop_end = end_date
    else:
        year = sorted(temp_data)[0]
        month = sorted(temp_data[year])[0]
        loop_start = datetime(year, month, 1)
        loop_end = today

    range_to_use = abs(
        relativedelta.relativedelta(loop_start, loop_end).months
    )
    if range_to_use == 0:
        year_check = abs(
            relativedelta.relativedelta(loop_start, loop_end).years
        )
        if year_check > 0:
            range_to_use = year_check * 12

    for month_add in range(
        0,
        range_to_use + 1
    ):
        loop_date = loop_start + relativedelta.relativedelta(months=month_add)
        if not temp_data.get(loop_date.year):
            temp_data[loop_date.year] = {}
            temp_data[loop_date.year][loop_date.month] = {
                'count': 0
            }
        else:
            if not temp_data[loop_date.year].get(loop_date.month):
                temp_data[loop_date.year][loop_date.month] = {
                    'count': 0
                }

    for year in sorted(temp_data):
        for month in sorted(temp_data.get(year)):
            label.append(
                '%s-%s' % (MONTHS[month], year)
            )
            data.append(
                temp_data[year][month].get('count')
            )
    return label, data


def get_iso_week_date_attributes(use_date, time_frame):
    if type(use_date) is not datetime:
        temp_date = parser.parse(use_date)
    else:
        temp_date = use_date

    if time_frame == 'week':
        temp_week = temp_date.isocalendar()[1]
        temp_monday = temp_date - timedelta(
            days=(
                temp_date.isocalendar()[2] - 1
            )
        )
        return temp_date, temp_week, temp_monday
    elif time_frame == 'month':
        return datetime(temp_date.year, temp_date.month, 1)
    elif time_frame == 'days':
        return temp_date


def generate_weekly_trend(results, request):
    start_date, end_date = None, None
    today, today_week, today_monday = get_iso_week_date_attributes(
        datetime.now(),
        'week'
    )
    if request.json.get('%s-start' % QUERY_FIELD):
        start_date, start_week, start_monday = get_iso_week_date_attributes(
            request.json.get('%s-start' % QUERY_FIELD),
            'week'
        )

    if request.json.get('%s-end' % QUERY_FIELD):
        end_date, end_week, end_monday = get_iso_week_date_attributes(
            request.json.get('%s-end' % QUERY_FIELD),
            'week'
        )

    label, data = [], []
    temp_data = {}
    for item in results.get('result'):
        id_data = item.get('_id')
        temp_date = date(
            id_data.get('year'),
            id_data.get('month'),
            id_data.get('day')
        )
        year = temp_date.year
        week = temp_date.isocalendar()[1]
        if not year == temp_date.isocalendar()[0]:
            year = temp_date.isocalendar()[0]

        if temp_data.get(year):
            if temp_data[year].get(week):
                temp_data[year][week]['count'] += item.get('count')
            else:
                temp_data[year][week] = {
                    'count': item.get('count'),
                    'date': temp_date
                }
        else:
            temp_data[year] = {}
            temp_data[year][week] = {
                'count': item.get('count'),
                'date': temp_date
            }

    if start_date and end_date:
        loop_start = start_monday
        loop_end = end_monday
    elif start_date:
        loop_start = start_monday
        loop_end = today_monday
    elif end_date:
        year = sorted(temp_data)[0]
        week = sorted(temp_data[year])[0]
        loop_start = datetime.combine(
            temp_data[year][week].get('date') - timedelta(
                days=(
                    temp_data[year][week].get('date').isocalendar()[2] - 1
                )
            ),
            datetime.min.time()
        )
        loop_end = end_monday
    else:
        year = sorted(temp_data)[0]
        week = sorted(temp_data[year])[0]
        loop_start = datetime.combine(
            temp_data[year][week].get('date') - timedelta(
                days=(
                    temp_data[year][week].get('date').isocalendar()[2] - 1
                )
            ),
            datetime.min.time()
        )
        loop_end = today_monday

    week_delta = (loop_end - loop_start).days / 7
    for week in range(0, week_delta + 1):
        loop_date = loop_start + relativedelta.relativedelta(days=(week * 7))
        if not temp_data.get(loop_date.year):
            temp_data[loop_date.year] = {}
            loop_year = loop_date.year
            if not loop_year == loop_date.isocalendar()[0]:
                loop_year = loop_date.isocalendar()[0]

            temp_data[loop_year][loop_date.isocalendar()[1]] = {
                'count': 0,
                'date': loop_date
            }
        else:
            loop_year = loop_date.year
            if not loop_year == loop_date.isocalendar()[0]:
                loop_year = loop_date.isocalendar()[0]

            if not temp_data[loop_year].get(loop_date.isocalendar()[1]):
                temp_data[loop_year][loop_date.isocalendar()[1]] = {
                    'count': 0,
                    'date': loop_date
                }

    for year in sorted(temp_data):
        for week in sorted(temp_data[year]):
            label.append(
                'Week of %s' % (
                    Week(year, week).monday().strftime('%m-%d-%Y')
                )
            )
            data.append(temp_data[year][week].get('count'))

    return label, data
