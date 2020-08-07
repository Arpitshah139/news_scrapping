from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations

class exxonmobil_corporation(object):
    def __init__(self,url,body=None):
        self.url = url
        self.body = body
    def crawler_news(self):
        loop = True
        page = 1
        while loop:
            response = crawler.MakeRequest(self.url.format(page=page),'Get',postData=self.body)
            soup = BeautifulSoup(response.content, 'html.parser')
            bulk_obj = DbOperations.Get_object_for_bulkop(False,'exxonmobil_corporation_news')
            news_data = soup.find_all('div', {'class': "contentCollection--item"})
            if news_data:
                for news in news_data:
                    news_dict = Helper.get_news_dict()

                    title_data = news.find('a')
                    title = title_data.text if title_data else ""

                    url_data = news.find('a', {'href': True})
                    url = "https://corporate.exxonmobil.com"+str(url_data['href']) if url_data else ''

                    description_data = news.find('span',{'class':'contentCollection--description p'})
                    description = description_data.text if description_data else ''

                    publish_date_data = news.find('span',{'class':'date'})
                    publish_date = Helper.parse_date(publish_date_data.text) if publish_date_data and publish_date_data.text != '' else ''

                    news_dict.update(
                        {"title": title, "url": url, "formatted_sub_header": title, "description": description, "link": url,
                         "publishedAt":publish_date,'date':publish_date,"news_provider": "exxonmobil corporation"})

                    bulk_obj.insert(news_dict)

                    if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                        bulk_obj.execute()
                        bulk_obj = DbOperations.Get_object_for_bulkop(False,'exxonmobil_corporation_news')

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                    bulk_obj.execute()

                page += 1

            else:
                print("News Not Found")
                loop = False

url = "https://corporate.exxonmobil.com/api/v2/related/collection?itemid=3f311ddd-4cb5-489b-a768-325e94ee0ef1&contextid=3f311ddd-4cb5-489b-a768-325e94ee0ef1&language=en&pagesize=5&page={page}"
news_obj = exxonmobil_corporation(url)
news_obj.crawler_news()