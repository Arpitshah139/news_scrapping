from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations
import hashlib
import json

class fujielectric(object):
    def __init__(self,url,body=None,headers=None):
        self.url = url
        self.body = body
        self.headers = headers
    def crawler_news(self):
        response = crawler.MakeRequest(self.url,'Get',postData=self.body,headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        bulk_obj = DbOperations.Get_object_for_bulkop(False,'fujielectric_news')
        news_data = soup.find('div', {'id': 'tab_news_release'})
        if news_data:
            for news in news_data.find_all('dt'):
                news_dict = Helper.get_news_dict()

                title_data = news.find_next_sibling().find_next_sibling().a
                title = title_data.text if title_data else ""

                url_data = news.find_next_sibling().find_next_sibling().a
                url = url_data['href'] if url_data else ''

                publish_date_data = news.text if news.text != '' else ''
                publish_date = Helper.parse_date(publish_date_data)

                news_dict.update(
                    {"title": title, "news_title_uid": hashlib.md5(title.encode()).hexdigest(),
                     "url": url, "link": url, "news_url_uid": hashlib.md5(url.encode()).hexdigest(),
                     "publishedAt": publish_date, 'date': publish_date, "publishedAt_scrapped": publish_date,
                     "company_id": "fujielectric", "ticker": "fujielectric_scrapped", "industry_name": "fujielectric",
                     "news_provider": "fujielectric"})

                bulk_obj.insert(news_dict)

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                    bulk_obj.execute()
                    bulk_obj = DbOperations.Get_object_for_bulkop(False,'fujielectric_news')

            if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                bulk_obj.execute()
        else:
            print("News Not Found")

url = "https://www.fujielectric.com/company/news/2020.html"
news_obj = fujielectric(url)
news_obj.crawler_news()