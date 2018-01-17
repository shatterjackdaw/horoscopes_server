# coding: utf-8
import random
import datetime
from django.conf import settings
from mongothon import Schema, create_model


db_horoscopes = settings.HOROSCOPES_DB


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

HoroscopeDayLog = create_model(horoscope_day_log_schema, db_horoscopes.horoscope_day_log, "HoroscopeDayLog")
HoroscopeDayLog.collection.ensure_index("date")


horoscope_week_log_schema = Schema({
    "date": {'type': basestring},       # %Y-%U 2018-00, 具体规则参见datetime.strftime()
    'horoscope_type': {'type': basestring, 'default': HoroscopeType.ARIES},
    'content': {'type': dict, 'default': {}},
})

HoroscopeWeekLog = create_model(horoscope_week_log_schema, db_horoscopes.horoscope_week_log, "HoroscopeWeekLog")
HoroscopeWeekLog.collection.ensure_index([("date", -1), ('horoscope_type', -1)])


horoscope_month_log_schema = Schema({
    "date": {'type': basestring},       # %Y-%m 2018-01
    'horoscope_type': {'type': basestring, 'default': HoroscopeType.ARIES},
    'content': {'type': dict, 'default': {}},
})

HoroscopeMonthLog = create_model(horoscope_month_log_schema, db_horoscopes.horoscope_month_log, "HoroscopeMonthLog")
HoroscopeMonthLog.collection.ensure_index([("date", -1), ('horoscope_type', -1)])


horoscope_year_log_schema = Schema({
    "date": {'type': basestring},       # %Y 2018
    'horoscope_type': {'type': basestring, 'default': HoroscopeType.ARIES},
    'content': {'type': dict, 'default': {}},
})

HoroscopeYearLog = create_model(horoscope_year_log_schema, db_horoscopes.horoscope_year_log, "HoroscopeYearLog")
HoroscopeYearLog.collection.ensure_index([("date", -1), ('horoscope_type', -1)])


@HoroscopeDayLog.static_method
def get_day_horoscope_log(local_id, horoscope_type, day_offset=0):
    if local_id > 8:
        local_id = 8
    now = datetime.datetime.now() + datetime.timedelta(hours=local_id-8) + datetime.timedelta(days=day_offset)
    the_day = datetime.datetime(now.year, now.month, now.day)
    day_log = HoroscopeDayLog.find_one({'date': the_day, 'horoscope_type': horoscope_type})
    if not day_log:
        # day_log = HoroscopeDayLog.create_new_horoscope_day_log()
        return {}
    if day_log.get('color') and day_log.get('gem') and day_log.get('lucky_nums'):
        return day_log.to_client_obj()
    if day_log.get('color') is None:
        day_log['color'] = random.choice(settings.STATIC['color'].keys())
    if day_log.get('gem') is None:
        day_log['gem'] = random.choice(settings.STATIC['gem'].keys())
    if day_log.get('lucky_nums') is None:
        day_log['lucky_nums'] = random.sample(range(10), 3)
    day_log.save()

    return day_log.to_client_obj()


@HoroscopeDayLog.static_method
def create_new_horoscope_day_log(date, horoscope_type):
    day_log = HoroscopeDayLog()
    day_log['date'] = date
    day_log['horoscope_type'] = horoscope_type
    r_value = get_random_horoscopes_value()
    day_log['rating'] = r_value['rating']
    day_log['matches'] = r_value['matches']
    # TODO: 未完
    day_log.save()

    return day_log


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


@HoroscopeDayLog.instance_method
def to_client_obj(self):
    data = dict(self)
    del data['_id']
    data[TableDb.GENERAL] = data[TableDb.GENERAL].values()[0].encode('utf-8')
    data[TableDb.LOVE] = data[TableDb.LOVE].values()[0].encode('utf-8')
    data[TableDb.MONEY] = data[TableDb.MONEY].values()[0].encode('utf-8')
    data[TableDb.CAREER] = data[TableDb.CAREER].values()[0].encode('utf-8')
    data[TableDb.ADVANCE] = data[TableDb.ADVANCE].values()[0].encode('utf-8')

    data['date'] = data['date'].strftime('%Y%m%d')
    data['color'] = settings.STATIC['color'][data['color']]
    data['gem'] = settings.STATIC['gem'][data['gem']]

    return data


@HoroscopeDayLog.static_method
def get_static_horoscope_data(horoscope_type):
    static = settings.STATIC['zodiac']
    data = static.get(horoscope_type, {})
    return data
