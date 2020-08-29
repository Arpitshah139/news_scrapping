from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations
import re
import hashlib

class ahlstrom_munksjo(object):
    def __init__(self,url,body=None,headers=None):
        self.url = url
        self.body = body
        self.headers = headers
    def crawler_news(self):
        response = crawler.MakeRequest(self.url,'Get',postData=self.body,headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        bulk_obj = DbOperations.Get_object_for_bulkop(False,'ahlstrom_munksjo_news')
        news_data = soup.find('section', {'class': "content-area"})
        if news_data:
            for news in news_data.find_all('p'):
                news_dict = Helper.get_news_dict()

                title_data = news.find('a')
                title = title_data.text if title_data else ""

                url_data = news.find('a', {'href': True})
                url = "https://www.ahlstrom-munksjo.com"+str(url_data['href']) if url_data else ''
                news.a.decompose()
                publish_date = Helper.parse_date(news.text.strip()) if news and news.text != '' else ''

                url_response = crawler.MakeRequest(url, 'Get', postData=self.body, headers=self.headers)
                url_soup = BeautifulSoup(url_response.content, 'html.parser')
                description_data = url_soup.find('section',{'class':"content-area press-release-area "})

                description = []
                regex = re.compile(r'[\n\xa0]')
                for desc in description_data.find_all('p'):
                    description.append(regex.sub("", str(desc.text)))
                description= ''.join(description)

                news_dict.update(
                    {"title": title, "news_title_uid": hashlib.md5(title.encode()).hexdigest(),
                     "url": url, "link": url, "news_url_uid": hashlib.md5(url.encode()).hexdigest(),
                     "description": description, "text": description,
                     "publishedAt": publish_date, 'date': publish_date, "publishedAt_scrapped": publish_date,
                     "company_id": "ahlstrom_munksjo", "ticker": "ahlstrom_munksjo_scrapped", "industry_name": "ahlstrom_munksjo",
                     "news_provider": "ahlstrom_munksjo"})

                bulk_obj.insert(news_dict)

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                    bulk_obj.execute()
                    bulk_obj = DbOperations.Get_object_for_bulkop(False,'ahlstrom_munksjo_news')

            if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                bulk_obj.execute()

        else:
            print("News Not Found")

url = "https://www.ahlstrom-munksjo.com/Media/releases/press-releases2/2020/"
news_obj = ahlstrom_munksjo(url)
news_obj.crawler_news()