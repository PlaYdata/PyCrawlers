

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

def get_playlist_id_from_entry(one_playlist_data_entry):
    return one_playlist_data_entry["yt$playlistId"]["$t"]

def get_video_id_from_playlist_data_entry(one_entry):
#     return [xx for xx in one_entry["media$group"]["media$player"][0]["url"].split("?")[-1].split("&") if xx.startswith("v=")][0].replace("v=","")
    return [xx for xx in one_entry["link"] if xx["rel"] == "related"][0]["href"].split("/")[-1]

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
    def all_playlist_url(self):
        return "https://gdata.youtube.com/feeds/users/{channel_id}/playlists/".format(channel_id=self.channel_id)
    
    
    @property
    def uploads_url(self):
        return "https://gdata.youtube.com/feeds/users/{channel_id}/uploads/".format(channel_id=self.channel_id)
    
    
    def playlist_url(self, playlist_id):
        return "https://gdata.youtube.com/feeds/playlists/{playlist_id}".format(playlist_id=playlist_id)
    
    def get_all_uploads(self, entry_parser=summary_one_upload_data_entry):
        all_upload_data_list = []
        
        next_page_list = [self.uploads_url]
        print "next_page_list = ",next_page_list
        
        while len(next_page_list) > 0:

            upload_data = self._get_data(next_page_list[0])
            
            all_upload_data_list.extend(map(entry_parser, upload_data["feed"]["entry"]))
            next_page_list = [xx["href"] for xx in upload_data["feed"]["link"] if xx["rel"] == "next"]
            print "next_page_list = ",next_page_list
            
        return all_upload_data_list
            
    def get_all_playlist_ids(self, entry_parser=get_playlist_id_from_entry):
        all_playlist_ids_list = []
        
        next_page_list = [self.all_playlist_url]
        print "next_page_list = ",next_page_list
        
        while len(next_page_list) > 0:

            playlist_data = self._get_data(next_page_list[0])
            
            all_playlist_ids_list.extend(map(entry_parser, playlist_data["feed"]["entry"]))
            next_page_list = [xx["href"] for xx in playlist_data["feed"]["link"] if xx["rel"] == "next"]
            print "next_page_list = ",next_page_list
            
        return all_playlist_ids_list
    
    def get_one_playlist_all_video_ids(self, playlist_id, entry_parser=get_video_id_from_playlist_data_entry):
        all_video_ids_list = []
        
        next_page_list = [self.playlist_url(playlist_id=playlist_id)]
        print "next_page_list = ",next_page_list
        
        while len(next_page_list) > 0:

            playlist_data = self._get_data(next_page_list[0])
            
            all_video_ids_list.extend(map(entry_parser, playlist_data["feed"]["entry"]))
            next_page_list = [xx["href"] for xx in playlist_data["feed"]["link"] if xx["rel"] == "next"]
            print "next_page_list = ",next_page_list
            
        return all_video_ids_list
    
    
    def get_one_playlist_meta_data(self, playlist_id):
        playlist_data = self._get_data(self.playlist_url(playlist_id=playlist_id))
        
        return {"logo":playlist_data["feed"]["logo"]["$t"],
                "title":playlist_data["feed"]["title"]["$t"],
                "subtitle":playlist_data["feed"]["subtitle"]["$t"],
                "author":playlist_data["feed"]["author"][0]["name"]["$t"]}    
            
    
    def get_all_playlist_all_video_ids(self):
        all_playlist_ids = self.get_all_playlist_ids()
        results = []
        for one_id in all_playlist_ids:
            one_playlisy_data = {"playlist_id":one_id,
                                 "video_ids":self.get_one_playlist_all_video_ids(one_id)}
            one_playlisy_data.update(self.get_one_playlist_meta_data(one_id))
            results.append(one_playlisy_data)
        
        return results
        

def crawl_channel_uploads(channel_id):
    ytcrawler = YoutubeChannelOpenData(channel_id=channel_id)
    return ytcrawler.get_all_uploads()


def crawl_channel_playlists_data(channel_id):
    ytcrawler = YoutubeChannelOpenData(channel_id=channel_id)
    return ytcrawler.get_all_playlist_all_video_ids()



