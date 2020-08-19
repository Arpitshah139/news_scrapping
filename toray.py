from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations
import re
import hashlib

class toray(object):
    def __init__(self,url,body=None,headers=None):
        self.url = url
        self.body = body
        self.headers = headers
    def crawler_news(self):
        response = crawler.MakeRequest(self.url,'Get',postData=self.body,headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        bulk_obj = DbOperations.Get_object_for_bulkop(False,'toray_news')
        news_data = soup.find('div', {'id': "contents"})
        if news_data:
            for news in news_data.find_all('dt',{'class':'mgnT15'}):
                news_dict = Helper.get_news_dict()

                title_data = news.find_next_sibling().a
                title = title_data.text if title_data else ""

                url_data = news.find_next_sibling().a
                url = "https://www.toray.in/india/news/"+str(url_data['href']) if url_data else ''

                publish_date = Helper.parse_date(str(news.text).split('\n')[0]) if news and news.text != '' else ''

                url_response = crawler.MakeRequest(url, 'Get', postData=self.body, headers=self.headers)
                url_soup = BeautifulSoup(url_response.content, 'html.parser')
                description_data = url_soup.find_all('p',{'class':"mgnB20"})

                description = []
                regex = re.compile(r'[\n\xa0]')
                for desc in description_data:
                    description.append(regex.sub("", str(desc.text)))
                description= ''.join(description)

                news_dict.update(
                    {"title": title, "news_title_uid": hashlib.md5(title.encode()).hexdigest(),
                     "url": url, "link": url, "news_url_uid": hashlib.md5(url.encode()).hexdigest(),
                     "description": description, "text": description,
                     "publishedAt": publish_date, 'date': publish_date, "publishedAt_scrapped": publish_date,
                     "company_id": "toray", "ticker": "toray_scrapped", "industry_name": "toray",
                     "news_provider": "toray"})

                bulk_obj.insert(news_dict)

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                    bulk_obj.execute()
                    bulk_obj = DbOperations.Get_object_for_bulkop(False,'toray_news')

            if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                bulk_obj.execute()

url = "https://www.toray.in/india/news/index.html#/"
news_obj = toray(url)
news_obj.crawler_news()