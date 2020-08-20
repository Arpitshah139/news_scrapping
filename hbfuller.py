from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations
import re
import hashlib

class hbfuller(object):
    def __init__(self,url,body=None,headers=None):
        self.url = url
        self.body = body
        self.headers = headers
    def crawler_news(self):
        loop = True
        page = 1
        while loop:
            try:
                response = crawler.MakeRequest(self.url.format(page=page),'Get',postData=self.body,headers=self.headers)
                soup = BeautifulSoup(response.content, 'html.parser')
                bulk_obj = DbOperations.Get_object_for_bulkop(False,'hbfuller_news')
                news_data = soup.find_all('div', {'class': "media"})
                if news_data:
                    for news in news_data:
                        news_dict = Helper.get_news_dict()

                        title_data = news.find('h4',{'class':'media-heading'})
                        title = title_data.text if title_data else ""

                        url_data = news.find('a', {'href': True})
                        url = "https://www.hbfuller.com"+str(url_data['href']) if url_data else ''

                        publish_date_data = news.find('div',{'class':'listing-date'})
                        publish_date = Helper.parse_date(str(publish_date_data.text).strip()) if publish_date_data and publish_date_data.text != '' else ''

                        url_response = crawler.MakeRequest(url, 'Get', postData=self.body, headers=self.headers)
                        url_soup = BeautifulSoup(url_response.content, 'html.parser')
                        description_data = url_soup.find('div',{'class':'row ar-body'}).find('div',{'class':"col-xs-12 col-sm-8 col-md-9"}).find('div',{'class':'col-sm-12'}).find('div',{'style':''})
                        description = description_data.text.strip().split('\n')
                        description= ''.join(description[1:])

                        news_dict.update(
                            {"title": title, "news_title_uid": hashlib.md5(title.encode()).hexdigest(),
                             "url": url, "link": url, "news_url_uid": hashlib.md5(url.encode()).hexdigest(),
                             "description": description, "text": description,
                             "publishedAt": publish_date, 'date': publish_date, "publishedAt_scrapped": publish_date,
                             "company_id": "hbfuller", "ticker": "hbfuller_scrapped", "industry_name": "hbfuller",
                             "news_provider": "hbfuller"})

                        bulk_obj.insert(news_dict)

                        if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                            bulk_obj.execute()
                            bulk_obj = DbOperations.Get_object_for_bulkop(False,'hbfuller_news')

                    if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                        bulk_obj.execute()

                    page += 1
                else:
                    print("News Not Found")
                    loop = False
            except AttributeError as e:
                print("News Not Found")
                loop = False

url = "https://www.hbfuller.com/en/north-america/news-and-events/press-releases?page={page}"
news_obj = hbfuller(url)
news_obj.crawler_news()