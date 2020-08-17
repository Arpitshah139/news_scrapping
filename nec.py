from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations
import hashlib

class nec(object):
    def __init__(self,url,body=None,headers= None):
        self.url = url
        self.body = body
        self.headers = headers

    def crawler_news(self):
        response = crawler.MakeRequest(self.url,'Get',postData=self.body,headers=self.headers)
        soup = BeautifulSoup(response.content, 'xml')
        bulk_obj = DbOperations.Get_object_for_bulkop(False,'nec_news')
        news_data = soup.find_all('item')
        if news_data:
            for news in news_data:
                news_dict = Helper.get_news_dict()

                title_data = news.find('title')
                title = title_data.text if title_data else ""

                url_data = news.find('link')
                url = url_data.text if url_data else ''

                description_data = news.find('description')
                description = description_data.text if description_data else ''

                publish_date_data = news.find('pubDate')
                publish_date = Helper.parse_date(publish_date_data.text) if publish_date_data and publish_date_data.text != '' else ''

                news_dict.update(
                    {"title": title,"news_title_uid":hashlib.md5(title.encode()).hexdigest(),
                     "url": url,"link": url,"news_url_uid": hashlib.md5(url.encode()).hexdigest(),
                     "description": description,"text":description,
                     "publishedAt":publish_date,'date':publish_date,"publishedAt_scrapped":publish_date,
                     "company_id":"nec","ticker":"nec_scrapped","industry_name":"nec","news_provider": "nec"})

                bulk_obj.insert(news_dict)

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                    bulk_obj.execute()
                    bulk_obj = DbOperations.Get_object_for_bulkop(False,'nec_news')

            if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                bulk_obj.execute()

url = "https://www.nec.com/en/press/press.xml"
news_obj = nec(url)
news_obj.crawler_news()