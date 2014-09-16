import requests
from pyquery import PyQuery
import pandas as pd

def filter_blanks_in_sessions(one_session_string):
    return " ".join([xx for xx in one_session_string.split(" ") if xx != ""])

def get_chapters_and_sessions(one_book_page_url, output_type="json"):
    """
    output_type in ["list_of_tuple", "json"]
    if output_type=="list_of_tuple" 
        return book_name, page_url, [(ch1_name, [session1_name, session2_name, ...]), (ch2_name, [session1_name, session2_name, ...]), ... ]
    
    if output_type=="json" 
        return {"book_name":book_name,
                "chapters":[{"chapter":ch1_name, "session":[session1_name, session2_name, ...]}, 
                {"chapter":ch2_name, "session":[session1_name, session2_name, ...]}, ... ]}

    """
    
    assert output_type in ["list_of_tuple", "json"]
    
    r = requests.get(one_book_page_url)
    S = PyQuery(r.text)
    book_name = S(".detailheader").text()
    chapters_and_sessions = S("#tab_02_2_content li.chapter").map(lambda ii,ee:(PyQuery(ee)("h3").text(),
                                                                                map(filter_blanks_in_sessions,PyQuery(ee)("h4").map(lambda i,e:PyQuery(e).text()))
                                                                                ))
    
    if output_type=="list_of_tuple" :
        return book_name, one_book_page_url, chapters_and_sessions
    elif output_type=="json":
        return {"book_name":book_name, 
                "page_url":one_book_page_url,
                "chapters":map(lambda xx:{"chapter":xx[0],"sessions":xx[1]},chapters_and_sessions)}
        