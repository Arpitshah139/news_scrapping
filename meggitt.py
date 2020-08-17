from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations
import re
import hashlib

class meggitt(object):
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
            bulk_obj = DbOperations.Get_object_for_bulkop(False,'meggitt_news')
            news_data = soup.find_all('div', {'class': "news_list_item"})
            if news_data:
                for news in news_data:
                    news_dict = Helper.get_news_dict()

                    title_data = news.find('h4')
                    title = title_data.text if title_data else ""
                    print(title)

                    url_data = news.find('a', {'href': True})
                    url = url_data['href'] if url_data else ''
                    print(url)

                    publish_date_data = news.find('h5')
                    publish_date_data.span.decompose()
                    publish_date = Helper.parse_date(str(publish_date_data.text).split('\n')[0]) if publish_date_data and publish_date_data.text != '' else ''
                    print(publish_date)

                    url_response = crawler.MakeRequest(url, 'Get', postData=self.body, headers=self.headers)
                    url_soup = BeautifulSoup(url_response.content, 'html.parser')
                    description_data = url_soup.find('div',{'class':"pf-content"})

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
                         "company_id": "meggitt", "ticker": "meggitt_scrapped", "industry_name": "meggitt",
                         "news_provider": "meggitt"})

                    bulk_obj.insert(news_dict)

                    if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                        bulk_obj.execute()
                        bulk_obj = DbOperations.Get_object_for_bulkop(False,'meggitt_news')

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                    bulk_obj.execute()

                page += 1
            else:
                print("News Not Found")
                loop = False

url = "https://www.meggitt.com/news/?_sfm_year=2020&sf_paged={page}"
news_obj = meggitt(url)
news_obj.crawler_news()