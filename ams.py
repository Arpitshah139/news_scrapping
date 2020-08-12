from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations
import hashlib

class ams(object):
    def __init__(self,url,body=None,headers= None):
        self.url = url
        self.body = body
        self.headers = headers

    def crawler_news(self):
        response = crawler.MakeRequest(self.url,'Get',postData=self.body,headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        bulk_obj = DbOperations.Get_object_for_bulkop(False,'ams_news')
        news_data = soup.find_all('div', {'class': "col-md-4 col-sm-8 col-sm-offset-2 col-md-offset-0"})
        if news_data:
            for news in news_data:
                news_dict = Helper.get_news_dict()

                title_data = news.find('h3',{"class":"info-box__title"})
                title = title_data.text.strip() if title_data else ""

                url_data = news.find('a', {'href': True})
                url = "https://www.ams.com"+str(url_data['href']) if url_data else ''

                description_data = news.find('div',{'class':"info-box__content"}).find('p')
                description = description_data.text if description_data else ''

                publish_date_data = news.find('p',{"class":"info-box__date"})
                publish_date = Helper.parse_date(publish_date_data.text) if publish_date_data and publish_date_data.text != '' else ''

                news_dict.update(
                    {"title": title,"news_title_uid":hashlib.md5(title.encode()).hexdigest(),
                     "url": url,"link": url,"news_url_uid": hashlib.md5(url.encode()).hexdigest(),
                     "description": description,"text":description,
                     "publishedAt":publish_date,'date':publish_date,"publishedAt_scrapped":publish_date,
                     "company_id":"ams","ticker":"ams_scrapped","industry_name":"ams","news_provider": "ams"})

                bulk_obj.insert(news_dict)

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                    bulk_obj.execute()
                    bulk_obj = DbOperations.Get_object_for_bulkop(False,'ams_news')

            if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                bulk_obj.execute()

url = "https://ams.com/pressreleases-2020"
news_obj = ams(url)
news_obj.crawler_news()