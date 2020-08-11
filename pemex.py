import datetime
from helper import Helper
import requests
from bs4 import BeautifulSoup
from crawler import *
import hashlib

class pemex(object):

    def __init__(self,url):
        self.url = url

    def crawler(self):
        try:
            response = crawler.MakeRequest(self.url,"Get")
            soup = BeautifulSoup(response.content, "html.parser")
            data = []
            boxs = soup.find_all("div",{"class":'news-box span3 left'})
            for box in boxs:
                datadict = Helper.get_news_dict()
                datadict.update({"url":"https://www.pemex.com"+box.find("a")['href']})
                print(hashlib.md5("https://www.pemex.com"+box.find("a")['href'].encode()).hexdigest())
                sys.exit()
                description = self.fetchDescription("https://www.pemex.com" + box.find("a")['href'])
                datadict.update({
                    "date": box.find("p",{"class":"news-meta news-date"}).text,
                    "news_provider": "pemex",
                    "formatted_sub_header": box.find("div",{"class":"ms-WPBody h2"}).text,
                    "publishedAt": Helper.parse_date(box.find("p",{"class":"news-meta news-date"}).text),
                    "description": description,
                    "title": box.find("div",{"class":"ms-WPBody h2"}).text,
                    "link": self.url,
                    "text":description,
                    "company_id" : "pemex",
                    "news_url_uid" : hashlib.md5("https://www.pemex.com"+box.find("a")['href'].encode()).hexdigest()

                })
                data.append(datadict)

            DbOperations.InsertIntoMongo("pemex_news",data)
        except Exception as e:
            print (e)

    def fetchDescription(self,url):
        article = ''
        try:
            description = crawler.MakeRequest(url, "Get")
            articlesoup = BeautifulSoup(description.content, 'html.parser')
            article = articlesoup.find("div", {"class": "article-content"}).text
        except Exception as e:
            print(e)
        return article
obj = pemex('https://www.pemex.com/en/Paginas/default.aspx')
obj.crawler()