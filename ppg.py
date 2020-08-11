from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations
import json

class ppg(object):
    def __init__(self,url,body=None,headers= None):
        self.url = url
        self.body = body
        self.headers = headers

    def crawler_news(self):
        response = crawler.MakeRequest(self.url,'Get',postData=self.body,headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        bulk_obj = DbOperations.Get_object_for_bulkop(False,'ppg_news')
        news_data = json.loads(response.content.decode('utf-8'))
        if news_data:
            for news in news_data['GetPressReleaseListResult']:

                news_dict = Helper.get_news_dict()

                title = news['Headline'] if 'Headline' in news else ""
                url = news['LinkToUrl'] if 'LinkToUrl' in news else ""
                description = news['ShortBody'] if 'ShortBody' in news else ""
                news_url_uid = news['PressReleaseId'] if 'PressReleaseId' in news else ""
                publish_date = Helper.parse_date(news['PressReleaseDate']) if 'PressReleaseDate' in news else ""

                news_dict.update(
                    {"title": title, "url": url, "formatted_sub_header": title, "description": description, "link": url,
                     "publishedAt":publish_date,'date':publish_date,"news_url_uid":news_url_uid,"news_provider": "ppg"})

                bulk_obj.insert(news_dict)

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                    bulk_obj.execute()
                    bulk_obj = DbOperations.Get_object_for_bulkop(False,'ppg_news')

            if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                bulk_obj.execute()

url = "https://news.ppg.com/feed/PressRelease.svc/GetPressReleaseList?apiKey=BF185719B0464B3CB809D23926182246&LanguageId=1&bodyType=3&pressReleaseDateFilter=3&categoryId=953a78e4-99ff-4cc5-bfef-b5432b56da87&pageSize=-1&pageNumber=0&tagList=&includeTags=true&year=-1&excludeSelection=1"
news_obj = ppg(url)
news_obj.crawler_news()
