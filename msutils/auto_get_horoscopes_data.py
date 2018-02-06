# coding:utf-8
import math
import time
import urllib2
import datetime
import random
import traceback
from bs4 import BeautifulSoup, Tag
from pymongo import MongoClient
from mongothon import Schema, create_model
from email.mime.text import MIMEText
import smtplib


class HoroscopeType:
    def __init__(self):
        pass

    ARIES = 'aries'                 # 白羊座
    TAURUS = 'taurus'               # 金牛座
    GEMINI = 'gemini'               # 双子座
    CANCER = 'cancer'               # 巨蟹座
    LEO = 'leo'                     # 狮子座
    VIRGO = 'virgo'                 # 处女座
    LIBRA = 'libra'                 # 天秤座
    SCORPIO = 'scorpio'             # 天蝎座
    SAGITTARIUS = 'sagittarius'     # 射手座
    CAPRICORN = 'capricorn'         # 摩羯座
    AQUARIUS = 'aquarius'           # 水瓶座
    PISCES = 'pisces'               # 双鱼座

    ALL = [ARIES, TAURUS, GEMINI, CANCER, LEO, VIRGO, LIBRA, SCORPIO, SAGITTARIUS, CAPRICORN, AQUARIUS, PISCES]


class TableDb:
    def __init__(self):
        pass

    GENERAL = "general"
    LOVE = "love"
    MONEY = "money"
    CAREER = "career"
    ADVANCE = "advance"
    HEALTH = "health"

    ALL = [GENERAL, LOVE, MONEY, CAREER, ADVANCE, HEALTH]

    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    YEARLY = 'yearly'


class Rating:
    def __init__(self):
        pass

    OVERALL = 'overall'
    LOVE = 'love'
    CAREER = 'career'
    MONEY = 'money'
    HEALTH = 'health'


class Matches:
    def __init__(self):
        pass

    FRIENDSHIP = 'friendship'
    LOVE = 'love'
    CAREER = 'career'

MONGO_CONFIG = {
    'CONN_ADDR1': '127.0.0.1:27017',

    # 'username': 'root',
    # 'password': 'youputao2012',
    # 数据库名字，可能需要修改
    'database': 'horoscopes_db',
    'bi_db': 'easy_log',  # 貌似已经废弃了
}


def get_mongo_conf(conf=None):
    _conf = conf or MONGO_CONFIG
    _h1, _h2 = _conf.get('CONN_ADDR1'), _conf.get('CONN_ADDR2')
    _mg_user, _mg_pass = _conf.get('username'), _conf.get('password')

    _host_list = []
    if _h1:
        _host_list.append(_h1)
    if _h2:
        _host_list.append(_h2)

    if _host_list:
        mongo = MongoClient(_host_list, replicaSet=_conf.get('REPLICAT_SET'))
        if _mg_user and _mg_pass:
            mongo.admin.authenticate(_mg_user, _mg_pass)
    else:
        mongo = MongoClient('127.0.0.1', 27017, connect=False, socketKeepAlive=True)
    return mongo

db = get_mongo_conf()[MONGO_CONFIG['database']]


horoscope_day_log_schema = Schema({
    "date": {'type': datetime.datetime},
    'horoscope_type': {'type': basestring, 'default': HoroscopeType.ARIES},
    'color': {'type': int},
    'gem': {'type': int},
    'lucky_nums': {'type': list},
    TableDb.GENERAL: {'type': dict, 'default': {}},
    TableDb.LOVE: {'type': dict, 'default': {}},
    TableDb.MONEY: {'type': dict, 'default': {}},
    TableDb.CAREER: {'type': dict, 'default': {}},
    TableDb.ADVANCE: {'type': dict, 'default': {}},
    TableDb.HEALTH: {'type': dict, 'default': {}},
    'rating': {
        'type': Schema({
            Rating.OVERALL: {'type': int},
            Rating.LOVE: {'type': int},
            Rating.CAREER: {'type': int},
            Rating.MONEY: {'type': int},
            Rating.HEALTH: {'type': int},
        }), 'default': {
            Rating.OVERALL: 0,
            Rating.LOVE: 0,
            Rating.CAREER: 0,
            Rating.MONEY: 0,
            Rating.HEALTH: 0
        }
    },
    'matches': {
        'type': Schema({
            Matches.FRIENDSHIP: {'type': basestring},
            Matches.LOVE: {'type': basestring},
            Matches.CAREER: {'type': basestring}
        }), 'default': {
            Matches.FRIENDSHIP: HoroscopeType.ARIES,
            Matches.LOVE: HoroscopeType.ARIES,
            Matches.CAREER: HoroscopeType.ARIES
        }
    }
})

