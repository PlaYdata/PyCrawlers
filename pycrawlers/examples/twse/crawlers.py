
from pyquery import PyQuery
import requests
import pandas as pd
import numpy as np
from pandas.io.parsers import StringIO
import csv
import re


def get_stockID_twse(field):
    """
    get_stockID_twse will return an numpy array which consists of stockID on twse.
    Input: 
        field: a string, can be either 'sii', 'otc', 'rotc' or 'pub'.
    Output:
        resutl: a numpy array of strings consists of stock ids. 
    """
    assert field in ["sii", "otc", "rotc", "pub"], "field must be 'sii', 'otc', 'rotc' or 'pub'."
    req_data = {"encodeURIComponent":1,
                "step":1,
                "firstin":1,
                "TYPEK":field,
                "code":""}
    resp = requests.post("http://mops.twse.com.tw/mops/web/ajax_t51sb01", data = req_data)
    resp.encoding = "utf8"
    query = PyQuery(resp.text)
    data = query("table").filter(lambda i, e: len(PyQuery(e)("td")) > 1)
    data_html = data.outerHtml()
    df = pd.read_html(data_html, infer_types=False)[0]
    temp_result = df[:][0]
    result = np.array([stock_id for stock_id in temp_result if not stock_id == u"\u516c\u53f8\u4ee3\u865f"])
    return result

def get_dailyQuotes_twse(date):
    """
    get_dailyQuotes_twse(date) will return the tables consist of daily trading data found on twse
    website. All data except those for warrent, CBBC and OCBBC.
    
    Input: a string of date with the format yyyy/mm/dd
    Ouput: A list of pandas dataframes. 
    """
    assert isinstance(date, str), "date must be sting"
    pattern = re.compile("[0-9]{4}/[0-9]{2}/[0-9]{2}")
    match = pattern.match(date)
    assert not match is None, "Wrong format of date. Date must be of yyyy/mm/dd format."
    
    df_list = []
    year, month, day = date.split("/")
    ym = year + month
    ymd = year + month + day
    url = "http://www.twse.com.tw/en/trading/exchange/MI_INDEX/MI_INDEX3_print.php?genpage=genpage/Report{year}{month}/A112{year}{month}{day}ALLBUT0999_1.php&type=csv".format(year = year, month = month, day = day)
    res = requests.get(url)
    res.encoding = "big5"
    data_string = res.text.replace(u'\uff0b',u"+").replace(u'\uff0d',u"-").replace(u'\uff1a',u":").replace(u'\u2019',"`")
    csvfile = StringIO(data_string)
    rows = list(csv.reader(csvfile))
    columns_number_set = set(map(lambda xx: len(xx), rows))
    for columns_number in columns_number_set:
        temp_rows = [row for row in rows if len(row) == columns_number]
        temp_df = pd.DataFrame(temp_rows[1:], columns = temp_rows[0])
        for colname in temp_df.columns:
            temp_df[colname] = temp_df[colname].map(lambda xx: xx.replace("=", "").replace(",", "").replace('"', "").replace("--", ""))
        df_list.append(temp_df)
    return df_list