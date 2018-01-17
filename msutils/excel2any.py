#!/usr/bin/env python  
# coding=utf-8  
# Python 2.7.3  

import os
import sys
import json
import numbers
import msgpack
import lua
import xlrd
import math
import re
from parse import parse
import traceback

# pprint
import pprint
pp = pprint.PrettyPrinter(indent=4)


SPECIAL_TAG = {
    'index': 'i',  # mark the sheet is a list, not dict
    'list1': 'l1',  # use `,` split to list
    'list2': 'l2',  # use `,|` split to list
    'root': 'r',  # mark the key is a sheet's attribute, not row's attribute
    'time': 't',  # mark the key time,
    'raw': 'a',  # raw value,
}

# 2d1h31m47s
intervals = (
    # ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('d', 86400),  # 60 * 60 * 24
    ('h', 3600),  # 60 * 60
    ('m', 60),
    ('s', 1),
)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

pattern_time_format = re.compile(r'[^0-9dhms]')
pattern_time = re.compile(r'([0-9]+)d|([0-9]+)h|([0-9]+)m|([0-9]+)s')
def tag_time(_value):
    if not isinstance(_value, unicode):
        return _value
    if _value:
        if pattern_time_format.search(_value):
            return _value
        second = 0
        match = pattern_time.findall(_value)
        if len(match) <= 0:
            return _value
        for vl in match:
            index = 0
            for v in vl:
                if v != "":
                    second = second + check_value(v) * intervals[index][1]
                index = index + 1
        return second
    return _value


def check_special_tag(_name):
    if _name:
        name = None
        re = parse("({tag}){value}", _name)
        if re:
            tags = re['tag'].split("#")
            name = re['value']
        else:
            re = parse("({tag})", _name)
            name = ""
        if re:
            tags = re['tag'].split("#")
            return tags, name

    return None, _name


def check_alias(_key, _value=False):
    if _value:
        try:
            return _key.split("#")[1], _key.split("#")[0]
        except:
            return _key, None
    else:
        try:
            return _key.split("#")[1]
        except:
            return _key


def check_map(_value):
    if not isinstance(_value, unicode):
        return False, None

    if _value.find('{') == -1 or len(_value) <= 1:
        return False, None

    data = []
    for text in _value.split(","):
        field = parse("{k}{{{v}}}", text)
        if not field:
            field = parse("{{{k}}}{v}", text)
        if not field:
            data.append(check_value(check_alias(parse("{{{v}}}", text)['v'])))
        else:
            data.append({'k': check_value(check_alias(field['k'])), 'v': check_value(check_alias(field['v']))})

    return True, data


def check_sheet_key(_key):
    try:
        return _key.split("~")[0], _key.split("~")[1]
    except:
        return None, None


def split(_value, _tags):
    re = _value.split(",")
    
    if SPECIAL_TAG['list2'] in _tags:
        new_re = []
        for x in re:
            new_re.append(x.split("|"))

        re = new_re

    return re


def set_value(_data, _key, _value, _tags):
    # normal
    if _tags and SPECIAL_TAG['raw'] in _tags:
        v = _value
        if not v:
            v = None
    elif _tags and (SPECIAL_TAG['list1'] in _tags or SPECIAL_TAG['list2'] in _tags):
        assert isinstance(_value, (str, unicode))
        if not _value:
            v = None
        else:        
            v = split(_value, _tags)
    else:
        # check special key
        re, field = check_map(_key)
        if re:
            for f in field:
                if not _data.has_key(f['k']):
                    _data[f['k']] = {}
                _data = _data[f['k']]
                _key = f['v']
        # check special value
        re, field = check_map(_value)
        if re:
            if len(field) == 1 and (not isinstance(field[0], dict)):
                _data[_key] = field[0]
                return
            if not _data.has_key(_key):
                _data[_key] = {}
            for f in field:
                _data[_key][f['k']] = tag_time(f['v'])
            return

        v = str(_value)
        # check_value(tag_time(check_alias()))

    if v != None:
        _data[_key] = v


def check_value(_value):
    if isinstance(_value, (unicode, str)):
        try:
            _value = float(_value)
        except:
            pass

    if isinstance(_value, float):
        if math.isnan(_value):
            return None
            
        if int(_value) == _value:
            return int(_value)

    if _value == "":
        return None

    return _value