HoroscopeDayLog = create_model(horoscope_day_log_schema, db.horoscope_day_log, "HoroscopeDayLog")
HoroscopeDayLog.collection.ensure_index([("date", -1), ('horoscope_type', -1)])


horoscope_week_log_schema = Schema({
    "date": {'type': basestring},       # %Y-%U 2018-00, 具体规则参见datetime.strftime()
    'horoscope_type': {'type': basestring, 'default': HoroscopeType.ARIES},
    TableDb.GENERAL: {'type': dict, 'default': {}},
    'rating': {
        'type': Schema({
            Rating.OVERALL: {'type': int},
            Rating.LOVE: {'type': int},
            Rating.CAREER: {'type': int},
            Rating.MONEY: {'type': int},
            Rating.HEALTH: {'type': int},
        }), 'default': {
            Rating.OVERALL: 0,
            Rating.LOVE: 0,
            Rating.CAREER: 0,
            Rating.MONEY: 0,
            Rating.HEALTH: 0
        }
    },
})

HoroscopeWeekLog = create_model(horoscope_week_log_schema, db.horoscope_week_log, "HoroscopeWeekLog")
HoroscopeWeekLog.collection.ensure_index([("date", -1), ('horoscope_type', -1)])


horoscope_month_log_schema = Schema({
    "date": {'type': basestring},       # %Y-%m 2018-01
    'horoscope_type': {'type': basestring, 'default': HoroscopeType.ARIES},
    'color': {'type': int},
    'gem': {'type': int},
    'lucky_nums': {'type': list},
    TableDb.GENERAL: {'type': dict, 'default': {}},
    'rating': {
        'type': Schema({
            Rating.OVERALL: {'type': int},
            Rating.LOVE: {'type': int},
            Rating.CAREER: {'type': int},
            Rating.MONEY: {'type': int},
            Rating.HEALTH: {'type': int},
        }), 'default': {
            Rating.OVERALL: 0,
            Rating.LOVE: 0,
            Rating.CAREER: 0,
            Rating.MONEY: 0,
            Rating.HEALTH: 0
        }
    },
    'matches': {
        'type': Schema({
            Matches.FRIENDSHIP: {'type': basestring},
            Matches.LOVE: {'type': basestring},
            Matches.CAREER: {'type': basestring}
        }), 'default': {
            Matches.FRIENDSHIP: HoroscopeType.ARIES,
            Matches.LOVE: HoroscopeType.ARIES,
            Matches.CAREER: HoroscopeType.ARIES
        }
    }
})

HoroscopeMonthLog = create_model(horoscope_month_log_schema, db.horoscope_month_log, "HoroscopeMonthLog")
HoroscopeMonthLog.collection.ensure_index([("date", -1), ('horoscope_type', -1)])


horoscope_year_log_schema = Schema({
    "date": {'type': basestring},       # %Y 2018
    'horoscope_type': {'type': basestring, 'default': HoroscopeType.ARIES},
    TableDb.GENERAL: {'type': dict, 'default': {}},
    'rating': {
        'type': Schema({
            Rating.OVERALL: {'type': int},
        }), 'default': {
            Rating.OVERALL: 0,
        }
    },
})

HoroscopeYearLog = create_model(horoscope_year_log_schema, db.horoscope_year_log, "HoroscopeYearLog")
HoroscopeYearLog.collection.ensure_index([("date", -1), ('horoscope_type', -1)])


# -----------------------auto-----------------------------
def auto_get_horoscopes_data():
    create_horoscopes_data()
    create_astrologyprime_horoscopes_data()
    create_horoscopes_other_all_data()
    create_findyourfate_horoscopes_data()
    create_theastrologer_horoscopes_data()
    print datetime.datetime.now()
    send_mail(['xingchen@mobile-mafia.com'], datetime.datetime.now().strftime('%m月%d日%Y年，星座数据正常'), '蛮正常的')


