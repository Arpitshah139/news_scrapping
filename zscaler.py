from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations
import re
import hashlib

class zscaler(object):
    def __init__(self,url,body=None,headers=None):
        self.url = url
        self.body = body
        self.headers = headers
    def crawler_news(self):
        loop = True
        page = 1
        while loop:
            response = crawler.MakeRequest(self.url.format(page=page),'Get',postData=self.body,headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            bulk_obj = DbOperations.Get_object_for_bulkop(False,'zscaler_news')
            news_data = soup.find_all('div', {'class': "col-12 col-md-6 zpb-32 zpb-md-48"})
            if news_data:
                for news in news_data :
                    news_dict = Helper.get_news_dict()

                    title_data = news.find('a')
                    title = title_data.text if title_data else ""

                    url_data = news.find('a', {'href': True})
                    url = url_data['href'] if url_data else ''

                    publish_date_data = news.find('time', {'class': 'text-center bg-sea-green'})
                    publish_date = Helper.parse_date(publish_date_data.text) if publish_date_data and publish_date_data.text != '' else ''

                    url_response = crawler.MakeRequest(url, 'Get', postData=self.body, headers=self.headers)
                    url_soup = BeautifulSoup(url_response.content, 'html.parser')
                    description_data = url_soup.find_all('div',{'class':"col-sm-12"})

                    description = []
                    regex = re.compile(r'[\n\xa0]')
                    for desc in description_data:
                        if desc.find('a',{'href':'https://www.zscaler.com/'}) != None:
                            description.append(regex.sub("", str(desc.text)))
                    description= ''.join(description)

                    news_dict.update(
                        {"title": title, "news_title_uid": hashlib.md5(title.encode()).hexdigest(),
                         "url": url, "link": url, "news_url_uid": hashlib.md5(url.encode()).hexdigest(),
                         "description": description, "text": description,
                         "publishedAt": publish_date, 'date': publish_date, "publishedAt_scrapped": publish_date,
                         "company_id": "zscaler", "ticker": "zscaler_scrapped", "industry_name": "zscaler",
                         "news_provider": "zscaler"})

                    bulk_obj.insert(news_dict)

                    if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                        bulk_obj.execute()
                        bulk_obj = DbOperations.Get_object_for_bulkop(False,'zscaler_news')

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                    bulk_obj.execute()

                page += 1
            else:
                print("News Not Found")
                loop = False

url = "https://www.zscaler.com/press/2020?page={page}"
headers = {
    'accept': "application/json, text/javascript, */*; q=0.01",
    'x-requested-with': "XMLHttpRequest",
    'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
    'content-type': "application/json; charset=utf-8",
    'sec-fetch-site': "same-origin",
    'sec-fetch-mode': "cors",
    'sec-fetch-dest': "empty",
    'cache-control': "no-cache"
    }
news_obj = zscaler(url,headers=headers)
news_obj.crawler_news()