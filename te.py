from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations
import re
import requests
import hashlib
import sys

class te(object):
    def __init__(self,url,body=None,headers=None):
        self.url = url
        self.body = body
        self.headers = headers
    def crawler_news(self):
        loop = True
        while loop:
            response = requests.request("GET", self.url, headers=self.headers, params=self.body)
            soup = BeautifulSoup(response.content, 'html.parser')
            bulk_obj = DbOperations.Get_object_for_bulkop(False,'te_news')
            news_data = soup.find_all('div', {'class': "listing-single"})
            next_page_data = soup.find_all('a',{'class':'next disabled'})
            if news_data:
                for news in news_data[:1]:
                    news_dict = Helper.get_news_dict()

                    title_data = news.find('h3')
                    title = title_data.text if title_data else ""

                    url_data = news.find('a', {'href': True})
                    url = "https://www.te.com"+str(url_data['href']) if url_data else ''

                    publish_date_data = news.find('p',{'class':'resource-date'})
                    publish_date = Helper.parse_date(publish_date_data.text) if publish_date_data and publish_date_data.text != '' else ''

                    url_response = crawler.MakeRequest(url, 'Get', postData=self.body, headers=self.headers)
                    url_soup = BeautifulSoup(url_response.content, 'html.parser')
                    description_data = url_soup.find('div',{'class':"content-area rte-output"})

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
                         "company_id": "te", "ticker": "te_scrapped", "industry_name": "te",
                         "news_provider": "te"})

                    bulk_obj.insert(news_dict)

                    if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                        bulk_obj.execute()
                        bulk_obj = DbOperations.Get_object_for_bulkop(False,'te_news')

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                    bulk_obj.execute()

                if next_page_data:
                    loop = False
                else:
                    self.body['page'] += 1
            else:
                print("News Not Found")

url = "https://www.te.com/usa-en/about-te/news-center.html"

body = {"tab":"new-product-releases","page":1}

headers = {
    'upgrade-insecure-requests': "1",
    'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    'sec-fetch-site': "same-origin",
    'sec-fetch-mode': "navigate",
    'sec-fetch-user': "?1",
    'sec-fetch-dest': "document",
    'cache-control': "no-cache"
    }
news_obj = te(url,body,headers)
news_obj.crawler_news()