# ----------theastrologer----------
def create_theastrologer_horoscopes_data():
    print '>>>>>>>create_theastrologer_horoscopes_data'
    # https://www.theastrologer.com/horoscope
    host = 'https://new.theastrologer.com'
    time_keys = {'daily': '/daily-horoscope/', 'weekly': '/weekly-horoscope/', 'monthly': '/monthly-horoscope/'}
    horoscopes_data = {'daily': [], 'weekly': [], 'monthly': [], 'yearly': []}

    for key, t_type in time_keys.iteritems():
        print key
        if key == 'monthly':
            data = get_theastrologer_monthly_horoscopes_data(host + t_type)
        else:
            data = get_theastrologer_horoscopes_data(host + t_type)
        if not data:
            continue
        horoscopes_data[key] = data
    save_horoscopes_data(horoscopes_data['daily'], TableDb.GENERAL)
    weekly_data = save_horoscopes_data(horoscopes_data['weekly'], TableDb.WEEKLY)
    save_horoscopes_noday_log(weekly_data, TableDb.WEEKLY)
    monthly_data = save_horoscopes_data(horoscopes_data['monthly'], TableDb.MONTHLY)
    save_horoscopes_noday_log(monthly_data, TableDb.MONTHLY)
    # 年的，每年跑一次就行了。。
    # y_data = get_theastrologer_yearly_horoscopes_data(host + '/2018-horoscope/')
    # horoscopes_data['yearly'] = y_data
    # yearly_data = save_yearly_horoscopes_data(horoscopes_data['yearly'], TableDb.YEARLY)
    # save_horoscopes_noday_log(yearly_data, TableDb.YEARLY)


def get_theastrologer_horoscopes_data(href):
    # 日周月型 解析爬下来的数据
    response = get_url_response(href)
    if not response:
        return ''
    horoscopes_data = []
    soup = BeautifulSoup(response, "html.parser")
    for s in soup.find_all(is_h2_no_id):
        new_text = ''
        horoscope_t = s['id']
        for cont in s.parent.contents:
            if cont.string is not None:
                new_text += cont.string
        horoscopes_data.append({'key': horoscope_t.lower(), 'content': new_text.strip()})
    print 'horoscopes_data>>' + str(horoscopes_data)
    return horoscopes_data


def get_theastrologer_monthly_horoscopes_data(href):
    # 年型 解析爬下来的数据
    response = get_url_response(href)
    if not response:
        return ''
    horoscopes_data = []
    soup = BeautifulSoup(response, "html.parser")
    for s in soup.find_all(is_h2_no_id):
        new_text = ''
        horoscope_t = ''
        for cont in s.parent.contents:
            if type(cont) == Tag:
                if cont.name == 'h2':
                    horoscope_t = cont['id']
                elif cont.name == 'p':
                    if new_text:
                        new_text += '\n\n'
                    for p_cont in cont.contents:
                        new_text += p_cont.string
        horoscopes_data.append({'key': horoscope_t.lower(), 'content': new_text.strip()})
    print 'horoscopes_data>>' + str(horoscopes_data)
    return horoscopes_data


def get_theastrologer_yearly_horoscopes_data(href):
    # 年型 解析爬下来的数据
    response = get_url_response(href)
    if not response:
        return ''
    horoscopes_data = []
    soup = BeautifulSoup(response, "html.parser")
    for s in soup.find_all(is_h2_no_id):
        new_text = ''
        horoscope_t = ''
        class_t = ''
        for cont in s.parent.contents:
            if type(cont) == Tag:
                print cont.name
                if cont.name == 'h2':
                    horoscope_t = cont['id']
                elif cont.name == 'h3':
                    if class_t and new_text:
                        horoscopes_data.append({'key': horoscope_t.lower(), 'content': new_text.strip(),
                                                'class_type': class_t.lower()})
                    new_text = ''
                    class_t = cont.string.strip()
                    class_t = class_t if class_t != 'Overview' else 'general'
                elif cont.name == 'p':
                    if new_text:
                        new_text += '\n\n'
                    for p_cont in cont.contents:
                        new_text += p_cont.string
                print 'new_text>>>>'
                print new_text
        if class_t and new_text:
            horoscopes_data.append({'key': horoscope_t.lower(), 'content': new_text.strip(),
                                    'class_type': class_t.lower()})
    print 'horoscopes_data>>' + str(horoscopes_data)
    return horoscopes_data


def is_h2_no_id(tag):
    return tag.name == 'h2' and tag.has_attr('id')


