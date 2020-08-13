import datetime
from helper import Helper
import requests
from bs4 import BeautifulSoup
from crawler import *
import hashlib

class fujitsu(object):

    def __init__(self,url):
        self.url = url

    def crawler(self):
        try:
            response = crawler.MakeRequest(self.url,"Get")
            soup = BeautifulSoup(response.content, "html.parser")
            data = []
            boxs = soup.find_all("ul",{"class":'filterlist'})
            for box in boxs:
                date = ''.join(box.p.strong.text.split(',')[-2:])
                date = Helper.parse_date(date.lstrip().rstrip())
                datadict = Helper.get_news_dict()
                datadict.update({"url":"https://www.fujitsu.com"+box.find("a")['href']})
                description = self.fetchDescription("https://www.fujitsu.com" + box.find("a")['href'])
                datadict.update({
                    "date": date,
                    "news_provider": "fujitsu",
                    "formatted_sub_header": box.find("a").text,
                    "publishedAt": date,
                    "description": description,
                    "title": description,
                    "link": self.url,
                    "text":box.p.text,
                    "company_id" : "fujitsu",
                    "news_url_uid" : hashlib.md5(("https://www.fujitsu.com"+box.find("a")['href']).encode()).hexdigest()

                })
                data.append(datadict)

            DbOperations.InsertIntoMongo("fujitsu_news",data)
        except Exception as e:
            print (e)

    def fetchDescription(self,url):
        article = ''
        try:
            description = crawler.MakeRequest(url, "Get")
            articlesoup = BeautifulSoup(description.content, 'html.parser')
            articles = articlesoup.find("div", {"class": "bannercopy"})
            articles = articles.find_all("p")
            for ar in articles:
                article += ar.text + '\n'
        except Exception as e:
            print(e)
        return article
obj = fujitsu('https://www.fujitsu.com/global/about/resources/news/')
obj.crawler()