# pylint: disable=no-member

import datetime
import importlib
import json
import os

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse, HttpResponseNotFound, \
                        FileResponse, UnreadablePostError
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from django.contrib.admin.views.decorators import staff_member_required

from .models import DataPoint, DataBundle, DataFile, DataSourceGroup, DataSource, ReportJob, \
                    generator_label, install_supports_jsonfield

@csrf_exempt
def add_data_point(request):
    response = {'message': 'Data point added successfully.'}

    if request.method == 'CREATE':
        response = HttpResponse(json.dumps(response, indent=2), content_type='application/json', \
                                status=201)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'CREATE, POST'
        response['Access-Control-Request-Headers'] = 'Content-Type'
        response['Access-Control-Allow-Headers'] = 'Content-Type'

        point = json.loads(request.body)

        data_point = DataPoint(recorded=timezone.now())
        data_point.source = point['passive-data-metadata']['source']
        data_point.generator = point['passive-data-metadata']['generator']
        data_point.created = datetime.datetime.fromtimestamp(point['passive-data-metadata']['source'], tz=timezone.get_default_timezone()) # pylint: disable=line-too-long

        if install_supports_jsonfield():
            data_point.properties = point
        else:
            data_point.properties = json.dumps(point, indent=2)

        data_point.save()

        return response
    elif request.method == 'POST':
        response = HttpResponse(json.dumps(response, indent=2), \
                                content_type='application/json', \
                                status=201)

        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'CREATE, POST'
        response['Access-Control-Request-Headers'] = 'Content-Type'
        response['Access-Control-Allow-Headers'] = 'Content-Type'

        point = json.loads(request.POST['payload'])

        data_point = DataPoint(recorded=timezone.now())
        data_point.source = point['passive-data-metadata']['source']
        data_point.generator = point['passive-data-metadata']['generator']
        data_point.created = datetime.datetime.fromtimestamp(point['passive-data-metadata']['source'], tz=timezone.get_default_timezone()) # pylint: disable=line-too-long

        if install_supports_jsonfield():
            data_point.properties = point
        else:
            data_point.properties = json.dumps(point, indent=2)

        data_point.save()

        return response
    elif request.method == 'OPTIONS':
        response = HttpResponse('', content_type='text/plain', status=200)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'CREATE, POST'
        response['Access-Control-Request-Headers'] = 'Content-Type'
        response['Access-Control-Allow-Headers'] = 'Content-Type'

        return response

    return HttpResponseNotAllowed(['CREATE', 'POST'])


@csrf_exempt
def add_data_bundle(request): # pylint: disable=too-many-statements
    response = {'message': 'Data bundle added successfully, and ready for processing.'}

    if request.method == 'CREATE':
        response = HttpResponse(json.dumps(response, indent=2), \
                                content_type='application/json', \
                                status=201)

        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'CREATE, POST'
        response['Access-Control-Request-Headers'] = 'Content-Type'
        response['Access-Control-Allow-Headers'] = 'Content-Type'

        points = None

        try:
            points = json.loads(request.body)
        except UnreadablePostError:
            response = {'message': 'Unable to parse data bundle.'}
            response = HttpResponse(json.dumps(response, indent=2), \
                                    content_type='application/json', \
                                    status=400)

            return response

        bundle = DataBundle(recorded=timezone.now())

        if install_supports_jsonfield():
            bundle.properties = points
        else:
            bundle.properties = json.dumps(points, indent=2)

        bundle.save()

        return response

    elif request.method == 'POST':
        response = HttpResponse(json.dumps(response, indent=2), \
                                content_type='application/json', \
                                status=201)

        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'CREATE, POST'
        response['Access-Control-Request-Headers'] = 'Content-Type'
        response['Access-Control-Allow-Headers'] = 'Content-Type'

        try:
            points = json.loads(request.POST['payload'])

            bundle = DataBundle(recorded=timezone.now())

            if install_supports_jsonfield():
                bundle.properties = points
            else:
                bundle.properties = json.dumps(points, indent=2)

            bundle.save()
        except ValueError:
            response = {'message': 'Unable to parse data bundle.'}
            response = HttpResponse(json.dumps(response, indent=2), \
                                    content_type='application/json', \
                                    status=400)
        except UnreadablePostError:
            response = {'message': 'Unable to parse data bundle.'}
            response = HttpResponse(json.dumps(response, indent=2), \
                                    content_type='application/json', \
                                    status=400)

        for key, value in request.FILES.iteritems(): # pylint: disable=unused-variable
            data_file = DataFile(data_bundle=bundle)
            data_file.identifier = value.name
            data_file.content_type = value.content_type
            data_file.content_file.save(value.name, value)
            data_file.save()

        return response
    elif request.method == 'OPTIONS':
        response = HttpResponse('', content_type='text/plain', status=200)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'CREATE, POST'
        response['Access-Control-Request-Headers'] = 'Content-Type'
        response['Access-Control-Allow-Headers'] = 'Content-Type'

        return response

    return HttpResponseNotAllowed(['CREATE', 'POST'])

