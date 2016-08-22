 # -*- coding: utf-8 -*-

import datetime
import json
import os
import pytz
import traceback

import importlib

from zipfile import ZipFile

from django.conf import settings
from django.core.files import File
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count
from django.template.loader import render_to_string
from django.utils import timezone

from passive_data_kit.decorators import handle_lock
from passive_data_kit.models import DataPoint, DataBundle, DataPointVisualizations, ReportJob

class Command(BaseCommand):
    help = 'Compiles data reports requested by end users.'

    def add_arguments(self, parser):
        pass
#        parser.add_argument('--delete',
#            action='store_true',
#            dest='delete',
#            default=False,
#            help='Delete data bundles after processing')
#
#        parser.add_argument('--count', 
#            type=int, 
#            dest='bundle_count',
#            default=100,
#            help='Number of bundles to process in a single run')
    
    @handle_lock
    def handle(self, *args, **options):
        os.umask(000)
        
        report = ReportJob.objects.filter(started=None, completed=None).order_by('requested').first()
        
        if report is not None:
            report.started = timezone.now()
            report.save()
            
            sources = report.parameters['sources']
            generators = report.parameters['generators']
            
            raw_json = False
            
            if ('raw_data' in report.parameters) and report.parameters['raw_data'] is True:
                raw_json = True
            
            filename = '/tmp/pdk_export_' + str(report.pk) + '.zip'

            with ZipFile(filename, 'w') as export_file:
                for generator in generators:
                    if raw_json:
                        for source in sources:
                            first = DataPoint.objects.filter(source=source, generator_identifier=generator).first()
                            last = DataPoint.objects.filter(source=source, generator_identifier=generator).last()
                            
                            if first is not None:
                                first_create = first.created
                                last_create = last.created
                                
                                start = datetime.datetime(first_create.year, first_create.month, first_create.day, 0, 0, 0, 0, first_create.tzinfo)
                                end = datetime.datetime(last_create.year, last_create.month, last_create.day, 0, 0, 0, 0, first_create.tzinfo) + datetime.timedelta(days=1)
                                
                                while start <= end:
                                    day_end = start + datetime.timedelta(days=1)
                                    
                                    day_filename = source + '__' + generator + '__' + start.date().isoformat() + '.json'
                                    
                                    points = DataPoint.objects.filter(source=source, generator_identifier=generator, created__gte=start, created__lt=day_end).order_by('created')
                                    
                                    out_points = []
                                    
                                    for point in points:
                                        out_points.append(point.properties)
                                        
                                    if len(out_points) > 0:
                                        export_file.writestr(day_filename, unicode(json.dumps(out_points, indent=2)).encode("utf-8"))
                                        
                                    start = day_end
                    else:
                        output_file = None
                
                        for app in settings.INSTALLED_APPS:
                            if output_file is None:
                                try:
                                    pdk_api = importlib.import_module(app + '.pdk_api')

                                    output_file = pdk_api.compile_report(generator, sources)
                                except ImportError:
    #                                traceback.print_exc()
                                    output_file = None
                                except AttributeError:
    #                                traceback.print_exc()
                                    output_file = None                                
                                
                        if output_file is not None:
                            export_file.write(output_file, output_file.split('/')[-1])
                        
                            os.remove(output_file)
                        
                export_file.close()
                
            report.report.save(filename.split('/')[-1], File(open(filename, 'r')))
            report.completed = timezone.now()
            report.save()
            
            subject = render_to_string('pdk_report_subject.txt', {'report': report, 'url': settings.SITE_URL})
            message = render_to_string('pdk_report_message.txt', {'report': report, 'url': settings.SITE_URL})
            
            host = settings.SITE_URL.split('/')[-2]

            send_mail(subject, message, 'Petey Kay <noreply@' + host + '>', [report.requester.email], fail_silently=False)
            

                            
                
            