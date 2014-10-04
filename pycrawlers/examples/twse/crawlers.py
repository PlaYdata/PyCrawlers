
from pyquery import PyQuery
import requests
import pandas as pd
import numpy as np


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
    result = np.array([stock_id for stock_id in temp_result if not stock_id == u"公司代號"])
    return result

