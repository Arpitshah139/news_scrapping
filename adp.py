from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations
import hashlib

class adp(object):
    def __init__(self,url,body=None,headers= None):
        self.url = url
        self.body = body
        self.headers = headers

    def crawler_news(self):
        loop = True
        count = 25
        while loop:
            response = crawler.MakeRequest(self.url.format(count=count), 'Get', postData=self.body, headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            bulk_obj = DbOperations.Get_object_for_bulkop(False, 'adp_news')
            news_data = soup.find_all('li', {'class': "wd_item"})
            if news_data:
                for news in news_data:
                    news_dict = Helper.get_news_dict()

                    title_data = news.find('div', {'class', 'wd_title'})
                    title = title_data.text if title_data else ""

                    url_data = news.find('a', {'href': True})
                    url = url_data['href'] if url_data else ''

                    description_data = news.find('div', {'class': 'wd_summary'})
                    description = description_data.text if description_data else ''

                    publish_date_data = news.find('div', {'class': 'wd_date'})
                    publish_date = Helper.parse_date(publish_date_data.text) if publish_date_data and publish_date_data.text != '' else ''

                    news_dict.update(
                        {"title": title, "news_title_uid": hashlib.md5(title.encode()).hexdigest(),
                         "url": url, "link": url, "news_url_uid": hashlib.md5(url.encode()).hexdigest(),
                         "description": description, "text": description,
                         "publishedAt": publish_date, 'date': publish_date, "publishedAt_scrapped": publish_date,
                         "company_id": "adp", "ticker": "adp_scrapped", "industry_name": "adp",
                         "news_provider": "adp"})

                    bulk_obj.insert(news_dict)

                    if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 100:
                        bulk_obj.execute()
                        bulk_obj = DbOperations.Get_object_for_bulkop(False, 'adp_news')

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                    bulk_obj.execute()

                count += 25
            else:
                print("News Not Found")
                loop = False

url = "https://mediacenter.adp.com/latest-news?year=2020&l=25&o={count}"
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
news_obj = adp(url,headers=headers)
news_obj.crawler_news()