def convert(_data, _xlsx_path, _start_row=2):
    DEBUG_XLSX=_xlsx_path
    DEBUG_SHEET=""
    DEBUG_ROW=0
    DEBUG_COL=0
    DEBUG_VALUE=""



    path, name = os.path.split(_xlsx_path)
    head, tail = os.path.splitext(name)
    if not tail in ['.xlsx'] or head.find('~$') == 0:
        return
    print path, name, head, tail

    data = {}
    xlsx_name = head.split("#")[0]
    if _data.has_key(xlsx_name):
        data = _data[xlsx_name]

    try:
        wb = xlrd.open_workbook(_xlsx_path)
        for sheet in wb.sheets():
            DEBUG_SHEET = sheet.name
            sheet_data = {}
            sheet_data_ref = sheet_data
            DEBUG_VALUE = sheet.cell(0, 0).value
            tags, name = check_special_tag(sheet.cell(0, 0).value)
            if tags and SPECIAL_TAG['index'] in tags:
                if name != "":
                    sheet_data[name] = []
                    sheet_data_ref = sheet_data[name]
                else:
                    sheet_data = []
                    sheet_data_ref = sheet_data

            for row in range(_start_row, sheet.nrows):
                DEBUG_ROW = row
                DEBUG_COL = 0
                DEBUG_VALUE = sheet.cell(row, 0).value
                row_name = check_value(sheet.cell(row, 0).value)
                row_data = {}
                for col in range(1, sheet.ncols):
                    DEBUG_COL = col
                    DEBUG_VALUE = sheet.cell(0, col).value
                    tags, col_name = check_special_tag(check_value(sheet.cell(0, col).value))
                    if not col_name or col_name.startswith("_"):
                        continue
                    DEBUG_VALUE = sheet.cell(row, col).value

                    value = sheet.cell(row, col).value
                    # print _xlsx_path, sheet.name, row, col, value
                    content = row_data
                    if tags and SPECIAL_TAG['root'] in tags:
                        content = sheet_data

                    if tags and SPECIAL_TAG['time'] in tags:
                        value = tag_time(value)

                    set_value(content, col_name, value, tags)

                if isinstance(sheet_data_ref, list):
                    sheet_data_ref.append(row_data)
                else:
                    sheet_data_ref[row_name] = row_data

            tags, _ = check_special_tag(sheet.name)
            sheet_alias_name, sheet_other_name = check_alias(sheet.name, True)
            sheet_key = None
            sheet_value = None
            if sheet_other_name and sheet_other_name != "":
                sheet_key, sheet_value = check_sheet_key(sheet_alias_name)

            if wb.nsheets <= 1 or (tags and SPECIAL_TAG['root'] in tags):
                if isinstance(sheet_data, list):
                    data = sheet_data
                else:
                    for v in sheet_data:
                        assert not data.has_key(v), "duplicate tag:{0} in sheet {1}".format(v,sheet.name)
                        data[v] = sheet_data[v]
            else:                    
                data[sheet_alias_name] = sheet_data
    except Exception as e:
        print bcolors.FAIL
        print "==================== Exception ========================="
        print "DEBUG_XLSX:",  DEBUG_XLSX
        print "DEBUG_SHEET:", DEBUG_SHEET
        print "DEBUG_ROW:",   DEBUG_ROW
        print "DEBUG_COL:",   DEBUG_COL
        print "DEBUG_VALUE:", DEBUG_VALUE
        print "==================== Exception ========================="
        print bcolors.ENDC
        traceback.print_exc()
        os.exit(-1)

    if not _data.has_key(xlsx_name):
        _data[xlsx_name] = data

def md5_file(fname):
    import hashlib
    try:
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except:
        return None

def md5_content(content):
    import hashlib
    try:
        hash_md5 = hashlib.md5()
        hash_md5.update(content)
        return hash_md5.hexdigest()
    except:
        return None

def getargv(_index, _default=None):
    try:
        return sys.argv[_index]
    except Exception, e:
        return _default

