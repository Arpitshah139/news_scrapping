from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations
import hashlib
import json

class omron(object):
    def __init__(self,url,body=None,headers=None):
        self.url = url
        self.body = body
        self.headers = headers
    def crawler_news(self):
        loop = True
        while loop:
            response = crawler.MakeRequest(self.url,'Post',postData=self.body,headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            bulk_obj = DbOperations.Get_object_for_bulkop(False,'omron_news')
            news_data = json.loads(response.content.decode('utf-8'))
            if news_data:
                for news in news_data:
                    news_dict = Helper.get_news_dict()

                    title = news['Title'] if 'Title' in news else ''

                    publish_date_data = news['EntryDate'] if 'EntryDate' in news else ''
                    publish_date = Helper.parse_date(publish_date_data)

                    news_dict.update(
                        {"title": title, "news_title_uid": hashlib.md5(title.encode()).hexdigest(),
                         "publishedAt": publish_date, 'date': publish_date, "publishedAt_scrapped": publish_date,
                         "company_id": "omron", "ticker": "omron_scrapped", "industry_name": "omron",
                         "news_provider": "omron"})

                    bulk_obj.insert(news_dict)

                    if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                        bulk_obj.execute()
                        bulk_obj = DbOperations.Get_object_for_bulkop(False,'omron_news')

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                    bulk_obj.execute()

                self.body['StartRange'] += 1
            else:
                print("News Not Found")
                loop = False

url = "https://www.omron.co.in/admin-panel/PressReleasesWS.php?Action=SelectPressreleasesEntitiesFront"
body = {"Category":"Businesses",
        "EntryDate":2020,
        "PageSize":5,
        "SortExpression":"EntryDate DESC, PressreleasesID DESC, Title ASC",
        "StartRange":1}
news_obj = omron(url,body)
news_obj.crawler_news()