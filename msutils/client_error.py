# -*- coding:utf-8 -*-
class ClientErrorCode(object):
    UNKNOWN = 1
    CLIENT_NOT_LOGIN = 2
    INVALID_USER_ID = 3
    USER_NOT_EXIST = 4
    WRONG_PASSWORD = 5
    MOMO_LOGIN_FAIL = 6
    REG_FIND_NEW_POS_FAILED = 7
    THIRD_PLATFORM_LOGIN_FAIL = 8
    HM_LOGIN_FAIL = 9
    PLAYER_FROZEN = 10
    ZSY_LOGIN_FAIL = 11
    QIHUU_360_LOGIN_FAIL = 12
    EMAIL_SEND_OK = 13
    EMAIL_INVALID_FMT = 14
    EMAIL_SEND_FAIL = 15
    VIVO_LOGIN_FAIL = 16
    ANQU_LOGIN_FAIL = 17
    LONGYUAN_LOGIN_FAIL = 18
    ZEROSEVENTHREE_LOGIN_FAIL = 19
    XSEVENSY_LOGIN_FAIL = 20
    LEHIHI_LOGIN_FAIL = 21
    TTYUYIN_LOGIN_FAIL = 22
    AIYINGYONG_LOGIN_FAIL = 23
    XUNLONG_LOGIN_FAIL = 24
    HANFENG_LOGIN_FAIL = 25
    CHUANGXING_LOGIN_FAIL = 26
    JINGSHI_LOGIN_FAIL = 27
    HUOSU_LOGIN_FAIL = 28

    # payment 200x
    PAYMENT_EXIST = 2001
    PAYMENT_GOOGLE_PAYMENT_CHECK_FAIL = 2002
    PAYMENT_CHECK_FAILED = 2003

    #account 240x
    ACCOUNT_ALREADY_BOUND = 2400
    USER_ALREADY_BOUND = 2401

    # redeem
    GET_REDEEM_FAIL = 2900
    INVALID_REDEEM_CODE = 2901
    ALREADY_GET_REDEEM_AWARD = 2902
    ALREADY_USED_UP_REDEEM = 2903


class ClientError(Exception):
    def __init__(self, code=0, params=None, *args, **kwargs):
        self.code = code
        self.params = params
        Exception.__init__(self, *args, **kwargs)

    def __str__(self):
        return self.__repr__()
