
import sys
import os
import numpy as np

pyfile_name = sys.argv[0]
print "[{pyfile_name}] Processing....".format(pyfile_name = sys.argv[0])

try:
    port = int(sys.argv[1])
    logpath = sys.argv[2]
except:
    print "Missing port or logpath"
    print "Usage: python TWusRgroup_Youtube_Video_Crawler.py <port> <logpath> [<dbpath>]"
    print "Exiting now...."
    exit()

print "[{pyfile_name}] Start mongod on localhost at port {port}".format(pyfile_name = pyfile_name, port = port)
print "[{pyfile_name}] log file is under {logpath}".format(pyfile_name = pyfile_name, logpath = logpath)

import requests
try:
    import ujson as json 
except:
    import json

import pymongo

try:
    dbpath = sys.argv[3]
    command = "mogod --port {port} --dbpath {dbpath} --logpath {logpath} --fork".format(port = port, dbpath = dbpath, logpath = logpath)
except:
    command = "mongod --port {port} --logpath {logpath} --fork".format(port = port, logpath = logpath)

os.system(command)

client = pymongo.MongoClient("localhost", port)
TWusRgroup = client["TWusRgroup"]


class YoutubeChannelOpenData(object):
    def __init__(self, channel_id, datatype = "json"):
        assert datatype in ["xml", "json"], 'datatype must in ["xml", "json"]'        
        self.channel_id = channel_id
        self.datatype = datatype
        
    def get_data(self, datafeed_url, params = {}, key = None):
        if self.datatype == "json":
            params["alt"] = "json"
            r = requests.get(datafeed_url, params = params)
            if key == None:
                return json.loads(r.text)
            else:
                return json.loads(r.text)[key]
        else:
            if key == None:
                return requests.get(datafeed_url, params)
            else:
                return requests.get(datafeed_url, params)

    @property
    def base_url(self):
        return "https://gdata.youtube.com/feeds/users/{channel_id}/".format(channel_id=self.channel_id)
    
    @property
    def playlist_url(self):
        return "https://gdata.youtube.com/feeds/users/{channel_id}/playlists/".format(channel_id=self.channel_id)
    
    @property
    def uploads_url(self):
        return "https://gdata.youtube.com/feeds/users/{channel_id}/uploads/".format(channel_id=self.channel_id)


twusergroup = YoutubeChannelOpenData("TWuseRGroup")

data_feed = twusergroup.get_data(twusergroup.uploads_url, {}, "feed")
playlist_urls = [data_feed["link"][4]["href"], data_feed["link"][5]["href"]]

empty = False
while not empty:
    temp_data = twusergroup.get_data(playlist_urls[-1], {}, "feed")
    checking_list = []
    for item in temp_data["link"]:
        checking_list.append(item["rel"]) 
    if "next" in checking_list:
        ind = checking_list.index("next")
        playlist_urls.append(temp_data["link"][ind]["href"])
    else:
        empty = True


TWusRgroup.uploads_list_urls.drop()
insert_object = {"urls":playlist_urls}
TWusRgroup.uploads_list_urls.insert(insert_object)


TWusRgroup.vedio_urls.drop()
for uploads_list_url in playlist_urls:
    temp_data = twusergroup.get_data(uploads_list_url, {}, "feed")
    for media_list in temp_data["entry"]:
        author = media_list["author"][0]["name"]["$t"]
        updated = media_list["updated"]["$t"]
        title = media_list["title"]["$t"]
        category = media_list["category"]
        description = media_list["media$group"]["media$description"]["$t"]
        url = media_list["media$group"]["media$player"][0]["url"]
        start_ind = url.find("v=")
        end_ind = url.find("&feature")
        url_id = url[start_ind + 2:end_ind]
        json_obj = {"_id": url_id,
                    "author": author,
                    "updated": updated,
                    "title": title,
                    "category": category,
                    "description": description,
                    "url": url}
        TWusRgroup.vedio_urls.insert(json_obj)


os.system('pkill -f mongod')
