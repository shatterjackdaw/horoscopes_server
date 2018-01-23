# -*- coding:utf-8 -*-
import datetime
import logging
import traceback
from django.conf import settings
from django.http import JsonResponse


elapse_logger = logging.getLogger('elapse_log')
except_logger = logging.getLogger('except_log')


class ElapseMiddleware(object):
    def __init__(self):
        self.start = None
        self.raw_data = ''

    def process_request(self, request):
        self.start = datetime.datetime.now()

    def process_response(self, request, response):
        get_para = ['%s:%s' % (k, v) for k, v in request.GET.items()]
        post_para = ['%s:%s' % (k, v) for k, v in request.POST.items()]
        access_line = ['elapse: %s' % str(datetime.datetime.now() - self.start),
                       'method: %s' % request.method,
                       'ip: %s' % request.META['REMOTE_ADDR'],
                       'code: %s' % response.status_code,
                       'path: %s' % request.path,
                       'GET: %s' % str(get_para),
                       'POST: %s' % str(post_para),
                       'User-Agent: %s' % request.META.get('HTTP_USER_AGENT', '')]
        elapse_logger.info(', '.join(access_line))

        return response


class ExceptionMiddleware(object):
    def __init__(self):
        self.start = None

    def process_exception(self, request, exception):
        """
        process_exception() 应当返回 None 或 HttpResponse 对象
        """
        except_logger.error(traceback.format_exc())

    def process_response(self, request, response):
        if request.GET.get('version') and not settings.DEBUG:
            if response.status_code == 500:
                return JsonResponse({'status': 500, 'msg': u'服务器内部错误'}, status=500)
            elif response.status_code == 404:
                return JsonResponse({'status': 404, 'msg': u'页面不存在'}, status=404)
        return response