import requests
from helper import Helper
import datetime
from bs4 import BeautifulSoup
from DbOps import *

class honey_well(object):
    def __init__(self,url):
        self.url = url
    def crawler_news(self):
        header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
            "Accept": "*/*"
        }
        response = requests.get(self.url, headers=header)
        soup = BeautifulSoup(response.content, 'html.parser')
        bulk_obj = DbOperations.Get_object_for_bulkop(False,'honey_well_news')
        for news in soup.find_all('div', {'class': "col-md-4 cg-item d-none"})[:4]:
            title_data = news.find('h4', {'class': "header5 give-ellipsis-after-3lines"})
            if title_data:
                title = title_data.text
            else:
                title = ""

            url_data = news.find('a', {'href': True})
            if url_data:
                url = "https://www.honeywell.com"+str(url_data['href'])
            else:
                url = ""

            url_response = requests.get(url,headers=header)
            url_soup_obj = BeautifulSoup(url_response.content, 'html.parser')
            description_data = url_soup_obj.find('meta',{'name':'description'})

            if description_data:
                description = description_data['content']
            else:
                description = ''
            news_dict = Helper.get_news_dict()
            news_dict.update({"tit"})

            bulk_obj.insert(news_dict)

            if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >2:
                bulk_obj.execute()
                bulk_obj = DbOperations.Get_object_for_bulkop(False,'honey_well_news')

        if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
            bulk_obj.execute()

url = "https://www.honeywell.com/en-us/news"
news_obj = honey_well(url)
news_obj.crawler_news()