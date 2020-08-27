from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations
import hashlib
import json
import re

class brodcom(object):
    def __init__(self,url,body=None,headers=None):
        self.url = url
        self.body = body
        self.headers = headers
    def crawler_news(self):
        response = crawler.MakeRequest(self.url,'Get',postData=self.body,headers=self.headers)
        bulk_obj = DbOperations.Get_object_for_bulkop(False,'brodcom_news')
        news_data = json.loads(response.content.decode('utf-8'))
        if news_data:
            for news in news_data['NewsCategories'][0]['2020']:
                news_dict = Helper.get_news_dict()

                title = news['title'] if 'title' in news else ''

                url = news['_url_'] if '_url_' in news else ''
                link = "https://www.broadcom.com/"+str(news['_url_']) if '_url_' in news else ''

                publish_date_data = news['PublishDate'] if 'PublishDate' in news else ''
                publish_date = Helper.parse_date(publish_date_data)

                content_type = news['content_type'] if 'content_type' in news else ''
                cid = news['content_id'] if 'content_id' in news else ''
                final_url = "https://www.broadcom.com/api/getjsonbyurl?vanityurl={url}&locale=avg_en&updateddate=&ctype={content_type}&cid={cid}".format(
                    url=url, content_type=content_type, cid=cid)
                url_response = crawler.MakeRequest(final_url, 'Get', postData=self.body, headers=self.headers)
                url_json = json.loads(url_response.content.decode('utf-8'))
                url_soup = BeautifulSoup(url_json['Body'], 'html.parser')
                description = []
                regex = re.compile(r'[\n\xa0]')
                for desc in url_soup.find_all('p'):
                    description.append(regex.sub("", str(desc.text)))

                description = ''.join(description)

                news_dict.update(
                    {"title": title, "news_title_uid": hashlib.md5(title.encode()).hexdigest(),
                     "url": link, "link": link, "news_url_uid": hashlib.md5(link.encode()).hexdigest(),
                     "description": description, "text": description,
                     "publishedAt": publish_date, 'date': publish_date, "publishedAt_scrapped": publish_date,
                     "company_id": "brodcom", "ticker": "brodcom_scrapped", "industry_name": "brodcom",
                     "news_provider": "brodcom"})

                bulk_obj.insert(news_dict)

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                    bulk_obj.execute()
                    bulk_obj = DbOperations.Get_object_for_bulkop(False,'brodcom_news')

            if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                bulk_obj.execute()
        else:
            print("News Not Found")

url = "https://www.broadcom.com/api/news/productnews?id=1206560249947&type=AVG_News_P&locale=avg_en&years=10&locale=avg_en&lastpubdate=2020-08-27-17%3A45%3A29&updateddate=2020-07-16-18%3A13%3A11"
news_obj = brodcom(url)
news_obj.crawler_news()