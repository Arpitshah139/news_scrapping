import requests
from helper import Helper
from DbOps import *
import json

class abb(object):
    def __init__(self,url):
        self.url = url
    def crawler_news(self):
        header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
            "Accept": "*/*"
        }

        loop = True
        offset = 1
        while loop:
            bulk_obj = DbOperations.Get_object_for_bulkop(False, 'abb_news')
            response = requests.get(self.url.format(off_set=offset), headers=header)
            news_data = json.loads(response.content.decode('utf-8'))

            # check if we found any news data or not
            if news_data.__contains__('count') and news_data['count'] > 0:
                for news in news_data['news']:
                    print (news)
                    news_dict = Helper.get_news_dict()
                    news_dict.update(
                        {"title": news['title'], "url": "https://new.abb.com/" + news['path'], "formatted_sub_header": news['title'],
                         "description": news['description'],"text":news['description'],
                         "publishedAt":Helper.parse_date(news['publishedOn']), "date": news['publishedOn'],
                         "link": "https://new.abb.com/" + news['path'], "news_provider": "abb"})
                    bulk_obj.insert(news_dict)
                    if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 1:
                        bulk_obj.execute()
                        bulk_obj = DbOperations.Get_object_for_bulkop(False, 'abb_news')
            else:
                print("No data found")
                loop = False
            offset += 1
            if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                bulk_obj.execute()

url = "https://global.abb/group/en/media/releases/group.abbglobal-news-search.json?feeds=abb:feeds/group_functions/corporate_communications/group_press_releases&feedsOperator=OR&limit=10&offset={off_set}"
news_obj = abb(url)
news_obj.crawler_news()