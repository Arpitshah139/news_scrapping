from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations
import hashlib
import json
import re

class novozymes(object):
    def __init__(self,url,body=None,headers=None):
        self.url = url
        self.body = body
        self.headers = headers
    def crawler_news(self):
        loop = True
        page = 0
        while loop:
            response = crawler.MakeRequest(self.url,'Post',postData=self.body.format(page=page),headers=self.headers)
            bulk_obj = DbOperations.Get_object_for_bulkop(False,'novozymes_news')
            news_data = json.loads(response.content.decode('utf-8'))
            if news_data['News']:
                for news in news_data['News']:
                    news_dict = Helper.get_news_dict()

                    title = news['Title'] if 'Title' in news  else ''

                    url = "https://www.novozymes.com"+str(news['Url']) if 'Url' in news else ''

                    publish_date_data = news['CreationDate'] if 'CreationDate' in news else ''
                    publish_date = Helper.parse_date(publish_date_data)

                    description = news['Content'] if 'Content' in news  else ''

                    news_dict.update(
                        {"title": title, "news_title_uid": hashlib.md5(title.encode()).hexdigest(),
                         "url": url, "link": url, "news_url_uid": hashlib.md5(url.encode()).hexdigest(),
                         "description": description, "text": description,
                         "publishedAt": publish_date, 'date': publish_date, "publishedAt_scrapped": publish_date,
                         "company_id": "novozymes", "ticker": "novozymes_scrapped", "industry_name": "novozymes",
                         "news_provider": "novozymes"})

                    bulk_obj.insert(news_dict)

                    if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                        bulk_obj.execute()
                        bulk_obj = DbOperations.Get_object_for_bulkop(False,'novozymes_news')

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                    bulk_obj.execute()

                page += 1
            else:
                print("News Not Found")
                loop = False

url = "https://www.novozymes.com/sitecore/api/news/list"
body = "{{\"pageNumber\":{page},\"pagesize\":10,\"tags\":[],\"query\":\"\"}}"
headers = {
    'accept': "application/json, text/plain, */*",
    'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
    'content-type': "application/json;charset=UTF-8",
    'sec-fetch-site': "same-origin",
    'sec-fetch-mode': "cors",
    'sec-fetch-dest': "empty",
    'cache-control': "no-cache",
    }
news_obj = novozymes(url,body,headers)
news_obj.crawler_news()