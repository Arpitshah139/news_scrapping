import datetime
from helper import Helper
import requests
from bs4 import BeautifulSoup
from crawler import *
import hashlib

class rtx(object):

    def __init__(self,url):
        self.url = url

    def crawler(self):
        try:
            page = 1
            bulk_obj = DbOperations.Get_object_for_bulkop(False, 'rtx_news')
            while True:
                response = crawler.MakeRequest(self.url.format(page=page),"Get")
                if 'we did not find any results related' in response.text:
                    break
                soup = BeautifulSoup(response.content, "html.parser")
                boxs = soup.find_all("li",{"class":'utc-cards--item'})
                for box in boxs:
                    date = box.find("time", {"class": "utc-card--date"}).text
                    if date:
                        date = Helper.parse_date(date)
                        if date.year < datetime.datetime.now().year:
                            break
                    datadict = Helper.get_news_dict()
                    datadict.update({"url":"https://www.rtx.com"+box.find("a")['href']})
                    description = self.fetchDescription("https://www.rtx.com" + box.find("a")['href'])
                    datadict.update({
                        "date": date,
                        "news_provider": "UNITED TECHNOLOGIES CORPORATION",
                        "formatted_sub_header": box.find("a").text,
                        "publishedAt": date,
                        "description": description,
                        "title": box.find("a").text,
                        "link": "https://www.rtx.com"+box.find("a")['href'],
                        "text":description,
                        "company_id" : "rtx",
                        "news_url_uid" : hashlib.md5(("https://www.rtx.com"+box.find("a")['href']).encode()).hexdigest()

                    })
                    print(datadict)
                    sys.exit()
                    bulk_obj.insert(datadict)

                    if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 100:
                        bulk_obj.execute()
                        bulk_obj = DbOperations.Get_object_for_bulkop(False, 'rtx_news')

            if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                bulk_obj.execute()
        except Exception as e:
            print (e)

    def fetchDescription(self,url):
        article = ''
        try:
            description = crawler.MakeRequest(url, "Get")
            articlesoup = BeautifulSoup(description.content, 'html.parser')
            article = articlesoup.find("div", {"class": "utc-container--content utc-article--content-text field-newscontentarea2"})
        except Exception as e:
            print(e)
        return article
obj = rtx('https://www.rtx.com/Overlays/NewsList?npagenum={page}')
obj.crawler()