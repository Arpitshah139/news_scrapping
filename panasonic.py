import datetime
from helper import Helper
from bs4 import BeautifulSoup
from crawler import *

class panasonic(object):

    def __init__(self,url,body=None):
        self.url = url
        self.body = body
    def crawler(self):
        try:
            data = []
            counter = 1
            while True:
                response = crawler.MakeRequest(self.url.format(counter=counter),"Get")
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, "html.parser")

                    boxs = soup.find_all("div",{"class":'unicom-newsListItem'})
                    for box in boxs:
                        date = box.find("p",{"class":"unicom-listInformationDate"}).text
                        if date:
                            date = Helper.parse_date(date)
                            if date.year < datetime.datetime.now().year:
                                break
                        datadict = Helper.get_news_dict()
                        datadict.update({"newsurl":box.find("a")['href']})
                        description = self.fetchDescription(box.find("a")['href'])
                        datadict.update({
                            "url": self.url,
                            "date": box.find("p",{"class":"unicom-listInformationDate"}).text,
                            "news_provider": "panasonic",
                            "formatted_sub_header": box.find("h3",{"class":"unicom-newsListTitleIn"}).text,
                            "publishedAt": date,
                            "description": description,
                            "title": box.find("h3",{"class":"unicom-newsListTitleIn"}).text,
                            "link": self.url
                        })

                        data.append(datadict)
                    counter += counter
                    self.url = "https://news.panasonic.com/global/all/all_{counter}.html"
                else:
                    break
            DbOperations.InsertIntoMongo("panasonic_news",data)
        except Exception as e:
            print (e)

    def fetchDescription(self,url):
        article = ''
        try:
            description = crawler.MakeRequest(url, "Get")
            articlesoup = BeautifulSoup(description.content, 'html.parser')
            articles = articlesoup.find_all("p", {"class": "block"})
            for a in articles:
                article +=a.text
        except Exception as e:
            print(e)
        return article
obj = panasonic('https://news.panasonic.com/global/all/all.html')
obj.crawler()