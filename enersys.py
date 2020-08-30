from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations
import re
import hashlib

class enersys(object):
    def __init__(self,url,body=None,headers=None):
        self.url = url
        self.body = body
        self.headers = headers
    def crawler_news(self):
        response = crawler.MakeRequest(self.url,'Get',postData=self.body,headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        bulk_obj = DbOperations.Get_object_for_bulkop(False,'enersys_news')
        news_data = soup.find('div', {'class': "content-listing__items glide__slides"})
        if news_data:
            for news in news_data.find_all('a',{'class':'content-listing__item glide__slide col-lg-3 '}):
                news_dict = Helper.get_news_dict()
                regex = re.compile(r'[\r\n\xa0]')

                title_data = news.find('h3')
                title = regex.sub("", str(title_data.text.strip())) if title_data else ""

                url = "https://www.enersys.com"+str(news['href'])

                publish_date_data = news.find('p',{'class':'content-listing__item-date'})
                publish_date = Helper.parse_date(publish_date_data.text.strip()) if publish_date_data and publish_date_data.text != '' else ''

                url_response = crawler.MakeRequest(url, 'Get', postData=self.body, headers=self.headers)
                url_soup = BeautifulSoup(url_response.content, 'html.parser')
                description_data = url_soup.find('div',{'class':"standard-page__body"})

                description = []

                for desc in description_data.find_all('p'):
                    description.append(regex.sub("", str(desc.text)))
                description= ''.join(description)

                news_dict.update(
                    {"title": title, "news_title_uid": hashlib.md5(title.encode()).hexdigest(),
                     "url": url, "link": url, "news_url_uid": hashlib.md5(url.encode()).hexdigest(),
                     "description": description, "text": description,
                     "publishedAt": publish_date, 'date': publish_date, "publishedAt_scrapped": publish_date,
                     "company_id": "enersys", "ticker": "enersys_scrapped", "industry_name": "enersys",
                     "news_provider": "enersys"})

                bulk_obj.insert(news_dict)

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                    bulk_obj.execute()
                    bulk_obj = DbOperations.Get_object_for_bulkop(False,'enersys_news')

            if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                bulk_obj.execute()

        else:
            print("News Not Found")

url = "https://www.enersys.com/en/about-us/news/"
news_obj = enersys(url)
news_obj.crawler_news()