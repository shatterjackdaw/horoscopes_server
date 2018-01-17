# -*- coding:utf-8 -*-
import base64
import hmac
import md5
import hashlib
import M2Crypto
from Crypto.Hash import SHA, MD5
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Cipher import DES3


always_safe = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
               'abcdefghijklmnopqrstuvwxyz'
               '0123456789' '_.-')
_safe_map = {}
for i, c in zip(xrange(256), str(bytearray(xrange(256)))):
    _safe_map[c] = c if (i < 128 and c in always_safe) else '%{:02x}'.format(i)
_safe_quoters = {}


def quote_lower(s, safe='/'):
    """quote('abc def') -> 'abc%20def'

    Each part of a URL, e.g. the path info, the query, etc., has a
    different set of reserved characters that must be quoted.

    RFC 2396 Uniform Resource Identifiers (URI): Generic Syntax lists
    the following reserved characters.

    reserved    = ";" | "/" | "?" | ":" | "@" | "&" | "=" | "+" |
                  "$" | ","

    Each of these characters is reserved in some component of a URL,
    but not necessarily in all of them.

    By default, the quote function is intended for quoting the path
    section of a URL.  Thus, it will not encode '/'.  This character
    is reserved, but in typical usage the quote function is being
    called on a path where the existing slash characters are used as
    reserved characters.
    """
    # fastpath
    if not s:
        if s is None:
            raise TypeError('None object cannot be quoted')
        return s
    cachekey = (safe, always_safe)
    try:
        (quoter, safe) = _safe_quoters[cachekey]
    except KeyError:
        safe_map = _safe_map.copy()
        safe_map.update([(c, c) for c in safe])
        quoter = safe_map.__getitem__
        safe = always_safe + safe
        _safe_quoters[cachekey] = (quoter, safe)
    if not s.rstrip(safe):
        return s
    return ''.join(map(quoter, s))


def ensure_utf8(s):
    if isinstance(s, unicode):
        s = s.encode('utf8')
    return s


# hmac
def hmac_sign(s, secret):
    return hmac.new(key=secret, msg=s, digestmod=hashlib.sha1).hexdigest()


# md5
def md5_sign(s):
    return hashlib.md5(s).hexdigest()


# md5_byte_hex
def md5_byte_sign(s, flag=None):
    if flag:
        print 124
        md5_data = hashlib.md5(s).digest()
        return base64.b64encode(md5_data)
    else:
        return hashlib.md5(s).digest()


# rsa
def rsa_sign(s, private_key, use_md5=False):
    if use_md5:
        s = MD5.new(s)
    else:
        s = SHA.new(s)
    pk = RSA.importKey(private_key)
    signer = PKCS1_v1_5.new(pk)
    return signer.sign(s)


# rsa verify
def rsa_verify(s, key, sign, use_md5=False):
    if use_md5:
        s = MD5.new(s)
    else:
        s = SHA.new(s)
    pk = RSA.importKey(key)
    verifier = PKCS1_v1_5.new(pk)
    return verifier.verify(s, base64.b64decode(sign))


# rsa decrypt
def rsa_decrypt(s, key):
    pk = M2Crypto.RSA.load_pub_key_bio(M2Crypto.BIO.MemoryBuffer(key))
    dec_s = base64.b64decode(s)
    input_len = len(dec_s)
    offset = 0
    i = 0
    maxDecryptBlock = 128
    params = ""
    while input_len - offset > 0:
        if input_len - offset > maxDecryptBlock:
            cache = pk.public_decrypt(dec_s[offset: offset + maxDecryptBlock], M2Crypto.RSA.pkcs1_padding)
        else:
            cache = pk.public_decrypt(dec_s[offset:], M2Crypto.RSA.pkcs1_padding)
        params += cache
        i += 1
        offset = i * maxDecryptBlock
    return params


# rsa decrypt to dict
def rsa_decrypt_to_dict(s, key):
    pk = M2Crypto.RSA.load_pub_key_bio(M2Crypto.BIO.MemoryBuffer(key))
    dec_s = base64.b64decode(s)
    input_len = len(dec_s)
    offset = 0
    i = 0
    maxDecryptBlock = 128
    params = ""
    while input_len - offset > 0:
        if input_len - offset > maxDecryptBlock:
            cache = pk.public_decrypt(dec_s[offset: offset + maxDecryptBlock], M2Crypto.RSA.pkcs1_padding)
        else:
            cache = pk.public_decrypt(dec_s[offset:], M2Crypto.RSA.pkcs1_padding)
        params += cache
        i += 1
        offset = i * maxDecryptBlock
    rtv = {}
    for f in params.split('&'):
        k, _, v = f.partition('=')
        rtv[k] = v
    return rtv


# base64encode
def base64_encode(s):
    return base64.b64encode(s)


# base64decode
def base64_decode(s):
    return base64.b64decode(s)


