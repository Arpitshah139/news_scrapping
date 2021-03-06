from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations
import re
import hashlib

class f5(object):
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
            bulk_obj = DbOperations.Get_object_for_bulkop(False,'f5_news')
            news_data = soup.find_all('div', {'class': "a09-result__container"})
            if news_data:
                for news in news_data[:1]:
                    news_dict = Helper.get_news_dict()

                    title_data = news.find('a',{'class':'a09-result__content-title'})
                    title = title_data.text if title_data else ""

                    url_data = news.find('a', {'href': True})
                    url = "https://www.f5.com"+str(url_data['href']) if url_data else ''

                    publish_date_data = news.find('p',{'class':'a09-result__content-meta'})
                    publish_date = Helper.parse_date(str(publish_date_data.text).split('|')[1].strip()) if publish_date_data and publish_date_data.text != '' else ''

                    url_response = crawler.MakeRequest(url, 'Get', postData=self.body, headers=self.headers)
                    url_soup = BeautifulSoup(url_response.content, 'html.parser')
                    description_data = url_soup.find('div',{'class':"c29-columns__col c29-columns__col--two-wide"})

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
                         "company_id": "f5", "ticker": "f5_scrapped", "industry_name": "f5",
                         "news_provider": "f5"})

                    bulk_obj.insert(news_dict)

                    if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                        bulk_obj.execute()
                        bulk_obj = DbOperations.Get_object_for_bulkop(False,'f5_news')

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                    bulk_obj.execute()

                page += 1
            else:
                print("News Not Found")
                loop = False

url = "https://www.f5.com/company/news/press-releases/_jcr_content/root/responsivegrid/c29_columns_392319707/col1/a09_article_list_fil.results.{page}"
news_obj = f5(url)
news_obj.crawler_news()