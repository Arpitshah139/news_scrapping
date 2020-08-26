from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations
import re
import hashlib

class trimble(object):
    def __init__(self,url,body=None,headers=None):
        self.url = url
        self.body = body
        self.headers = headers
    def crawler_news(self):
        response = crawler.MakeRequest(self.url,'Get',postData=self.body,headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        bulk_obj = DbOperations.Get_object_for_bulkop(False,'trimble_news')
        news_data = soup.find('div',{'class':'newslist'}).find_all('div', {'class': "newsDate"})
        if news_data:
            for news in news_data:
                news_dict = Helper.get_news_dict()

                title = news.find_next_sibling().text if news.find_next_sibling() else ''

                url = "https://www.trimble.com"+str(news.find_next_sibling()['href']) if news.find_next_sibling() else ''

                publish_date = Helper.parse_date(news.text) if news and news.text != '' else ''

                url_response = crawler.MakeRequest(url, 'Get', postData=self.body, headers=self.headers)
                url_soup = BeautifulSoup(url_response.content, 'html.parser')
                description_data = url_soup.find('div', {'class': "body"})

                description = []
                regex = re.compile(r'[\n\xa0]')
                for desc in description_data.find_all('div'):
                    description.append(regex.sub("", str(desc.text)))

                description = ''.join(description)

                news_dict.update(
                    {"title": title, "news_title_uid": hashlib.md5(title.encode()).hexdigest(),
                     "url": url, "link": url, "news_url_uid": hashlib.md5(url.encode()).hexdigest(),
                     "description": description, "text": description,
                     "publishedAt": publish_date, 'date': publish_date, "publishedAt_scrapped": publish_date,
                     "company_id": "trimble", "ticker": "trimble_scrapped", "industry_name": "trimble",
                     "news_provider": "trimble"})

                bulk_obj.insert(news_dict)

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                    bulk_obj.execute()
                    bulk_obj = DbOperations.Get_object_for_bulkop(False,'trimble_news')

            if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                bulk_obj.execute()
        else:
            print("News Not Found")

url = "https://www.trimble.com/webservices/NewsReleaseService.asmx/getLatestNewsHTML_EN?divList=00&year=2020&rowCount="
news_obj = trimble(url)
news_obj.crawler_news()