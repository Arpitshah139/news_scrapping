import datetime
from helper import Helper
import requests
from bs4 import BeautifulSoup
from crawler import *
import hashlib

class qp(object):

    def __init__(self,url):
        self.url = url

    def crawler(self):
        try:
            response = crawler.MakeRequest(self.url,"Get")
            soup = BeautifulSoup(response.content, "html.parser")
            data = []
            boxs = soup.find_all("div",{"class":'rowBlock newsRowBlock'})
            for box in boxs:
                datadict = Helper.get_news_dict()
                datadict.update({"url":"https://qp.com.qa/en/MediaCentre/pages/News.aspx"})
                datadict.update({
                    "date": Helper.parse_date(box.find("p",{"class":"articleDate"}).text),
                    "news_provider": "Qatar Pertrolium",
                    "formatted_sub_header": box.find("p",{"class":"articleTitle"}).text,
                    "publishedAt": Helper.parse_date(box.find("p",{"class":"articleDate"}).text),
                    "description": box.find("div",{"class":"articleData clearfix"}).text,
                    "title": box.find("p",{"class":"articleTitle"}).text,
                    "link": self.url,
                    "text":box.find("div",{"class":"articleData clearfix"}).text,
                    "company_id" : "Qatar Pertrolium",
                    "news_url_uid" : hashlib.md5(("https://qp.com.qa/en/MediaCentre/pages/News.aspx").encode()).hexdigest()

                })
                data.append(datadict)

            DbOperations.InsertIntoMongo("qp_news",data)
        except Exception as e:
            print (e)

obj = qp('https://qp.com.qa/en/MediaCentre/pages/News.aspx')
obj.crawler()