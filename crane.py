from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations
import re
import json
import hashlib

class crane(object):
    def __init__(self,url,body=None,headers=None):
        self.url = url
        self.body = body
        self.headers = headers
    def crawler_news(self):
        response = crawler.MakeRequest(self.url,'Get',postData=self.body,headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        bulk_obj = DbOperations.Get_object_for_bulkop(False,'crane_news')
        news_data = json.loads(response.content.decode('utf-8'))
        if news_data:
            for news in news_data['GetPressReleaseListResult']:
                news_dict = Helper.get_news_dict()

                title = news['Headline'] if 'Headline' in news else ""

                url = "https://www.craneco.com"+str(news['LinkToDetailPage']) if 'LinkToDetailPage' in news else ''

                publish_date = Helper.parse_date(news['PressReleaseDate']) if 'PressReleaseDate' in news else ''

                url_response = crawler.MakeRequest(url, 'Get', postData=self.body, headers=self.headers)
                url_soup = BeautifulSoup(url_response.content, 'html.parser')
                description_data = url_soup.find('div',{'class':"module_body clearfix"})

                description = []
                regex = re.compile(r'[\n\xa0]')
                for desc in description_data.find_all('p'):
                    description.append(regex.sub("", str(desc.text)))
                description= ''.join(description)

                news_dict.update(
                    {"title": title, "news_title_uid": hashlib.md5(title.encode()).hexdigest(),
                     "url": url, "link": url, "news_url_uid": hashlib.md5(url.encode()).hexdigest(),
                     "description": description, "text": description,
                     "publishedAt": publish_date, 'date': publish_date, "publishedAt_scrapped": publish_date,
                     "company_id": "crane", "ticker": "crane_scrapped", "industry_name": "crane",
                     "news_provider": "crane"})

                bulk_obj.insert(news_dict)

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                    bulk_obj.execute()
                    bulk_obj = DbOperations.Get_object_for_bulkop(False,'crane_news')

            if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                bulk_obj.execute()
        else:
            print("News Not Found")

url = "https://www.craneco.com/feed/PressRelease.svc/GetPressReleaseList?apiKey=BF185719B0464B3CB809D23926182246&LanguageId=1&bodyType=0&pressReleaseDateFilter=3&categoryId=1cb807d2-208f-4bc3-9133-6a9ad45ac3b0&pageSize=-1&pageNumber=0&tagList=&includeTags=true&year=2020&excludeSelection=1"
news_obj = crane(url)
news_obj.crawler_news()