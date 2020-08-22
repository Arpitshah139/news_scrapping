from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations
import hashlib
import json
import re

class tereos(object):
    def __init__(self,url,body=None,headers=None):
        self.url = url
        self.body = body
        self.headers = headers
    def crawler_news(self):
        loop = True
        page = 1
        while loop:
            response = crawler.MakeRequest(self.url.format(page=page),'Get',postData=self.body,headers=self.headers)
            bulk_obj = DbOperations.Get_object_for_bulkop(False,'tereos_news')
            news_data = json.loads(response.content.decode('utf-8'))
            if news_data:
                for news in news_data:
                    news_dict = Helper.get_news_dict()

                    title = news['title']['rendered'] if 'title' in news and 'rendered' in news['title'] else ''

                    url = news['link'] if 'link' in news else ''

                    publish_date_data = news['date_gmt'] if 'date_gmt' in news else ''
                    publish_date = Helper.parse_date(publish_date_data)

                    description_data = BeautifulSoup(news['acf']['sections'][0]['text'], 'html.parser')

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
                         "company_id": "tereos", "ticker": "tereos_scrapped", "industry_name": "tereos",
                         "news_provider": "tereos"})

                    bulk_obj.insert(news_dict)

                    if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                        bulk_obj.execute()
                        bulk_obj = DbOperations.Get_object_for_bulkop(False,'tereos_news')

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                    bulk_obj.execute()

                page += 1
            else:
                print("News Not Found")
                loop = False

url = "https://tereos.com/en/wp-json/wp/v2/multiple-post-type/?page={page}&per_page=5&type%5B%5D=news"
news_obj = tereos(url)
news_obj.crawler_news()