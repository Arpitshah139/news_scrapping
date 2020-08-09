import datetime
from helper import Helper
from bs4 import BeautifulSoup
from crawler import *
class TI(object):

    def __init__(self,url,body=None):
        self.url = url
        self.body = body


    def crawler(self):
        try:
            response = crawler.MakeRequest(self.url,"Post",postData=self.body)
            soup = BeautifulSoup(response.content, "html.parser")
            news = soup.find_all("div",{"class":"row row-padding listing"})
            data = []
            for new in news:
                datadict = Helper.get_news_dict()
                datadict.update({"newsurl": "https://news.ti.com/" + new.find("a")['href']})
                description = self.fetchDescription("https://news.ti.com/" + new.find("a")['href'])
                datadict.update({
                    "url": self.url,
                    "date": new.find("div",{"class":"rel-date"}).text,
                    "news_provider": "TEXAS INSTRUMENTS INC",
                    "formatted_sub_header": new.find("div",{"class":"abstract"}).text if new.find("div",{"class":"abstract"}) is not None else '',
                    "publishedAt": Helper.parse_date((new.find("div",{"class":"rel-date"}).text).split("|")[0]),
                    "description": description,
                    "title": new.find("div",{"class":"abstract"}).text if new.find("div",{"class":"abstract"}) is not None else '',
                    "link": self.url
                })
                print(datadict)
                data.append(datadict)

            DbOperations.InsertIntoMongo("ti_news", data)

        except Exception as e:
            print(e)

    def fetchDescription(self,url):
        article = ''
        try:
            description = crawler.MakeRequest(url, "Get")
            articlesoup = BeautifulSoup(description.content, 'html.parser')
            article = articlesoup.find("p").text
        except Exception as e:
            print(e)
        return article



obj = TI('https://news.ti.com/news-releases/',{"display_month":"","display_year":"2020","fm_content_type_id":"","page_size":"100","section_id":"1,124797,124796","start_row":"1","tekMsBtn":""})
obj.crawler()

