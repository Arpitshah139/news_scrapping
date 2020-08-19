from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations
import json
import re
import hashlib

class audi(object):
    def __init__(self,url,body=None,headers=None):
        self.url = url
        self.body = body
        self.headers = headers
    def crawler_news(self):
        loop = True
        page = 1
        while loop:
            response = crawler.MakeRequest(self.url.format(page=page),'Get',postData=self.body,headers=self.headers)
            if response.headers['Content-Type'] == 'application/json; charset=utf-8':
                response_json= json.loads(response.content.decode('utf-8'))
            else:
                print("No data found")
                break
            soup = BeautifulSoup(response_json['html'], 'html.parser')
            bulk_obj = DbOperations.Get_object_for_bulkop(False,'audi_news')
            news_data = soup.find_all('li',{'class':'page-list--item is-detailed infinite-nodes--list-item'})
            if news_data:
                for news in news_data:
                    news_dict = Helper.get_news_dict()

                    title_data = news.find('h3')
                    title = title_data.text.strip() if title_data else ""

                    url_data = news.find('a', {'href': True})
                    url = url_data['href'] if url_data else ''

                    publish_date_data = news.find('div',{'class':'meta--item'})
                    publish_date = Helper.parse_date(publish_date_data.text) if publish_date_data and publish_date_data.text != '' else ''

                    description_data = news.find('div', {'class': "page-list--text"})
                    description = description_data.text.strip() if description_data else ''

                    news_dict.update(
                        {"title": title, "news_title_uid": hashlib.md5(title.encode()).hexdigest(),
                         "url": url, "link": url, "news_url_uid": hashlib.md5(url.encode()).hexdigest(),
                         "description": description, "text": description,
                         "publishedAt": publish_date, 'date': publish_date, "publishedAt_scrapped": publish_date,
                         "company_id": "audi", "ticker": "audi_scrapped", "industry_name": "audi",
                         "news_provider": "audi"})

                    bulk_obj.insert(news_dict)

                    if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                        bulk_obj.execute()
                        bulk_obj = DbOperations.Get_object_for_bulkop(False,'audi_news')

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                    bulk_obj.execute()

                page += 1
            else:
                print("News Not Found")
                loop = False

url = "https://www.audi-mediacenter.com/en/press-releases?container_context=lg%2C1.0&next={page}"
news_obj = audi(url)
news_obj.crawler_news()