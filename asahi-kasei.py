from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations
import hashlib
import json
import re

class asahi_kasei(object):
    def __init__(self,url,body=None,headers=None):
        self.url = url
        self.body = body
        self.headers = headers
    def crawler_news(self):
        response = crawler.MakeRequest(self.url,'Get',postData=self.body,headers=self.headers)
        bulk_obj = DbOperations.Get_object_for_bulkop(False,'asahi_kasei_news')
        news_data = json.loads(response.content.decode('utf-8'))
        if news_data:
            for news_list in news_data[0]['2020'][1]['release'][0]['mooth']:
                for news in news_list['item']:
                    news_dict = Helper.get_news_dict()

                    title = news['text'] if 'text' in news else ''

                    url = "https://www.asahi-kasei.com"+str(news['url']) if 'url' in news else ''

                    publish_date_data = news['day'] if 'day' in news else ''
                    publish_date = Helper.parse_date(publish_date_data)

                    url_response = crawler.MakeRequest(url, 'Get', postData=self.body, headers=self.headers)
                    url_soup = BeautifulSoup(url_response.content, 'html.parser')
                    description_data = url_soup.find('main', {'class': "main"})

                    description = []
                    regex = re.compile(r'[\n\xa0]')
                    for desc in description_data.find_all('p'):
                        description.append(regex.sub("", str(desc.text)))
                    description = ''.join(description)

                    news_dict.update(
                        {"title": title, "news_title_uid": hashlib.md5(title.encode()).hexdigest(),
                         "url": url, "link": url, "news_url_uid": hashlib.md5(url.encode()).hexdigest(),
                         "description": description, "text": description,
                         "publishedAt": publish_date, 'date': publish_date, "publishedAt_scrapped": publish_date,
                         "company_id": "asahi_kasei", "ticker": "asahi_kasei_scrapped", "industry_name": "asahi_kasei",
                         "news_provider": "asahi_kasei"})

                    bulk_obj.insert(news_dict)

                    if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                        bulk_obj.execute()
                        bulk_obj = DbOperations.Get_object_for_bulkop(False,'asahi_kasei_news')

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                    bulk_obj.execute()
        else:
            print("News Not Found")

url = "https://www.asahi-kasei.com/common/data/news.json?_=1598729128664"
news_obj = asahi_kasei(url)
news_obj.crawler_news()