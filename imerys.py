from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations
import hashlib

class imerys(object):
    def __init__(self,url,body=None,headers=None):
        self.url = url
        self.body = body
        self.headers = headers
    def crawler_news(self):
        loop = True
        page = 0
        while loop:
            response = crawler.MakeRequest(self.url.format(page=page),'Get',postData=self.body,headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            bulk_obj = DbOperations.Get_object_for_bulkop(False,'imerys_news')
            news_data = soup.find_all('div', {'class': "documents-list__item"})
            if news_data:
                for news in news_data:
                    news_dict = Helper.get_news_dict()

                    title_data = news.find('a')
                    title = title_data.text if title_data else ""

                    url_data = news.find('a', {'href': True})
                    url = url_data['href'] if url_data else ''

                    publish_date_data = news.find('div',{'class':'documents-list__item__date'})
                    publish_date = Helper.parse_date(publish_date_data.text) if publish_date_data and publish_date_data.text != '' else ''

                    news_dict.update(
                        {"title": title, "news_title_uid": hashlib.md5(title.encode()).hexdigest(),
                         "url": url, "link": url, "news_url_uid": hashlib.md5(url.encode()).hexdigest(),
                         "publishedAt": publish_date, 'date': publish_date, "publishedAt_scrapped": publish_date,
                         "company_id": "imerys", "ticker": "imerys_scrapped", "industry_name": "imerys",
                         "news_provider": "imerys"})

                    bulk_obj.insert(news_dict)

                    if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                        bulk_obj.execute()
                        bulk_obj = DbOperations.Get_object_for_bulkop(False,'imerys_news')

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                    bulk_obj.execute()

                page += 1
            else:
                print("News Not Found")
                loop = False

url = "https://www.imerys.com/media-center?f%5B0%5D=y%3A2020&search=&sort_by=created&sort_order=DESC&page={page}"
news_obj = imerys(url)
news_obj.crawler_news()