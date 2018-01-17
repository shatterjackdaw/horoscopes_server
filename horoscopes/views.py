# coding:utf-8
from django.shortcuts import render
from django.http import JsonResponse
from models import HoroscopeDayLog, HoroscopeType


def index(request):
    horoscope_type = request.GET.get('horoscope')
    if not horoscope_type or horoscope_type not in HoroscopeType.ALL:
        return JsonResponse({'status': 1, 'desc': 'horoscope error!'})
    local_id = int(request.GET.get('local_id', 0))

    horoscope_static = HoroscopeDayLog.get_static_horoscope_data(str(horoscope_type))
    ret = {
        'status': 0,
        str(horoscope_type): {
            'today': HoroscopeDayLog.get_day_horoscope_log(local_id, horoscope_type, 0),
            'tomorrow': HoroscopeDayLog.get_day_horoscope_log(local_id, horoscope_type, 1),
        },
        'base_data': horoscope_static
    }

    return JsonResponse(ret)