def convert_dir(_data, _dir, _output_dir, _allinone, _hash_record, _start_row=2):
    json_hash_dict = _hash_record.get('json',{})
    bin_hash_dict = _hash_record.get('bin',{})
    xls_hash_dict = _hash_record.get('xls',{})

    src_changes = []
    dist_changes = {}
    exists_change = False

    change_list = []
    xlsx_list = []
    for folder, subs, files in os.walk(_dir):
        for filename in files:
            xls_name,ext = os.path.splitext(filename)
            xls_path = os.path.join(_dir, filename)

            if ext != ".xlsx" or xls_name.startswith("."):
                continue

            xls_alias_name, xls_alias_value = check_alias(xls_name, True)
            if xls_alias_value:
                xls_name = xls_alias_value
            else:
                xls_name = xls_alias_name
            
            if not _allinone:
                json_path = os.path.join(_output_dir, xls_name + '.json')
                bin_path = os.path.join(_output_dir, xls_name + '.bin')
            else:
                json_path = os.path.join(_output_dir, 'data/' + xls_name + '.json')
                bin_path = os.path.join(_output_dir, 'data/' + xls_name + '.bin')
            
            xls_md5 = md5_file(xls_path)
            json_md5 = md5_file(json_path)
            bin_md5 = md5_file(bin_path)
            
            xlsx_list.append((filename, xls_name, bin_path))

            if xls_hash_dict.get(filename, '') != xls_md5 or bin_hash_dict.get(xls_name, '') != bin_md5 or json_hash_dict.get(xls_name, '') != json_md5:
                exists_change = True
                if xls_name not in change_list:
                    change_list.append(xls_name)

                xls_hash_dict[filename] = xls_md5

    for (filename, xls_name, bin_path) in xlsx_list:
        if xls_name in change_list:
            src_changes.append(filename)
            dist_changes[xls_name] = True
            xls_path = os.path.join(_dir, filename)
            convert(_data, xls_path, _start_row)
        else:
            with open(bin_path, "rb") as f:
                data = msgpack.load(f)
                if not _data.has_key(xls_name):
                    _data[xls_name] = {}
                if isinstance(data, dict):
                    for data_key in data.keys():
                        _data[xls_name][data_key] = data[data_key]
                elif isinstance(data, list):
                    _data[xls_name] = data



    _hash_record["xls"] = xls_hash_dict

    return src_changes, dist_changes, exists_change

def read_record(_path):
    hash_dict = {"json":{}, "bin":{}, "xls":{}}

    if os.path.exists(_path):
        try:
            with open(_path, "r") as f:
                hash_dict = json.load(f)
        except:
            pass
    return hash_dict

def save_record(_path, hash_dict):
    with open(_path, "w") as f:
        f.write(json.dumps(hash_dict, ensure_ascii=False, indent=2, sort_keys=True))

def export(_data, _output_dir, _filter=None, _hash_record=None, _export_format=["lua","json","bin"]):
    # json/bin md5
    for key in _data:
        if _filter and not _filter.get(key):
            continue

        for fmt in _export_format:
            if fmt == "lua":
                content = "return " + lua.dumps(_data[key], ensure_ascii=False, indent=2, sort_keys=True)
            elif fmt == "json":
                content = json.dumps(_data[key], ensure_ascii=False, indent=2, sort_keys=True)
            elif fmt == "bin":
                content = msgpack.packb(_data[key], use_bin_type=True)

            with open(os.path.join(_output_dir, key + "." + fmt), "w") as f:
                if _hash_record and _hash_record.get(fmt) != None:
                    _hash_record[fmt][key] = md5_content(content)

                if fmt != "bin":
                    f.write(content.encode('utf-8'))
                else:
                    f.write(content)

def export_allinone(_data, _output_dir, _output_prefix, _ignore=None):
    _data["@version"] = os.popen("(git rev-parse --short HEAD)").read().strip()

    if _ignore:
        for ignore in _ignore:
            if ignore in _data:
                del _data[ignore]

    encodedjson = json.dumps(_data, ensure_ascii=False, indent=2, sort_keys=True)
    with open(os.path.join(_output_dir, _output_prefix + ".json"), "w") as f:
        f.write(encodedjson)

    encodedlua = lua.dumps(_data, ensure_ascii=False, indent=2, sort_keys=True)
    with open(os.path.join(_output_dir, _output_prefix + ".lua"), "w") as f:
        f.write("return "+encodedlua)


    messagepacked = msgpack.packb(_data, use_bin_type=True)
    with open(os.path.join(_output_dir, _output_prefix + ".bin"), "w") as f:
        f.write(messagepacked)

def main():
    reload(sys)
    sys.setdefaultencoding('utf-8')

    if len(sys.argv) < 2:
        print "Invalide args! <source_path[, output_path, ]>"
        return

    source_path   = getargv(1)
    output_path   = getargv(2, source_path)
    output_prefix = getargv(3, None)
    ignore_list   = getargv(4, "").split("|")

    data = {}

    if source_path.endswith(".xlsx"):
        convert(data, source_path)
        export(data, output_path)
    else:
        hash_dict = read_record(os.path.join(source_path, "hash.json"))
        src_changes, dist_changes, exists_change = convert_dir(data, source_path, output_path, output_prefix, hash_dict)

        if output_prefix:
            export_allinone(data, output_path, output_prefix, ignore_list)

        elif exists_change:
            export(data, output_path, dist_changes, hash_dict)

            save_record(os.path.join(source_path, "hash.json"), hash_dict)


if __name__ == '__main__':
    main()
