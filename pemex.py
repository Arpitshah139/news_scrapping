import datetime
from helper import Helper
import requests
from bs4 import BeautifulSoup
from DbOps import DbOperations
class pemex(object):

    def __init__(self,url):
        self.url = url

    @staticmethod
    def MakeRequest(url, requestType, postData=None):
        response = None
        try:
            headers = {}
            headers.update({'Accept': 'application/json, text/plain, */*'})
            headers.update({'Accept-Encoding': 'gzip, deflate, br'})
            headers.update({'Accept-Language': 'en-US,en;q=0.9'})
            headers.update({'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0'})

            if (requestType == "Post"):

                response = requests.post(url, data=postData, headers=headers, verify=False)

            else:

                response = requests.get(url, headers=headers, verify=False)

        except Exception as e:
            print(e)
        return response


    def crawler(self):
        try:
            response = self.MakeRequest(self.url,"Get")
            soup = BeautifulSoup(response.content, "html.parser")
            data = []
            boxs = soup.find_all("div",{"class":'news-box span3 left'})
            for box in boxs:
                datadict = Helper.get_news_dict()
                datadict.update({"newsurl":"https://www.pemex.com"+box.find("a")['href']})
                description = self.fetchDescription("https://www.pemex.com" + box.find("a")['href'])
                datadict.update({
                    "url": self.url,
                    "date": box.find("p",{"class":"news-meta news-date"}).text,
                    "news_provider": "pemex",
                    "formatted_sub_header": box.find("div",{"class":"ms-WPBody h2"}).text,
                    "publishedAt": box.find("p",{"class":"news-meta news-date"}).text,
                    "description": description,
                    "title": box.find("div",{"class":"ms-WPBody h2"}).text,
                    "link": self.url
                })
                data.append(datadict)

            DbOperations.InsertIntoMongo("pemex_news",data)
        except Exception as e:
            print (e)

    def fetchDescription(self,url):
        article = ''
        try:
            description = self.MakeRequest(url, "Get")
            articlesoup = BeautifulSoup(description.content, 'html.parser')
            article = articlesoup.find("div", {"class": "article-content"}).text
        except Exception as e:
            print(e)
        return article
obj = pemex('https://www.pemex.com/en/Paginas/default.aspx')
obj.crawler()