def is_h3_no_id(tag):
    return tag.name == 'h3' and tag.string == 'Overview'
# --------------------


# ----------findyourfate----------
def create_findyourfate_horoscopes_data():
    print '>>>>>>>create_findyourfate_horoscopes_data'
    # https://www.findyourfate.com/horoscope
    host = 'http://www.findyourfate.com/rss/%s.php?sign=%s&id=45'
    horoscope_keys = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo']
    horoscope_keys2 = ['Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    time_keys = {'daily': 'dailyhoroscope-feed', 'weekly': 'weekly-horoscope', 'monthly': 'monthly-horoscope'}
    horoscopes_data = {'daily': [], 'weekly': [], 'monthly': []}

    for h_type in horoscope_keys:
        for key, t_type in time_keys.iteritems():
            h_content = get_findyourfate_horoscopes_data(host % (t_type, h_type))
            if not h_content:
                continue
            horoscopes_data[key].append({'key': h_type.lower(), 'content': h_content})

    time.sleep(120)
    # 连续请求到Libra，后面就会一直请求不成功。等一会就好。
    for h_type in horoscope_keys2:
        for key, t_type in time_keys.iteritems():
            h_content = get_findyourfate_horoscopes_data(host % (t_type, h_type))
            if not h_content:
                continue
            horoscopes_data[key].append({'key': h_type.lower(), 'content': h_content})

    save_horoscopes_data(horoscopes_data['daily'], TableDb.GENERAL)
    save_horoscopes_data(horoscopes_data['weekly'], TableDb.WEEKLY)
    save_horoscopes_data(horoscopes_data['monthly'], TableDb.MONTHLY)


def get_findyourfate_horoscopes_data(href):
    # 解析爬下来的数据
    response = get_url_response(href)
    if not response:
        return ''
    soup = BeautifulSoup(response, "html.parser")
    h_content = soup.item.description.string.strip()
    print 'h_content>>' + str(h_content)
    return h_content
# --------------------


# ----------astrologyprime----------
def create_astrologyprime_horoscopes_data():
    print '>>>>>>>create_astrologyprime_horoscopes_data'
    # https://www.astrologyprime.com/horoscope
    host = 'https://www.astrologyprime.com/horoscope/'
    horoscopes_data = []
    for h_type in HoroscopeType.ALL:
        horoscopes_data += get_astrologyprime_horoscopes_data(host + h_type, h_type)

    save_horoscopes_data(horoscopes_data, TableDb.GENERAL)


def get_astrologyprime_horoscopes_data(href, horoscope_t):
    # 解析爬下来的数据
    horoscopes_data = []
    response = get_url_response(href)
    if not response:
        return horoscopes_data
    soup = BeautifulSoup(response, "html.parser")
    # for span_h in soup.select('span[class=tooltiptext]'):     # 昨今明都有
    for span_h in soup.select('div[id="tomorrow"] > div > span'):   # 只有明天
        h_content = span_h.string.strip()
        horoscopes_data.append({'key': horoscope_t, 'content': h_content})
        h_content = span_h.string.strip()
        horoscopes_data.append({'key': horoscope_t, 'content': h_content})
    print 'horoscopes_data>>' + str(horoscopes_data)
    return horoscopes_data
# --------------------


# ----------horoscopeservices----------
def create_horoscopes_data():
    print '>>>>>>>create_horoscopes_data'
    # http://www.horoscopeservices.co.uk
    host = 'http://www.horoscopeservices.co.uk'
    href_list = {
        TableDb.GENERAL: "/daily-horoscopes/b1-daily-horoscopes.asp",
        TableDb.LOVE: "/daily-horoscopes/c1-daily-love-horoscopes.asp",
        TableDb.MONEY: "/daily-horoscopes/d1-daily-money-horoscopes.asp",
        TableDb.CAREER: "/daily-horoscopes/e1-daily-career-horoscopes.asp",
        TableDb.ADVANCE: "/daily-horoscopes/F1-daily-horoscope.asp",
        TableDb.HEALTH: "/daily-horoscopes/UHF-english-health-and-fitness-horoscopes.asp"
    }
    new_ids_data = {}
    for key, href in href_list.iteritems():
        horoscopes_data = get_horoscopes_daily_data(host + href)
        new_ids_data[key] = save_horoscopes_data(horoscopes_data, key)
    print 'new_ids_data>>>' + str(new_ids_data)
    save_after_tomorrow_horoscopes_day_log(new_ids_data)


def get_horoscopes_daily_data(href):
    # 解析爬下来的数据
    horoscopes_data = []
    response = get_url_response(href)
    if not response:
        return horoscopes_data
    # print 'get_horoscopes_data>>response>' + str(response)
    soup = BeautifulSoup(response, "html.parser")
    for h4 in soup.find_all('h4'):
        key = h4.string.strip().lower()
        h_content = h4.next_sibling.next_sibling.string.strip()
        horoscopes_data.append({'key': key, 'content': h_content})
    print 'horoscopes_data>>' + str(horoscopes_data)
    return horoscopes_data


def create_horoscopes_other_all_data():
    print '>>>>>>>create_horoscopes_other_all_data'
    # http://www.horoscopeservices.co.uk
    host = 'http://www.horoscopeservices.co.uk'
    href_list_data = get_horoscopes_all_href(host + '/daily-horoscopes')
    for href_data in href_list_data:
        print 'href_data>>>' + str(href_data)
        horoscopes_data = get_horoscopes_other_all_data(href_data, host)
        save_horoscopes_other_all_data(horoscopes_data)


def get_horoscopes_all_href(href):
    # 解析爬下来的数据
    horoscope_data_list = []
    response = get_url_response(href)
    if not response:
        return horoscope_data_list
    soup = BeautifulSoup(response, "html.parser")
    for data in soup.select('div .feed-row-description'):
        if not isinstance(data.next_sibling.next_sibling.next_element, Tag):
            continue
        print data.next_sibling.next_sibling.next_element['href']
        title_str = data.string.strip()
        href_str = data.next_sibling.next_sibling.next_element.get('href')
        if not href_str:
            print href_str
            continue
        if href_str[0] != '/':
            href_str = '/daily-horoscopes/' + href_str
        horoscope_data = {'href': href_str, 'language_type': 'None'}
        if 'Chinese Daily Horoscopes' in title_str:
            horoscope_data['time_type'] = 'Daily'
            horoscope_data['class_type'] = 'Chinese Daily'
        elif 'SMS' in title_str:
            horoscope_data['language_type'] = title_str[:title_str.find('SMS')].strip()
            t_type_str = title_str.split('Daily')[1]
            type_str = t_type_str[:t_type_str.find('Horoscope')].strip().lower()
            horoscope_data['time_type'] = 'Daily'
            horoscope_data['class_type'] = type_str
        elif 'Yearly' in title_str:
            horoscope_data['time_type'] = 'yearly'
            horoscope_data['class_type'] = 'All'
        elif 'Daily' in title_str:
            horoscope_data['class_type'], horoscope_data['language_type'] = get_time_span_href_data(title_str, 'Daily')
            horoscope_data['time_type'] = 'Daily'
        elif 'Weekly' in title_str:
            horoscope_data['class_type'], horoscope_data['language_type'] = get_time_span_href_data(title_str, 'Weekly')
            horoscope_data['time_type'] = 'Weekly'
        elif 'Monthly' in title_str:
            horoscope_data['class_type'], horoscope_data['language_type'] = get_time_span_href_data(title_str, 'Monthly')
            horoscope_data['time_type'] = 'Monthly'
        horoscope_data_list.append(horoscope_data)
    return horoscope_data_list


def get_time_span_href_data(title_str, time_type):
    title_1, title_2 = title_str.split(time_type)
    title_1, title_2 = title_1.strip(), title_2.strip()
    language_type = 'None'
    if title_1:
        language_type = title_1
    if 'Horoscope' in title_2:
        class_type = title_2[:title_2.find('Horoscope')].strip()
    else:
        class_type = title_2.strip()
    if not class_type:
        class_type = 'abstract'
    return class_type, language_type


def get_horoscopes_other_all_data(href_data, host):
    # 解析爬下来的数据
    horoscopes_data = []
    response = get_url_response(host + href_data['href'])
    if not response:
        return horoscopes_data
    soup = BeautifulSoup(response, "html.parser")
    if href_data['class_type'] == 'All':
        for h4 in soup.find_all('h4'):
            print h4.next_sibling.encode('utf-8')
            key = h4.string.strip().lower()
            h_content = h4.next_sibling.string.strip()
            horoscopes_data.append({'class_type': key, 'content': h_content, 'time_type': href_data['time_type'],
                                    'language_type': href_data['language_type']})
    else:
        for h4 in soup.find_all('h4'):
            if not h4.string or not h4.next_sibling.next_sibling.string:
                continue
            key = h4.string.strip().lower()
            h_content = h4.next_sibling.next_sibling.string.strip()
            horoscopes_data.append({'horoscope': key, 'content': h_content, 'time_type': href_data['time_type'],
                                    'language_type': href_data['language_type'], 'class_type': href_data['class_type']})
    print 'horoscopes_data>>' + str(horoscopes_data)
    return horoscopes_data
# --------------------
# -----------------------auto-----------------------------


def get_url_response(href):
    # 爬一波数据
    try:
        request = urllib2.Request(href)
        response = urllib2.urlopen(request, timeout=10)
        return response.read()
    except:
        print traceback.format_exc()
        print 'retry>>>'
        try:
            request = urllib2.Request(href)
            response = urllib2.urlopen(request, timeout=30)
            return response.read()
        except:
            print 'failure>href>'
            print href
            return ''


def save_after_tomorrow_horoscopes_day_log(horoscopes_data):
    # 把新数据存成后天的时间
    date_time = get_after_tomorrow_date()
    print 'save after tomorrow date_time>>' + str(date_time)
    ids_total_dict = {}
    for h_type in HoroscopeType.ALL:
        if HoroscopeDayLog.find_one({'date': date_time, 'horoscope_type': h_type}):
            continue
        new_day_log = HoroscopeDayLog({'date': date_time, 'horoscope_type': h_type})
        for t_class in TableDb.ALL:
            if horoscopes_data.get(t_class):
                new_day_log[t_class] = horoscopes_data[t_class][h_type]
                ids_total_dict.setdefault(t_class, [])
                ids_total_dict[t_class].append(horoscopes_data[t_class][h_type])
        r_data = get_random_horoscopes_value()
        new_day_log['rating'] = r_data['rating']
        new_day_log['matches'] = r_data['matches']
        new_day_log['lucky_nums'] = random.sample(range(10), 3)
        new_day_log.save()

    last_time = math.floor(time.time()) + 24*3600*2
    for t_class in TableDb.ALL:
        if not ids_total_dict.get(t_class):
            continue
        db_table = db[t_class]
        db_table.update_many({'_id': {'$in': ids_total_dict[t_class]}}, {'$set': {'last_time': last_time}})


def save_horoscopes_noday_log(horoscopes_data, time_k):
    # 存下周log
    time_data = {TableDb.WEEKLY: ['%Y-%U', HoroscopeWeekLog], TableDb.MONTHLY: ['%Y-%m', HoroscopeMonthLog],
                 TableDb.YEARLY: ['%Y', HoroscopeYearLog]}
    time_conf = time_data[time_k]
    now_date = datetime.datetime.now()
    date_time = now_date.strftime(time_conf[0])
    # b_date = (now_date + datetime.timedelta(days=-1)).strftime('%Y-%U')
    print 'save today noday date_time>>' + str(date_time)
    for h_type in HoroscopeType.ALL:
        new_noday_log = time_conf[1].find_one({'date': date_time, 'horoscope_type': h_type})
        if new_noday_log:
            continue
        new_noday_log = time_conf[1]({'date': date_time, 'horoscope_type': h_type,
                                      TableDb.GENERAL: horoscopes_data[h_type]})
        r_data = get_random_horoscopes_value()
        new_noday_log['rating'] = r_data['rating']
        if time_k == TableDb.YEARLY:
            new_noday_log['rating'] = {Rating.OVERALL: r_data['rating'][Rating.OVERALL]}
        elif time_k == TableDb.MONTHLY:
            new_noday_log['lucky_nums'] = random.sample(range(10), 3)
            new_noday_log['matches'] = r_data['matches']
        new_noday_log.save()


def save_horoscopes_data(new_horoscopes_data, t_class):
    """
    存储各星座数据到mongo
    :param new_horoscopes_data:
    :param t_class:
    :return: {星座: _id}
    """
    db_table = db[t_class]
    day_data = {}
    for data in new_horoscopes_data:
        old_data = db_table.find_one({'content': data['content']})
        if old_data:
            print 'normal content repeat >> t_class:' + str(t_class) + ', horoscope>>' + str(data.get('key', ''))
            data_id = old_data['_id']
        else:
            print 'normal no repeat>>>>>>>'
            data_id = db_table.save({'content': data['content'], 'horoscope': data['key'],
                                     'add_time': math.floor(time.time())})
        print data
        day_data[data['key']] = {str(data_id): data['content']}
    return day_data


def save_yearly_horoscopes_data(new_horoscopes_data, t_class):
    """
    存储年的各星座数据到mongo
    :param new_horoscopes_data:
    :param t_class:
    :return: {星座: _id}
    """
    db_table = db[t_class]
    day_data = {}
    for data in new_horoscopes_data:
        old_data = db_table.find_one({'content': data['content']})
        if old_data:
            print 'content repeat >> t_class:' + str(t_class) + ', horoscope>>' + str(data.get('key', ''))
            data_id = old_data['_id']
        else:
            print 'no repeat>>>>>>>'
            ret = {'content': data['content'], 'horoscope': data['key'], 'class_type': data['class_type'],
                   'add_time': math.floor(time.time())}
            if data['class_type'] == 'general':
                ret['is_current'] = True
            data_id = db_table.save(ret)
        print data
        day_data[data['key']] = {str(data_id): data['content']}
    return day_data


def save_horoscopes_other_all_data(new_horoscopes_data):
    """
    存储其他的全部星座数据到mongo
    :param new_horoscopes_data:
    :return: {星座: _id}
    """
    db_table = db.horoscopes_other_all
    for data in new_horoscopes_data:
        if not data.get('content'):
            continue
        old_data = db_table.find_one({'content': data['content']})
        if old_data:
            print 'content repeat >> '
        else:
            print 'no repeat>>>>>>>'
            data['add_time'] = math.floor(time.time())
            db_table.save(data)
        print data


def get_after_tomorrow_date():
    # 后天的时间
    now_date = datetime.datetime.now()
    tomorrow_date = now_date + datetime.timedelta(days=2)
    return datetime.datetime(tomorrow_date.year, tomorrow_date.month, tomorrow_date.day)


def update_all_horoscopes_data():
    all_horoscopes = HoroscopeDayLog.find()
    for horoscope_obj in all_horoscopes:
        print 'horoscope_obj>>>' + str(dict(horoscope_obj))
        # for db_key in TableDb.ALL:
        #     if db_key == TableDb.HEALTH:
        #         continue
        #     print 'list>>'
        #     print horoscope_obj[db_key]
        #     table_id = horoscope_obj[db_key][0]
        #     data = db[db_key].find_one({'_id': table_id})
        #     horoscope_obj[db_key] = {str(table_id): data['content']}
        #     print data['content']
        # print 'horoscope_obj>>>' + str(dict(horoscope_obj))
        r_data = get_random_horoscopes_value()
        horoscope_obj['rating'] = r_data['rating']
        horoscope_obj['matches'] = r_data['matches']
        horoscope_obj.save()


def get_random_horoscopes_value():
    rating_list = [25, 30, 35, 40, 45, 50]
    data = {'rating': {
                Rating.OVERALL: random.choice(rating_list),
                Rating.LOVE: random.choice(rating_list),
                Rating.CAREER: random.choice(rating_list),
                Rating.MONEY: random.choice(rating_list),
                Rating.HEALTH: random.choice(rating_list)
            },
            'matches': {
                Matches.FRIENDSHIP: random.choice(HoroscopeType.ALL),
                Matches.LOVE: random.choice(HoroscopeType.ALL),
                Matches.CAREER: random.choice(HoroscopeType.ALL)
            }
    }
    return data


def send_mail(to_list, sub, content):
    mail_host = "smtp.exmail.qq.com"  # 设置服务器
    mail_user = "sys_op@mobile-mafia.com"  # 用户名
    mail_pass = "Youputao2012"  # 口令
    mail_postfix = "mobile-mafia.com"  # 发件箱的后缀

    msg = MIMEText(content, _subtype='plain', _charset='utf-8')
    msg['Subject'] = sub
    msg['From'] = mail_user
    msg['To'] = ";".join(to_list)
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user,mail_pass)
        server.sendmail(mail_user, to_list, msg.as_string())
        server.close()
        return True
    except Exception, e:
        print str(e)
        return False


if __name__ == '__main__':
    auto_get_horoscopes_data()
