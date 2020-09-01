from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations
import hashlib
import json
import re
import sys

class zeiss(object):
    def __init__(self,url,body=None,headers=None):
        self.url = url
        self.body = body
        self.headers = headers
    def crawler_news(self):
        response = crawler.MakeRequest(self.url,'Get',postData=self.body,headers=self.headers)
        bulk_obj = DbOperations.Get_object_for_bulkop(False,'zeiss_news')
        news_data = json.loads(response.content.decode('utf-8'))
        if news_data:
            for news_id,news  in news_data['elements'].items():
                news_dict = Helper.get_news_dict()

                title = news['title'].strip() if 'title' in news  else ''

                url = "https://www.zeiss.com"+str(news['item_link']) if 'item_link' in news else ''

                publish_date_data = news['date'] if 'date' in news else ''
                publish_date = Helper.parse_date(publish_date_data) if publish_date_data != '' else ''

                description = news['description'] if 'description' in news  else ''

                news_dict.update(
                    {"title": title, "news_title_uid": hashlib.md5(title.encode()).hexdigest(),
                     "url": url, "link": url, "news_url_uid": hashlib.md5(url.encode()).hexdigest(),
                     "description": description, "text": description,
                     "publishedAt": publish_date, 'date': publish_date, "publishedAt_scrapped": publish_date,
                     "company_id": "zeiss", "ticker": "zeiss_scrapped", "industry_name": "zeiss",
                     "news_provider": "zeiss"})

                bulk_obj.insert(news_dict)

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                    bulk_obj.execute()
                    bulk_obj = DbOperations.Get_object_for_bulkop(False,'zeiss_news')

            if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                bulk_obj.execute()

        else:
            print("News Not Found")

url = "https://www.zeiss.com/corporate/int/newsroom/press-releases/_jcr_content/mainpar/section_97a8/sectionpar/column_control_266/column/columnpar/visibilitycontainer/wrapperpar/filter_4ebb.model.json"
news_obj = zeiss(url)
news_obj.crawler_news()