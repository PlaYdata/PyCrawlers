import pandas as pd
from pandas.io.parsers import StringIO
import numpy as np
import requests
import csv
import re
import tempfile
import time
import os
import zipfile

def get_daily_history_taifex(start_date, end_date):
    assert isinstance(start_date, str) and isinstance(end_date, str), "date must be sting"
    pattern = re.compile("[0-9]{4}/[0-9]{2}/[0-9]{2}")
    match1 = pattern.match(start_date)
    match2 = pattern.match(end_date)
    assert not (match1 is None or match2 is None), "Wrong format of date. Date must be of yyyy/mm/dd format."
    
    time_tuple1 = time.strptime('{start_date} 0:0:0'.format(start_date = start_date), '%Y/%m/%d %H:%M:%S')
    time_in_sec1 = time.mktime(time_tuple1)
    time_tuple2= time.strptime('{end_date} 23:59:59'.format(end_date = end_date), '%Y/%m/%d %H:%M:%S')
    time_in_sec2 = time.mktime(time_tuple2)
    dur = time_in_sec2 - time_in_sec1 + 1
    assert dur <= 2592000.0, "Can not query data longer than 30 days."
    
    req_data = {"DATA_DATE":start_date,
                "DATA_DATE1":end_date,
                "COMMODITY_ID":"all",
                "commodity_id2t":""}
    res = requests.post("http://www.taifex.com.tw/eng/eng3/eng3_2dl.asp", data = req_data)
    res.encoding = "big5"
    csv_string = res.text.replace(u'\uff0b',u"+").replace(u'\uff0d',u"-").replace(u'\uff1a',u":").replace(u"\u2019", u"`")
    csvfile = StringIO(csv_string)
    rows = list(csv.reader(csvfile))
    columns_number_set = set(map(lambda xx: len(xx), rows))
    df_list = []
    for columns_number in columns_number_set:
        temp_rows = [one_row for one_row in rows if len(one_row) == columns_number]
        columns = map(lambda xx: " ".join(map(lambda yy: yy.capitalize(), re.split(" |_", xx))), temp_rows[0])
        temp_df = pd.DataFrame(temp_rows[1:], columns = columns)
        for colname in temp_df.columns:
            temp_df[colname] = temp_df[colname].map(lambda xx: xx.replace(u"-", "").replace(u",", ""))
        df_list.append(temp_df)
    return df_list

def get_annual_history_taifex(year, cache = False):
    assert isinstance(year, str), "year must be sting"
    pattern = re.compile("[0-9]{4}")
    match = pattern.match(year)
    assert not match is None, "Wrong format of year. Year must be of yyyy format."
    
    temp_path = tempfile.mkdtemp("_pycrawlers", "taifex_")
    url = "http://www.taifex.com.tw/eng/eng3/hisdata_fut/{year}_fut.zip".format(year = year)
    res = requests.get(url, stream = True)
    temp_zip = zipfile.ZipFile(StringIO(res.content))
    temp_zip.extractall(path = temp_path)
    df_list = []
    for filename in os.listdir(temp_path):
        file_path = os.path.join(temp_path, filename)
        with open(file_path, "r") as rf:
            temp_rows = rf.readlines()
        csvfile = StringIO("".join(temp_rows))
        rows = list(csv.reader(csvfile))
        temp_df = pd.DataFrame(rows[1:], columns = rows[0])
        temp_df.columns = map(lambda xx: " ".join(map(lambda yy: yy.capitalize(), re.split(" |_", xx))), temp_df.columns)
        for colname in temp_df.columns:
            temp_df[colname] = temp_df[colname].map(lambda xx: xx.replace(u"-", "").replace(u",", ""))
        df_list.append(temp_df)
    if not cache:
        os.system("rm -rf {path}".format(path = temp_path))
        return pd.concat(df_list)
    else:
        return pd.concat(df_list), temp_path