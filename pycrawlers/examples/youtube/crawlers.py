

import requests

try:
    import ujson as json 
except:
    import json
    

def summary_one_upload_data_entry(one_upload_data_entry):
    return {"ytid":one_upload_data_entry["id"]["$t"].split("/")[-1],
            "title":one_upload_data_entry["title"]["$t"],
            "categories":one_upload_data_entry["category"],
            "author":one_upload_data_entry["author"][0]["name"]["$t"],
            "description":one_upload_data_entry["media$group"]["media$description"]["$t"],
            }



class YoutubeChannelOpenData(object):
    def __init__(self, channel_id, datatype="json"):
        
        assert datatype in ["xml", "json"], 'datatype must in ["xml", "json"]'
        
        self.channel_id = channel_id
        self.datatype = datatype
        
    
    def _get_data(self, datafeed_url):
        if self.datatype == "json":
            return json.loads(requests.get(datafeed_url, params={"alt":"json"}).text)
        else:
            return requests.get(datafeed_url).text
            
    
    @property
    def base_url(self):
        return "https://gdata.youtube.com/feeds/users/{channel_id}".format(channel_id=self.channel_id)
    
    
    @property
    def playlist_url(self):
        return "https://gdata.youtube.com/feeds/users/{channel_id}/playlists/".format(channel_id=self.channel_id)
    
    
    @property
    def uploads_url(self):
        return "https://gdata.youtube.com/feeds/users/{channel_id}/uploads/".format(channel_id=self.channel_id)

    
    def get_all_uploads(self, entry_parser=summary_one_upload_data_entry):
        all_upload_data_list = []
        
        next_page_list = [self.uploads_url]
        #print "next_page_list = ",next_page_list
        
        while len(next_page_list) > 0:

            upload_data = self._get_data(next_page_list[0])
            
            all_upload_data_list.extend(map(entry_parser, upload_data["feed"]["entry"]))
            next_page_list = [xx["href"] for xx in upload_data["feed"]["link"] if xx["rel"] == "next"]
            #print "next_page_list = ",next_page_list
            
        return all_upload_data_list
    

def crawl_channel_uploads(channel_id):
    ytcrawler = YoutubeChannelOpenData(channel_id=channel_id)
    return ytcrawler.get_all_uploads()


