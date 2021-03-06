# pylint: disable=line-too-long, no-member

import calendar
import datetime
import json
import os

from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

DEFAULT_INTERVAL = 600
DEFAULT_DAYS = 2

def generator_name(identifier): # pylint: disable=unused-argument
    return 'Data Frequency'

def compile_visualization(identifier, points, folder): # pylint: disable=unused-argument
    now = timezone.now()

    interval = DEFAULT_INTERVAL

    try:
        interval = settings.PDK_DATA_FREQUENCY_VISUALIZATION_INTERVAL
    except AttributeError:
        pass

    visualize_days = DEFAULT_DAYS

    try:
        visualize_days = settings.PDK_DATA_FREQUENCY_VISUALIZATION_DAYS
    except AttributeError:
        pass

    latest = points.order_by('-created').first()

    if latest is not None:
        now = latest.created

    now = now.replace(second=0, microsecond=0)

    remainder = now.minute % int(interval / 60)

    now = now.replace(minute=(now.minute - remainder))

    now += datetime.timedelta(seconds=interval)

    start = now - datetime.timedelta(days=visualize_days)

    end = start + datetime.timedelta(seconds=interval)

    timestamp_counts = {}

    keys = []

    while start < now:
        timestamp = str(calendar.timegm(start.timetuple()))

        keys.append(timestamp)

        timestamp_counts[timestamp] = points.filter(created__lte=end, created__gte=start).count()

        start = end
        end = start + datetime.timedelta(seconds=interval)

    timestamp_counts['keys'] = keys

    with open(folder + '/timestamp-counts.json', 'w') as outfile:
        json.dump(timestamp_counts, outfile, indent=2)


def visualization(source, generator): # pylint: disable=unused-argument
    filename = settings.MEDIA_ROOT + '/pdk_visualizations/' + source.identifier + '/pdk-data-frequency/timestamp-counts.json'

    context = {}

    try:
        with open(filename) as infile:
            data = json.load(infile)

            context['data'] = data

            context['updated'] = datetime.datetime.utcfromtimestamp(os.path.getmtime(filename))
    except IOError:
        context['data'] = {}
        context['updated'] = None

    return render_to_string('pdk_data_frequency_template.html', context)
