import pandas as pd
from pandas.io.parsers import StringIO
import numpy as np
import requests
import csv
import re

# def get_stock_quotes(stock=None, date_start=False, date_end=False):
def get_stock_quotes(stock, date_start, date_end):
    """
    get_stock_quotes(stock, date1, date2) will return the tables consist of daily trading data found on Yahoo!  Finance
    website. All data except those for warrent, CBBC and OCBBC.

    Input: a string of date with the format yyyy/mm/dd
    Ouput: A list of pandas dataframes.
    """
    date = [date_start, date_end]
    pattern = re.compile("[0-9]{4}/[0-9]{2}/[0-9]{2}")
    df_list, year, month, day= [], [], [], []

    for i in date:
        assert isinstance( i, str), "date must be sting"
        match = pattern.match(i)
        assert not match is None, "Wrong format of date. Date must be of yyyy/mm/dd format."
        year.append(i.split("/")[0])
        month.append(i.split("/")[1])
        day.append(i.split("/")[2])

    CSVurl = "http://real-chart.finance.yahoo.com/table.csv?s={stock}&a={month_s}&b={day_s}&c={year_s}&d={month_e}\
&e={day_e}&f={year_e}&g={chart_format}&ignore=.csv".format(stock = stock,
                                                            month_s = str(int(month[0])-1),
                                                            day_s = day[0],
                                                            year_s = year[0],
                                                            month_e = str(int(month[1])-1),
                                                            day_e = day[1],
                                                            year_e = year[1],
                                                            chart_format="d")

    time.sleep( int( 5 * random.random() ) )
    res = requests.get(CSVurl)

    if int(res.status_code) == 404:
        print "404 error"
        return
    res.encoding = "unicode"
    data_string = res.text#.replace(u'-',u"")
    csvfile = StringIO(data_string)
    rows = list(csv.reader(csvfile))
    columns_number_set = set(map(lambda xx: len(xx), rows))
    for columns_number in columns_number_set:
        temp_rows = [row for row in rows if len(row) == columns_number]
        temp_df = pd.DataFrame(temp_rows[1:], columns = temp_rows[0])
        temp_df['COMPANY'] = stock
        df_list = temp_df
    return df_list

"""
This function check what's day is valid.
"""

def qoutes_valid_day():

    CSVurl = "http://real-chart.finance.yahoo.com/table.csv?s={stock}&a={month_s}&b={day_s}&c={year_s}&d={month_e}\
&e={day_e}&f={year_e}&g={chart_format}&ignore=.csv".format(stock = "MMM",
                                                            month_s = "",
                                                            day_s = "",
                                                            year_s = "",
                                                            month_e = "",
                                                            day_e = "",
                                                            year_e = "",
                                                            chart_format="d")

    res = requests.get(CSVurl)
    res.encoding = "unicode"
    data_string = res.text.replace(u'-',u"")
    csvfile = StringIO(data_string)
    rows = list(csv.reader(csvfile))
    columns_number_set = set(map(lambda xx: len(xx), rows))
    for columns_number in columns_number_set:
        DAYdata = [ row for row in rows if len(row) == columns_number ]
        DAYdf = pd.DataFrame(DAYdata[1:], columns = DAYdata[0])
        DAYlist = DAYdf["Date"].values.tolist()

    return DAYlist

DAYlist = qoutes_valid_day()

def verify_day(date):
    pattern = re.compile("[0-9]{4}/[0-9]{2}/[0-9]{2}")
#     df_list, year, month, day= [], [], [], []
    assert isinstance( date, str), "date must be sting"
    match = pattern.match(date)
    assert not match is None, "Wrong format of date. Date must be of yyyy/mm/dd format."
    year, month, day= date.split("/")
#     print year, month, day
    if (year + month + day) in DAYlist:
        return year + month + day, "True"
    else:
        return year + month + day, "False"


def get_SP500_daliy_quotes(date):
    """
    get_SP500_daliy_quotes() will return the tables consist of daily trading data found on Yahoo!  Finance
    website. All data except those for warrent, CBBC and OCBBC.

    Input: None
    Ouput: A list of pandas dataframes.
    """
    if verify_day(date)[1] is "False":
        return "There is no data. Please choose another day."

    CSVurlSP = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
    SP_res = requests.get(CSVurlSP)
    SP_res.encoding="unicode"
    SP_data_string = SP_res.text
    SP_csvfile = StringIO(SP_data_string)
    SP_rows = list(csv.reader(SP_csvfile))
    SP_columns_num_set = set(map(lambda xx: len(xx), SP_rows))
    SP_data = [SP_one_row for SP_one_row in SP_rows if len(SP_one_row) == 3]
    SP_df = pd.DataFrame(SP_data[1:], columns = SP_data[0])
    SP_name = SP_df["Symbol"].values.tolist()
    if "FRX" in SP_name: SP_name.remove("FRX")

    df_quotes = get_stock_quotes(SP_name[0], date, date)
    print len(SP_name)
    for i in SP_name[1:]:
        df_quotes = df_quotes.append(get_stock_quotes( i, date, date), ignore_index = True)
    bigdata = df_quotes
    return bigdata
