# -*- coding:utf-8 -*-
from Crypto.Cipher import AES
import time
import json
import base64

current_second = lambda: int(round(time.time()))

key = '0123456789abcdef'
mode = AES.MODE_ECB

class enc_tool():
    def __init__(self):
        self.mode = AES.MODE_ECB
        self.key = key

    #加密函数，如果text不足16位就用空格补足为16位，
    #如果大于16当时不是16的倍数，那就补足为16的倍数。
    def encrypt(self,text):
        cryptor = AES.new(self.key,self.mode)
        #这里密钥key 长度必须为16（AES-128）,
        #24（AES-192）,或者32 （AES-256）Bytes 长度
        #目前AES-128 足够目前使用
        length = 16
        count = len(text)
        if count < length:
            add = (length-count)
            #\0 backspace
            text = text + ('\0' * add)
        elif count > length:
            add = (length-(count % length))
            text = text + ('\0' * add)
        self.ciphertext = cryptor.encrypt(text)
        #因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        #所以这里统一把加密后的字符串转化为16进制字符串
        return self.ciphertext

    #解密后，去掉补足的空格用strip() 去掉
    def decrypt(self,text):
        cryptor = AES.new(self.key,self.mode)
        plain_text  = cryptor.decrypt(text)
        return plain_text.rstrip('\0')

crypt = enc_tool()

def encrypt_user_token(user_id):
    plain_text = json.dumps({'user_id':str(user_id),'time':current_second()})
    encrypted_text = crypt.encrypt(plain_text)
    return base64.b64encode(encrypted_text)

def decrypt_user_token(encrypted_user_token):
    return crypt.decrypt(base64.b64decode(encrypted_user_token))
