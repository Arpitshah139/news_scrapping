import datetime
from helper import Helper
import requests
from bs4 import BeautifulSoup
from crawler import *
import hashlib

class adlinktech(object):

    def __init__(self,url):
        self.url = url

    def crawler(self):
        try:
            bulk_obj = DbOperations.Get_object_for_bulkop(False, 'adlinktech_news')
            response = crawler.MakeRequest(self.url,"Get")
            soup = BeautifulSoup(response.content, "html.parser")
            boxs = soup.find_all("div",{"class":'listCol sort-item news-item'})
            for box in boxs:
                datadict = Helper.get_news_dict()
                datadict.update({"url":"https://www.adlinktech.com"+box.find("a")['href']})
                date,description = self.fetchDescription("https://www.adlinktech.com" + box.find("a")['href'])
                datadict.update({
                    "date": Helper.parse_date(date),
                    "news_provider": "ADLINK TECHNOLOGY INC.",
                    "formatted_sub_header": box.find("div",{"class":"contentText"}).text,
                    "publishedAt": Helper.parse_date(date),
                    "description": description,
                    "title": box.find("div",{"class":"contentText"}).text,
                    "link": "https://www.adlinktech.com"+box.find("a")['href'],
                    "text":description,
                    "company_id" : "adlinktech",
                    "news_url_uid" : hashlib.md5(("https://www.adlinktech.com"+box.find("a")['href']).encode()).hexdigest()

                })
                bulk_obj.insert(datadict)

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 100:
                    bulk_obj.execute()
                    bulk_obj = DbOperations.Get_object_for_bulkop(False, 'adlinktech_news')

            if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                bulk_obj.execute()
        except Exception as e:
            print (e)

    def fetchDescription(self,url):
        article = ''
        date = ''
        try:
            description = crawler.MakeRequest(url, "Get")
            articlesoup = BeautifulSoup(description.content, 'html.parser')
            date = articlesoup.find("div", {"class": "newsPage-date floatL"}).text
            article = articlesoup.find("div", {"class": "contentText"}).text

        except Exception as e:
            print(e)
        return date,article
obj = adlinktech('https://www.adlinktech.com/en/CompanyNews')
obj.crawler()