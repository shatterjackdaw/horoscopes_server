# coding:utf-8
import time
import json
from django.shortcuts import render
from django.http import JsonResponse
from models import HoroscopeDayLog, HoroscopeType, HoroscopeWeekLog, HoroscopeMonthLog, HoroscopeYearLog, User, \
    get_compatibility_data_by_zodiac


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
            'weekly': HoroscopeWeekLog.get_week_horoscope_log(local_id, horoscope_type, 0),
            'monthly': HoroscopeMonthLog.get_month_horoscope_log(local_id, horoscope_type, 0),
            'yearly': HoroscopeYearLog.get_year_horoscope_log(local_id, horoscope_type, 0),
        },
        'base_data': horoscope_static
    }

    return JsonResponse(ret)


def info_regist(request):
    facebook_id = request.POST.get('facebook_id')
    device_id = request.POST.get('device_id')
    info = json.loads(request.POST.get('info', {}))
    if not facebook_id and not device_id:
        return JsonResponse({'status': 1, 'desc': 'facebook_id or device_id empty!'})
    birth = info.get('birth')
    avatar_url = info.get('avatar_url')
    is_auto = info.get('is_auto')
    data = {
        'birth': birth,
        'avatar_url': avatar_url,
        'is_auto': is_auto,
    }
    if facebook_id:
        data['facebook_id'] = str(facebook_id)
    if device_id:
        data['device_id'] = str(device_id)

    try:
        if facebook_id:
            user = User.find_one({'facebook_id': str(facebook_id)})
        else:
            user = User.find_one({'device_id': str(device_id), 'facebook_id': {'$exists': False}})

        if is_auto is True:
            data['auto_order'] = {'open': [int(time.time())], 'close': []}
        if user:
            user.update_instance({'$set': data})
        else:
            user = User(data)
            user.save()

        return JsonResponse({'status': 0})
    except:
        return JsonResponse({'status': 1, 'desc': 'save info error!'})


def info_login(request):
    facebook_id = request.POST.get('facebook_id')
    device_id = request.POST.get('device_id')
    user = None
    if facebook_id:
        user = User.find_one({'facebook_id': str(facebook_id)})
    elif device_id:
        user = User.find_one({'device_id': str(device_id), 'facebook_id': {'$exists': False}})
    if not user:
        return JsonResponse({'status': 1, 'desc': 'facebook_id or device_id error!'})

    data = user.to_client_obj()
    return JsonResponse({'status': 0, 'info': data})


def auto_order(request):
    facebook_id = request.POST.get('facebook_id')
    device_id = request.POST.get('device_id')
    user = None
    if facebook_id:
        user = User.find_one({'facebook_id': str(facebook_id)})
    elif device_id:
        user = User.find_one({'device_id': str(device_id), 'facebook_id': {'$exists': False}})
    if not user:
        return JsonResponse({'status': 1, 'desc': 'facebook_id or device_id error!'})

    is_auto = request.POST.get('is_auto')
    now_time = int(time.time())
    if is_auto is True:
        user.update_instance({'$addToSet': {"auto_order.open": now_time}, '$set': {'is_auto': True}})
    else:
        user.update_instance({'$addToSet': {"auto_order.close": now_time}, '$set': {'is_auto': False}})

    return JsonResponse({'status': 0})


def get_compatibility_data(request):
    zodiac_man = request.GET.get('zodiac_man')
    zodiac_woman = request.GET.get('zodiac_woman')
    if not zodiac_man or not zodiac_woman or zodiac_man not in HoroscopeType.ALL or zodiac_woman not in HoroscopeType.ALL:
        return JsonResponse({'status': 1, 'desc': 'horoscope error!'})

    data = get_compatibility_data_by_zodiac(zodiac_man, zodiac_woman)
    ret = {
        'status': 0,
        'compatibility': data
    }

    return JsonResponse(ret)
