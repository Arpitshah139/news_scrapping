import datetime
from helper import Helper
import requests
from bs4 import BeautifulSoup
from crawler import *
import hashlib

class BD(object):

    def __init__(self,url):
        self.url = url

    def crawler(self):
        try:
            counter = 1
            data = []
            while True:

                response = crawler.MakeRequest(self.url,"Get")
                soup = BeautifulSoup(response.content, "html.parser")
                if response.status_code == 200:

                    boxs = soup.find_all("div",{"class":'item'})
                    for box in boxs:
                        date = Helper.parse_date(box.find("p",{"class":"fade"}).text)
                        if date:
                            if date.year < datetime.datetime.now().year:
                                break

                        datadict = Helper.get_news_dict()
                        datadict.update({"url":"https://www.bd.com/" + box.find("a")['href']})
                        description = self.fetchDescription("https://www.bd.com/" + box.find("a")['href'])
                        datadict.update({
                            "date": Helper.parse_date(box.find("p",{"class":"fade"}).text),
                            "news_provider": "Becton, Dickinson and Company",
                            "formatted_sub_header": box.find("a").text.strip(),
                            "publishedAt": Helper.parse_date(box.find("p",{"class":"fade"}).text),
                            "description": description,
                            "title": box.find("a").text.strip(),
                            "link": self.url,
                            "text":description,
                            "company_id" : "Becton, Dickinson and Company",
                            "news_url_uid" : hashlib.md5(("https://www.bd.com"+box.find("a")['href']).encode()).hexdigest()

                        })
                        data.append(datadict)
                else:
                    break
            DbOperations.InsertIntoMongo("bd_news",data)
        except Exception as e:
            print (e)

    def fetchDescription(self,url):
        article = ''
        try:
            # print(url)
            description = crawler.MakeRequest(url, "Get")
            articlesoup = BeautifulSoup(description.content, 'html.parser')
            # print(articlesoup)
            articlesoupobj = articlesoup.find("div",{"class":"container"})
            articles = articlesoupobj.find_all("p",attrs={'class': None})
            for art in articles:
                article += art.text + "\n"
        except Exception as e:
            print(e)
        return article
obj = BD('https://www.bd.com/en-us/company/news-and-media/press-releases?page=1')
obj.crawler()