@staff_member_required
def pdk_home(request):
    for app in settings.INSTALLED_APPS:
        try:
            app_views = importlib.import_module(app + '.views')

            return app_views.custom_pdk_home(request)
        except ImportError:
            pass
        except AttributeError:
            pass

    context = {}

    if request.method == 'POST':
        if request.POST['operation'] == 'add_source':
            identifier = request.POST['source_identifier'].strip()
            name = request.POST['friendly_name'].strip()

            group = request.POST['assigned_group']
            group_name = request.POST['new_group_name'].strip()

            source = DataSource(identifier=identifier, name=name)

            if group == "-1":
                pass
            elif group == "0":
                group = DataSourceGroup.objects.filter(name=group_name).first()

                if group is None:
                    group = DataSourceGroup(name=group_name)
                    group.save()

                source.group = group
            else:
                source.group = DataSourceGroup.objects.get(pk=int(group))

            source.save()
        if request.POST['operation'] == 'remove_source':
            DataSource.objects.filter(pk=int(request.POST['pk'])).delete()

    context['groups'] = DataSourceGroup.objects.order_by('name')
    context['solo_sources'] = DataSource.objects.filter(group=None).order_by('name')

    return render(request, 'pdk_home.html', context=context)

@staff_member_required
def pdk_source(request, source_id): # pylint: disable=unused-argument
    context = {}

    source = DataSource.objects.filter(identifier=source_id).first()

    if source is None:
        source = DataSource(identifier=source_id, name='Unknown')
        source.save()

    context['source'] = source

    return render(request, 'pdk_source.html', context=context)

@staff_member_required
def pdk_source_generator(request, source_id, generator_id): # pylint: disable=unused-argument
    context = {}

    source = DataSource.objects.filter(identifier=source_id).first()

    if source is None:
        source = DataSource(identifier=source_id, name='Unknown')
        source.save()

    context['source'] = source
    context['generator'] = generator_id
    context['generator_label'] = generator_label(generator_id)

    context['visualization'] = None

    for app in settings.INSTALLED_APPS:
        try:
            pdk_api = importlib.import_module(app + '.pdk_api')

            context['visualization'] = pdk_api.visualization(source, generator_id)
        except ImportError:
            pass
        except AttributeError:
            pass

    for app in settings.INSTALLED_APPS:
        try:
            pdk_api = importlib.import_module(app + '.pdk_api')

            context['data_table'] = pdk_api.data_table(source, generator_id)
        except ImportError:
            pass
        except AttributeError:
            pass

    return render(request, 'pdk_source_generator.html', context=context)

@staff_member_required
def unmatched_sources(request): # pylint: disable=unused-argument
    sources = []

    for point in DataPoint.objects.order_by('source').values_list('source', flat=True).distinct():
        sources.append(point)

    return JsonResponse(sources, safe=False, json_dumps_params={'indent': 2})


@staff_member_required
def pdk_visualization_data(request, source_id, generator_id, page): # pylint: disable=unused-argument
    folder = settings.MEDIA_ROOT + '/pdk_visualizations/' + source_id + '/' + generator_id

    filename = 'visualization-' + page + '.json'

    if page == '0':
        filename = 'visualization.json'

    try:
        with open(folder + '/' + filename) as data_file:
            return HttpResponse(data_file.read(), content_type='application/json')
    except IOError:
        pass

    return HttpResponseNotFound()

@staff_member_required
def pdk_download_report(request, report_id): # pylint: disable=unused-argument
    job = ReportJob.objects.get(pk=int(report_id))

    filename = settings.MEDIA_ROOT + '/' + job.report.name

    response = FileResponse(open(filename, 'rb'), content_type='application/octet-stream')

    response['Content-Length'] = os.path.getsize(filename)
    response['Content-Disposition'] = 'attachment; filename=pdk-export.zip'

    return response

@staff_member_required
def pdk_export(request): # pylint: disable=too-many-branches
    context = {}

    context['sources'] = DataPoint.objects.all().order_by('source')\
                                                .values_list('source', flat=True)\
                                                .distinct()

    context['generators'] = DataPoint.objects.all().order_by('generator_identifier')\
                                                   .values_list('generator_identifier', flat=True)\
                                                   .distinct()

    context['message'] = ''
    context['message_type'] = 'ok'

    if request.method == 'POST':
        export_sources = []
        export_generators = []

        for source in context['sources']:
            key = 'source_' + source

            if key in request.POST:
                export_sources.append(source)

        for generator in context['generators']:
            key = 'generator_' + generator

            if key in request.POST:
                export_generators.append(generator)

        if len(export_sources) == 0: # pylint: disable=len-as-condition
            context['message_type'] = 'error'

            if len(export_generators) == 0: # pylint: disable=len-as-condition
                context['message'] = 'Please select one or more sources and generators to export data.' # pylint: disable=line-too-long
            else:
                context['message'] = 'Please select one or more sources to export data.'
        elif len(export_generators) == 0: # pylint: disable=len-as-condition
            context['message_type'] = 'error'

            context['message'] = 'Please select one or more generators to export data.'
        else:
            job = ReportJob(requester=request.user, requested=timezone.now())

            params = {}

            params['sources'] = export_sources
            params['generators'] = export_generators

            if 'export_raw_json' in request.POST and request.POST['export_raw_json']:
                params['raw_data'] = True

            if install_supports_jsonfield():
                job.parameters = params
            else:
                job.parameters = json.dumps(params, indent=2)

            job.save()

            context['message_type'] = 'ok'
            context['message'] = 'Export job queued. Check your e-mail for a link to the output when the export is complete.' # pylint: disable=line-too-long

    return render(request, 'pdk_export.html', context=context)
