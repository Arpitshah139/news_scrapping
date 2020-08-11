from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations

class denso(object):
    def __init__(self,url,body=None,headers= None):
        self.url = url
        self.body = body
        self.headers = headers

    def crawler_news(self):
        response = crawler.MakeRequest(self.url,'Get',postData=self.body,headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        bulk_obj = DbOperations.Get_object_for_bulkop(False,'denso_news')
        news_data_1 = soup.find_all('div', {'class': "menuBlock01--border menuBlock01--small menuBlock01  menuBlock01--right"})
        news_data_2 = soup.find_all('div', {'class': "menuBlock01--border menuBlock01--small menuBlock01 "})
        news_data = news_data_1 + news_data_2
        if news_data:
            for news in news_data:
                news_dict = Helper.get_news_dict()

                title_data = news.find('span',{"class":"menuBlock01__headingText"})
                title = title_data.text.strip() if title_data else ""

                url_data = news.find('a', {'href': True})
                url = "https://www.denso.com"+str(url_data['href']) if url_data else ''

                url_response = crawler.MakeRequest(url,'Get',postData=self.body,headers=self.headers)
                url_response_soup = BeautifulSoup(url_response.content, 'html.parser')
                description_data = url_response_soup.find('span',{'class':'heading01__copy heading01__copy--lead'})
                description = description_data.text.strip() if description_data else ''

                publish_date_data = news.find('p',{"class":"menuBlock01__text"})
                publish_date_data.span.decompose()
                publish_date = Helper.parse_date(publish_date_data.text) if publish_date_data and publish_date_data.text != '' else ''

                news_dict.update(
                    {"title": title, "url": url, "formatted_sub_header": title, "description": description, "link": url,
                     "publishedAt":publish_date,'date':publish_date,"news_provider": "denso"})

                bulk_obj.insert(news_dict)

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                    bulk_obj.execute()
                    bulk_obj = DbOperations.Get_object_for_bulkop(False,'denso_news')

            if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                bulk_obj.execute()

url = "https://www.denso.com/global/en/news/news-releases/2020/"
news_obj = denso(url)
news_obj.crawler_news()