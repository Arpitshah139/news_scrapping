from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations
import re
import hashlib

class polyone(object):
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
            bulk_obj = DbOperations.Get_object_for_bulkop(False,'polyone_news')
            news_data = soup.find('div',{'class':'block-region-results'})
            if news_data:
                for news in news_data.find_all('tr'):
                    news_dict = Helper.get_news_dict()

                    title_data = news.find('h3')
                    title = title_data.text if title_data else ""

                    url_data = news.find('a', {'href': True})
                    url = "https://www.polyone.com/"+str(url_data['href']) if url_data else ''

                    publish_date_data = news.find('h5',{'class':'float-left'})
                    publish_date = Helper.parse_date(str(publish_date_data.text).split('\n')[0]) if publish_date_data and publish_date_data.text != '' else ''

                    url_response = crawler.MakeRequest(url, 'Get', postData=self.body, headers=self.headers)
                    url_soup = BeautifulSoup(url_response.content, 'html.parser')
                    description_data = url_soup.find('div',{'class':"block-region-top"})
                    description_data = description_data.strong.find_all_previous('p')[1:-3]
                    description_data.reverse()

                    description = []
                    regex = re.compile(r'[\n\xa0]')
                    for desc in description_data:
                        description.append(regex.sub("", str(desc.text)))
                    description= ''.join(description)

                    news_dict.update(
                        {"title": title, "news_title_uid": hashlib.md5(title.encode()).hexdigest(),
                         "url": url, "link": url, "news_url_uid": hashlib.md5(url.encode()).hexdigest(),
                         "description": description, "text": description,
                         "publishedAt": publish_date, 'date': publish_date, "publishedAt_scrapped": publish_date,
                         "company_id": "polyone", "ticker": "polyone_scrapped", "industry_name": "polyone",
                         "news_provider": "polyone"})

                    bulk_obj.insert(news_dict)

                    if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                        bulk_obj.execute()
                        bulk_obj = DbOperations.Get_object_for_bulkop(False,'polyone_news')

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                    bulk_obj.execute()

                page += 1
                break
            else:
                print("News Not Found")
                loop = False

url = "https://www.polyone.com/news/archives?page={page}"
news_obj = polyone(url)
news_obj.crawler_news()