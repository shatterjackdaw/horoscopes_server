# coding:utf-8
import math
import re
import time
import urllib2
import datetime
from bs4 import BeautifulSoup
from auto_get_horoscopes_data import db, HoroscopeType, TableDb


HOST = 'http://horoscope.ohippo.com/zodiac-signs'


def get_date_time_href(sub_day, horoscope_t):
    date_str = get_date_time_str(sub_day)
    return '/' + str(horoscope_t) + '/daily-' + date_str


def get_date_time_str(sub_day):
    now_date = datetime.datetime.now()
    real_date = now_date + datetime.timedelta(days=sub_day)
    return real_date.strftime('%Y%m%d')


def create_horoscopes_data():
    for value in range(100,100):
        horoscopes_data, is_ok = get_horoscopes_data(value)
        save_horoscopes_data(horoscopes_data, TableDb.GENERAL)
        if not is_ok:
            print 'over up in ' + get_date_time_str(value)
            break
    for value in range(-95, -200, -1):
        horoscopes_data, is_ok = get_horoscopes_data(value)
        save_horoscopes_data(horoscopes_data, TableDb.GENERAL)
        if not is_ok:
            print 'over down in ' + get_date_time_str(value)
            break


def get_url_response(href, value=0):
    # 爬一波数据
    try:
        request = urllib2.Request(HOST + href)
        response = urllib2.urlopen(request, timeout=10)
        return response.read()
    except:
        if value > 10:
            print 'href>>' + str(href) + ', no chance..'
        print 'href>>' + str(href) + 'can not connect, retry!'
        time.sleep(1)
        return get_url_response(href, value + 1)


def get_horoscopes_data(day_value):
    print 'day_value>>>>>' + str(day_value)
    horoscopes_data = []
    for h_type in HoroscopeType.ALL:
        href = get_date_time_href(day_value, h_type)
        print 'href>>' + str(href)
        # 解析爬下来的数据
        response = get_url_response(href)
        # print 'get_horoscopes_data>>response>' + str(response)
        soup = BeautifulSoup(response, "html.parser")
        print 'parse data'
        try:
            target_content = soup.find_all(text=re.compile('zodiac_content'))[0]
            # print 'target_content>>' + target_content
            start_v = target_content.find('{')
            end_v = target_content.find(';')
            real_content = eval(target_content[start_v:end_v])
            print 'real_content>>' + str(real_content)
        except:
            return horoscopes_data, False
        for dict_data in real_content['data']:
            if dict_data.get('type') and dict_data['type'] == 'paragraph' and dict_data.get('text'):
                horoscopes_data.append({'content': dict_data['text'], 'key': h_type})
        time.sleep(1)
    print 'horoscopes_data>>>' + str(horoscopes_data)
    return horoscopes_data, True


def save_horoscopes_data(new_horoscopes_data, t_class):
    """
    存储各星座数据到mongo
    :param new_horoscopes_data:
    :param t_class:
    :return: {星座: _id}
    """
    db_table = db[t_class]
    for data in new_horoscopes_data:
        old_data = db_table.find_one({'content': data['content']})
        if not old_data:
            db_table.save({'content': data['content'], 'horoscope': data['key']})


if __name__ == '__main__':
    print 'create_horoscopes_data'
    create_horoscopes_data()
