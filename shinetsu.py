from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations
import hashlib
import re
import json

class shinetsu(object):
    def __init__(self,url,body=None,headers=None):
        self.url = url
        self.body = body
        self.headers = headers
    def crawler_news(self):
        response = crawler.MakeRequest(self.url,'Post',postData=self.body,headers=self.headers)
        news_json = json.loads(response.content.decode('utf-8'))
        if news_json:
            soup = BeautifulSoup(news_json['data'], 'html.parser')
            bulk_obj = DbOperations.Get_object_for_bulkop(False,'shinetsu_news')
            news_data = soup.find_all('div', {'class': "item"})
            if news_data:
                for news in news_data:
                    news_dict = Helper.get_news_dict()

                    title_data = news.find('div',{'class':'title'})
                    title = title_data.text.strip().split('\n')[0] if title_data else ""

                    url_data = news.find('a', {'href': True})
                    url = url_data['href'] if url_data else ''

                    publish_date_data = news.find('p',{'class':'date'})
                    publish_date = Helper.parse_date(publish_date_data.text) if publish_date_data and publish_date_data.text != '' else ''

                    if url.split('.')[-1] != 'pdf':
                        url_response = crawler.MakeRequest(url, 'Get', postData=self.body, headers=self.headers)
                        url_soup = BeautifulSoup(url_response.content, 'html.parser')
                        description_data = url_soup.find('div', {'class': "content-news"})

                        description = []
                        regex = re.compile(r'[\n\xa0]')
                        for desc in description_data.find_all('p'):
                            description.append(regex.sub("", str(desc.text)))
                        description = ''.join(description)
                    else:
                        description =  ''

                    news_dict.update(
                        {"title": title, "news_title_uid": hashlib.md5(title.encode()).hexdigest(),
                         "url": url, "link": url, "news_url_uid": hashlib.md5(url.encode()).hexdigest(),
                         "description": description, "text": description,
                         "publishedAt": publish_date, 'date': publish_date, "publishedAt_scrapped": publish_date,
                         "company_id": "shinetsu", "ticker": "shinetsu_scrapped", "industry_name": "shinetsu",
                         "news_provider": "shinetsu"})

                    bulk_obj.insert(news_dict)

                    if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                        bulk_obj.execute()
                        bulk_obj = DbOperations.Get_object_for_bulkop(False,'shinetsu_news')

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                    bulk_obj.execute()

            else:
                print("News Not Found")

url = "https://www.shinetsu.co.jp/wp-admin/admin-ajax.php"
body = {'action':'shinetsu_get_last_news','id':985,'num':3}
news_obj = shinetsu(url,body)
news_obj.crawler_news()