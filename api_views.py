# pylint: disable=no-member, line-too-long

import datetime
import json

import arrow

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse, HttpResponseNotAllowed
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import authenticate

from passive_data_kit.models import DataServerApiToken, DataPoint, DataServerAccessRequestPending, DataSource


def valid_pdk_token_required(function):
    def wrap(request, *args, **kwargs):
        token = request.POST['token']

        now = timezone.now()

        expires = Q(expires__gte=now) | Q(expires=None)

        if DataServerApiToken.objects.filter(token=token).filter(expires).count() > 0:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied('Invalid Token')

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__

    return wrap


@csrf_exempt
def pdk_request_token(request):
    user = authenticate(
        username=request.POST['username'], password=request.POST['password'])

    if user is not None and user.is_staff:
        now = timezone.now()

        token = user.pdk_api_tokens.order_by('-expires').first()

        if (token is not None) and (token.expires < now):
            token = None

        if token is None:
            token_duration = datetime.timedelta(days=7)

            try:
                token_duration = datetime.timedelta(
                    seconds=settings.PDK_TOKEN_LIFESPAN)
            except AttributeError:
                print 'Unable to locate PDK_TOKEN_LIFESPAN in settings'

            token = DataServerApiToken(
                user=user, expires=(now + token_duration))
            token.save()

        response = {}
        response['token'] = token.fetch_token()
        response['expires'] = token.expires.isoformat()

        return HttpResponse(json.dumps(response), content_type='application/json')

    return HttpResponseNotAllowed(['POST'])


@csrf_exempt
@valid_pdk_token_required
def pdk_data_point_query(request):  # pylint: disable=too-many-locals, too-many-branches
    if request.method == 'POST':
        page_size = int(request.POST['page_size'])
        page_index = int(request.POST['page_index'])

        filters = json.loads(request.POST['filters'])
        excludes = json.loads(request.POST['excludes'])
        order_bys = json.loads(request.POST['order_by'])

        latest = None

        if 'latest' in request.POST:
            latest = int(request.POST['latest_pk'])
        else:
            latest_point = DataPoint.objects.all().order_by('-pk').first()

            latest = latest_point.pk

        query = DataPoint.objects.filter(pk__lte=latest)

        for filter_obj in filters:
            processed_filter = {}

            for field, value in filter_obj.iteritems():
                if value is not None:
                    if field == 'created' or field == 'recorded':
                        value = arrow.get(value).datetime

                processed_filter[field] = value

            query = query.filter(**processed_filter)

        for exclude in excludes:
            processed_exclude = {}

            for field, value in exclude.iteritems():
                if value is not None:
                    if field == 'created' or field == 'recorded':
                        value = arrow.get(value).datetime

                processed_exclude[field] = value

            query = query.exclude(**processed_exclude)

        payload = {
            'latest': latest,
            'count': query.count(),
            'page_index': page_index,
            'page_size': page_size,
        }

        processed_order_by = []

        for order_by in order_bys:
            for item in order_by:
                processed_order_by.append(item)

        if processed_order_by:
            query = query.order_by(*processed_order_by)

        matches = []

        for item in query[(page_index * page_size):((page_index + 1) * page_size)]:
            matches.append(item.fetch_properties())

        payload['matches'] = matches

        token = DataServerApiToken.objects.filter(
            token=request.POST['token']).first()

        access_request = DataServerAccessRequestPending()

        if token is not None:
            access_request.user_identifier = str(
                token.user.pk) + ': ' + str(token.user.username)
        else:
            access_request.user_identifier = 'api_token: ' + \
                request.POST['token']

        access_request.request_type = 'api-data-points-request'
        access_request.request_time = timezone.now()
        access_request.request_metadata = json.dumps(request.POST, indent=2)
        access_request.successful = True
        access_request.save()

        return HttpResponse(json.dumps(payload), content_type='application/json')

    return HttpResponseNotAllowed(['POST'])


@csrf_exempt
@valid_pdk_token_required
def pdk_data_source_query(request):  # pylint: disable=too-many-locals, too-many-branches
    if request.method == 'POST':
        page_size = int(request.POST['page_size'])
        page_index = int(request.POST['page_index'])

        filters = json.loads(request.POST['filters'])
        excludes = json.loads(request.POST['excludes'])
        order_bys = json.loads(request.POST['order_by'])

        query = None

        for filter_obj in filters:
            processed_filter = {}

            for field, value in filter_obj.iteritems():
                if value is not None:
                    if field == 'created' or field == 'recorded':
                        value = arrow.get(value).datetime

                processed_filter[field] = value

            if query is None:
                query = DataSource.objects.filter(**processed_filter)
            else:
                query = query.filter(**processed_filter)

        for exclude in excludes:
            processed_exclude = {}

            for field, value in exclude.iteritems():
                if value is not None:
                    if field == 'created' or field == 'recorded':
                        value = arrow.get(value).datetime

                processed_exclude[field] = value

            if query is None:
                query = DataSource.objects.exclude(**processed_exclude)
            else:
                query = query.exclude(**processed_exclude)

        if query is None:
            query = DataSource.objects.all()

        query = query.order_by('identifier')

        payload = {
            'count': query.count(),
            'page_index': page_index,
            'page_size': page_size,
        }

        processed_order_by = []

        for order_by in order_bys:
            for item in order_by:
                processed_order_by.append(item)

        if processed_order_by:
            query = query.order_by(*processed_order_by)

        matches = []

        for item in query[(page_index * page_size):((page_index + 1) * page_size)]:
            matches.append(item.fetch_definition())

        payload['matches'] = matches

        token = DataServerApiToken.objects.filter(
            token=request.POST['token']).first()

        access_request = DataServerAccessRequestPending()

        if token is not None:
            access_request.user_identifier = str(
                token.user.pk) + ': ' + str(token.user.username)
        else:
            access_request.user_identifier = 'api_token: ' + \
                request.POST['token']

        access_request.request_type = 'api-data-source-request'
        access_request.request_time = timezone.now()
        access_request.request_metadata = json.dumps(request.POST, indent=2)
        access_request.successful = True
        access_request.save()

        return HttpResponse(json.dumps(payload), content_type='application/json')

    return HttpResponseNotAllowed(['POST'])
