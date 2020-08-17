import datetime
import hashlib
import json

from bs4 import BeautifulSoup

from crawler import *
from helper import Helper


class infineon(object):
    def __init__(self, url, body=None, headers=None):
        self.url = url
        self.body = body
        self.headers = headers

    def crawler_news(self):
        loop = True
        offset = 0
        while loop:
            bulk_obj = DbOperations.Get_object_for_bulkop(False, 'infineon_news')
            response = crawler.MakeRequest(self.url, 'Post', postData=self.body.format(off_set=offset),
                                           headers=self.headers)
            if response is not None:
                news_data = json.loads(response.content.decode('utf-8'))

                if news_data.__contains__('count') and news_data['count'] > 0:
                    for news in news_data['pages']['items']:
                        date = Helper.parse_date(news['news_date'])
                        if date:
                            date = Helper.parse_date(date)
                            if date.year < datetime.datetime.now().year:
                                break

                        news_dict = Helper.get_news_dict()
                        description = self.fetchDescription("https://www.infineon.com/" + news['url'])
                        news_dict.update(
                            {"date": Helper.parse_date(news['news_date']),
                             "news_provider": "Infineon",
                             "url": "https://www.infineon.com/" + news['url'],
                             "formatted_sub_header": "",
                             "publishedAt": Helper.parse_date(news['news_date']),
                             "description": description,
                             "title": news['title'],
                             "link": "https://www.infineon.com/" + news['url'],
                             "text": description,
                             "company_id": "Infineon",
                             "news_url_uid": hashlib.md5(
                                 ("https://www.infineon.com/" + news['url']).encode()).hexdigest()
                             })

                        bulk_obj.insert(news_dict)
                        if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 1:
                            bulk_obj.execute()
                            bulk_obj = DbOperations.Get_object_for_bulkop(False, 'infineon_news')
                else:
                    print("No data found")
                    loop = False
                offset += 1
                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                    bulk_obj.execute()

            else:
                break

    def fetchDescription(self, url):
        article = ''
        try:
            description = crawler.MakeRequest(url, "Get")
            articlesoup = BeautifulSoup(description.content, 'html.parser')
            articles = articlesoup.find("div", {"class": "copy"})
            for ar in articles.find_all("p"):
                article = article + " " + ar.text
        except Exception as e:
            print(e)
        return article


url = "https://www.infineon.com/cms/en/services/ajax/search/pressReleases"
news_obj = infineon(url,
                    "term=&offset={off_set}&max_results=10&lang=en&news_category_ids=news%2Fcategory%2Ffinancial-press%2F&news_category_ids=news%2Fcategory%2Fquarterly-report%2F&parent_folder=/en/",
                    {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                     "X-Requested-With": "XMLHttpRequest", "Accept": "application/json, text/javascript, */*; q=0.01"})
news_obj.crawler_news()
