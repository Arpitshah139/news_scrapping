from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations
import hashlib

class voestalpine(object):
    def __init__(self,url,body=None,headers= None):
        self.url = url
        self.body = body
        self.headers = headers

    def crawler_news(self):
        response = crawler.MakeRequest(self.url,'Get',postData=self.body,headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        bulk_obj = DbOperations.Get_object_for_bulkop(False,'voestalpine_news')
        article_data = soup.find_all('div',{'class':'article'})
        if article_data:
            for article in article_data:
                news_data = article.find_all('section',{'class':""})
                for news in news_data[1::2]:

                    news_dict = Helper.get_news_dict()

                    title_data = news.find('h2')
                    title = title_data.text if title_data else ""

                    url = news.find_next_sibling().a['href'] if news.find_next_sibling() else ''

                    description_data = news.find('p')
                    description = description_data.text if description_data else ''

                    url_response = crawler.MakeRequest(url,'Get',postData=self.body,headers=self.headers)
                    url_soup = BeautifulSoup(url_response.content, 'html.parser')
                    publish_date_data = url_soup.find('p',{'class':'meta large inline'})
                    publish_date = Helper.parse_date(publish_date_data.text.replace('|',"").strip()) if publish_date_data and publish_date_data.text != '' else ''

                    news_dict.update(
                        {"title": title, "news_title_uid": hashlib.md5(title.encode()).hexdigest(),
                         "url": url, "link": url, "news_url_uid": hashlib.md5(url.encode()).hexdigest(),
                         "description": description, "text": description,
                         "publishedAt": publish_date, 'date': publish_date, "publishedAt_scrapped": publish_date,
                         "company_id": "voestalpine", "ticker": "voestalpine_scrapped", "industry_name": "voestalpine", "news_provider": "voestalpine"})

                    bulk_obj.insert(news_dict)

                    if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                        bulk_obj.execute()
                        bulk_obj = DbOperations.Get_object_for_bulkop(False,'voestalpine_news')

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                    bulk_obj.execute()

url = "https://www.voestalpine.com/group/en/media/press-releases/latest-news/"
news_obj = voestalpine(url)
news_obj.crawler_news()