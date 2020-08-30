from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations
import re
import hashlib

class titanx(object):
    def __init__(self,url,body=None,headers=None):
        self.url = url
        self.body = body
        self.headers = headers
    def crawler_news(self):
        loop = True
        page = 1
        while loop:
            response = crawler.MakeRequest(self.url.format(page=page),'Get',postData=self.body,headers=self.headers)
            if (response.status_code == 200):
                soup = BeautifulSoup(response.content, 'html.parser')
            else:
                break
            bulk_obj = DbOperations.Get_object_for_bulkop(False,'titanx_news')
            news_data = soup.find('div', {'class': "x-main full"}).find_all('div',{'class':'x-container max width'})
            if news_data:
                for news in news_data:
                    news_dict = Helper.get_news_dict()

                    title_data = news.find('h2',{'class':'entry-title'})
                    title = title_data.text.strip() if title_data else ""

                    url_data = news.find('a', {'href': True})
                    url = url_data['href'] if url_data else ''

                    publish_date_data = news.find('time',{'class':'entry-date'})
                    publish_date = Helper.parse_date(publish_date_data.text) if publish_date_data and publish_date_data.text != '' else ''

                    url_response = crawler.MakeRequest(url, 'Get', postData=self.body, headers=self.headers)
                    url_soup = BeautifulSoup(url_response.content, 'html.parser')
                    description_data = url_soup.find('div',{'class':"entry-content content"})

                    description = []
                    regex = re.compile(r'[\n\xa0]')
                    if description_data.h2 != None:
                        for desc in description_data.h2.find_all_previous("p")[::-1]:
                            description.append(regex.sub("", str(desc.text)))
                    else:
                        for desc in description_data.find_all('p'):
                            description.append(regex.sub("", str(desc.text)))
                    description= ''.join(description)
                    print(description)
                    print(title)
                    print(url)
                    print(publish_date)

                    news_dict.update(
                        {"title": title, "news_title_uid": hashlib.md5(title.encode()).hexdigest(),
                         "url": url, "link": url, "news_url_uid": hashlib.md5(url.encode()).hexdigest(),
                         "description": description, "text": description,
                         "publishedAt": publish_date, 'date': publish_date, "publishedAt_scrapped": publish_date,
                         "company_id": "titanx", "ticker": "titanx_scrapped", "industry_name": "titanx",
                         "news_provider": "titanx"})

                    bulk_obj.insert(news_dict)

                    if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                        bulk_obj.execute()
                        bulk_obj = DbOperations.Get_object_for_bulkop(False,'titanx_news')

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                    bulk_obj.execute()

                page += 1
            else:
                print("News Not Found")
                loop = False

url = "http://titanx.com/blog/page/{page}/"
news_obj = titanx(url)
news_obj.crawler_news()