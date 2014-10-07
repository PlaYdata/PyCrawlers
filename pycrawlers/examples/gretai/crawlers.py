import pandas as pd
from pandas.io.parsers import StringIO
import numpy as np
import requests
import csv
import re

URL_template = "http://www.gretai.org.tw/web/stock/aftertrading/DAILY_CLOSE_quotes/stk_quote_download.php?l=en-us&d={date}"

def get_dailyQuotesOTC_gretai(date):
    assert isinstance(date, str), "date must be sting"
    pattern = re.compile("[0-9]{4}/[0-9]{2}/[0-9]{2}")
    match = pattern.match(date)
    assert not match is None, "Wrong format of date. Date must be of yyyy/mm/dd format."
    
    res = requests.get(URL_template.format(date = date))
    res.encoding = "big5"
    csv_string = res.text.replace(u'\uff0b',u"+").replace(u'\uff0d',u"-").replace(u'\uff1a',u":").replace(u"\u2019", u"`")
    csvfile = StringIO(csv_string)
    rows = list(csv.reader(csvfile))
    columns_num_set = set(map(lambda xx: len(xx), rows))
    df_list = []
    for col_num in columns_num_set:
        temp_rows = [one_row for one_row in rows if len(one_row) == col_num]
        temp_df = pd.DataFrame(temp_rows[1:], columns = temp_rows[0])
        for colname in temp_df.columns:
            temp_df[colname] = temp_df[colname].map(lambda xx: xx.replace("=", "").replace(",", "").replace('"', "").replace("---", ""))
        temp_df["Date"] = date
        df_list.append(temp_df)
    return df_list

