
import requests
import pandas as pd 
from pyquery import PyQuery
import re
import numpy as np
from pycrawlers.examples.twse.crawlers import get_stockID_twse
import traceback
import datetime


def get_stock_major_data(stock_id):

    res = requests.get("https://tw.stock.yahoo.com/d/s/major_{stock_id}.html".format(stock_id=stock_id))
    S = PyQuery(res.text)
    
    date_list = map(int,re.findall("[0-9]+",S("td.tt").filter(lambda i,e:len(PyQuery(e).text().split("/"))>1).text()))
    date_list[0] = date_list[0]+1911
    date = "-".join(map(str,date_list))
    
    data_table = pd.read_html(S("table").filter(lambda i,e:len(PyQuery(e)("td.ttt")) == 128).outerHtml())[0]
    
    pre_df = np.r_[ data_table.values[1:,0:4], data_table.values[1:,4:]]
    df = pd.DataFrame(pre_df)
    df.columns = ["trader","buy","sell","net"]
    df["stockId"] = df["trader"].map(lambda xx: stock_id)
    df["dateString"] = df["trader"].map(lambda xx: date)
    df = df[["dateString","stockId","trader","buy","sell","net"]]
    
    df["buy"] = df["buy"].map(lambda xx:int(xx))
    df["sell"] = df["sell"].map(lambda xx:int(xx))
    df["net"] = df["net"].map(lambda xx:int(xx))
    
    return {"stockId":stock_id,"date":date,"data":df}
    


def get_all_stock_major_data(stock_ids = get_stockID_twse('sii').tolist() + get_stockID_twse('otc').tolist()):
    all_data_df_list = []
    error_stock_ids = []
    
    #stock_ids = stock_ids[:10]
    
    while len(stock_ids) > 0:
        print "len(stock_ids) = ",len(stock_ids)
        one_stock_id = stock_ids.pop()
        
        try:
            one_stock_data = get_stock_major_data(one_stock_id)
            all_data_df_list.append(one_stock_data["data"])
            print "%s -- SUCCESS" % one_stock_id
        except Exception as e:
            print "%s -- ERROR" % one_stock_id
            print e
            print traceback.format_exc()
            #print e.__dict__
            #print e.message
            #print pickle.dumps(e.request)
            
            error_stock_ids.append({"stockId":one_stock_id,
                                    "message":e.message,
                                    "traceback":traceback.format_exc()})
    
    return {"data":pd.concat(all_data_df_list), "error":error_stock_ids}



def update_all_stock_major_data(data_collection, error_collection):
    
    twse_ids = get_stockID_twse('sii').tolist()
    twotc_ids = get_stockID_twse('otc').tolist()
    
    stock_ids = twse_ids + twotc_ids
    #stock_ids = stock_ids[:10]
    
    counter = 0
    len_stock_ids = len(stock_ids)
    for one_stock_id in stock_ids:
        print "~~~~~~~~~~~~~~~~~~~~~~~~"
        print "%s/%s = " % (counter,len_stock_ids)
        counter = counter + 1
        #one_stock_id = stock_ids.pop()
        
        try:
            one_stock_data = get_stock_major_data(one_stock_id)
            one_stock_data_in_db = data_collection.find({"stockId":one_stock_data["stockId"],"dateString":one_stock_data["date"]}).count()>0
            if not one_stock_data_in_db:
                data_collection.insert(one_stock_data["data"].to_dict(outtype="record"))
                print "%s -- SUCCESS: insert into db " % one_stock_id
            else:
                print "%s -- SUCCESS: already in db " % one_stock_id
                
            
            
        except Exception as e:
            
            print "%s -- ERROR" % one_stock_id
            print e
            print traceback.format_exc()
            #print e.__dict__
            #print e.message
            #print pickle.dumps(e.request)
            try:
                error_collection.insert({"stockId":one_stock_id,
                                         "message":e.message,
                                         "traceback":traceback.format_exc(),
                                         "time":datetime.datetime.now()})
            except:
                error_collection.insert({"stockId":one_stock_id,
                                         "traceback":traceback.format_exc(),
                                         "time":datetime.datetime.now()})
            
    
    
    
            
            
    