def des3ecb_decrypt(s, key):
    cipher = DES3.new(key, DES3.MODE_ECB)
    return cipher.decrypt(base64.standard_b64decode(s))


# ++++++++++++++++++++酷派RAS专用算法++++++++++++++++++++++++

class Cptranssyncsignvalid:
    def getparam(self, transdata, sign, key):
        m1 = md5.new()
        m1.update(transdata)
        md5Str = m1.hexdigest()
        # print md5Str
        decodeBaseStr = base64.decodestring(key)
        # 截取41位以后的再做一次Base64
        tempStr = decodeBaseStr[40:len(decodeBaseStr)]
        finalStr = base64.decodestring(tempStr)
        # print finalStr
        # 以‘+’拆分得到privateKey和modKey，以空格拆分sign
        if '+' in finalStr:
            decodeBaseVec = finalStr.split('+')
            privateKey = decodeBaseVec[0]
            modKey = decodeBaseVec[1]
        else:
            print "paykey不正确，请检查"
        chs = sign.split(' ')
        if (chs == ''):
            print "密文不符要求"
        # 用数组接收tobytearray返回的字符串
        reqRsa = [0, 0, 0]
        chsStr0 = "%d" % (int(chs[0], 16))
        chsStr1 = "%d" % (int(chs[1], 16))
        chsStr2 = "%d" % (int(chs[2], 16))
        reqRsa[0] = rsa(chsStr0, privateKey, modKey)
        reqRsa[1] = rsa(chsStr1, privateKey, modKey)
        reqRsa[2] = rsa(chsStr2, privateKey, modKey)
        reqRsabyte = [0, 0, 0]
        for i in range(0, 3):
            reqRsabyte[i] = tobyte(reqRsa[i])
        reqMd5 = '%s%s%s' % (reqRsabyte[0], reqRsabyte[1], reqRsabyte[2])
        return (1 if md5Str in reqMd5 else 0)


def modpow(b, e, m):
    result = 1
    while (e > 0):
        if e & 1:
            result = (result * b) % m
        e = e >> 1
        b = (b * b) % m
    return result


def str_to_int(string):
    n = 0
    for i in range(len(string)):
        n = n >> 8
        # print ord(string[i])
        n += ord(string[i])
    return n


def rsa(data, e, n):
    result = modpow(long(data, 10), long(e, 10), long(n, 10))
    return result


# @param 传入RSA解码出来的大数
# @return byte数组转换的字符串；
def tobyte(big):
    byteLen = big.bit_length() / 8 + 1
    byteArray = [0] * byteLen
    # 取得比特位数
    bigByte = bin(big).replace('0b', '')
    for i in range(0, byteLen):
        if i == 0:
            byteArray[i] = chr(int(bigByte[0:big.bit_length() - (byteLen - 1) * 8], base=2))
        else:
            byteArray[i] = chr(
                int(bigByte[big.bit_length() + i * 8 - (byteLen) * 8:big.bit_length() + i * 8 - (byteLen - 1) * 8],
                    base=2))
            # 将比特数组转换成字符串
    byteStr = ''.join(byteArray)
    return byteStr


if __name__ == "__main__":
    paykey = "M0NCNjVCN0FEQTU2QjhERkQxQjVEMDc3NUUxMUZCNjUwMTMyNEQxNU1URXlOelUzT0RBM01EQXpNVFE0TVRFeU16RXJNVFEwTVRrM05qWTBPVEF4T0RVd01UVTRNVEF3TWpNMU1qa3pNek01TXpjMU1ESTNNVEF4"

    # 2、提取支付结果通知数据
    result = "FAILURE"
    # 3、解析支付结果通知数据成业务数据
    # transdata = "{\"exorderno\":\"20160906201750377866374900\",\"transid\":\"T3116090620174710305\",\"waresid\":1,\"appid\":\"5000004399\",\"feetype\":0,\"money\":1,\"count\":1,\"result\":0,\"transtype\":0,\"transtime\":\"2016-09-06 20:17:56\",\"cpprivate\":\"\",\"paytype\":406}"
    # sign = "291d3ade3c803cc2e4265488195e14db 3ff0f817d9f4c5d65e72112e0e38a11b e5a23bc50f280c4c9a0347630aae36"
    transdata = "{\"exorderno\":\"fz201612120519563938coolpad\",\"transid\":\"T3116120810510216766\",\"waresid\":1,\"appid\":\"5000005233\",\"feetype\":0,\"money\":6,\"count\":1,\"result\":0,\"transtype\":0,\"transtime\":\"2016-12-08 10:51:52\",\"cpprivate\":\"\",\"paytype\":401}"
    sign = "3e455105f34bdcc4d6fd1ee0b36eddc9 267d0b2e382afe27ec8bd12f932d6bfd 226bc83de1f2cc44b1a21c8255692177 "

    checkPart = Cptranssyncsignvalid()
    checkFlag = checkPart.getparam(transdata, sign, paykey)
    print checkFlag
