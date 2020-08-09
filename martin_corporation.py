from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations

class martin_corporation(object):
    def __init__(self,url,body=None):
        self.url = url
        self.body = body
        self.header = {
                            'upgrade-insecure-requests': "1",
                            'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
                            'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                            'sec-fetch-site': "same-origin",
                            'sec-fetch-mode': "navigate",
                            'sec-fetch-user': "?1",
                            'sec-fetch-dest': "document",
                            'cache-control': "no-cache"
                      }
    def crawler_news(self):
        loop = True
        count = 0
        while loop:
            response = crawler.MakeRequest(self.url.format(count=count),'Get',postData=self.body,headers=self.header)
            soup = BeautifulSoup(response.content, 'html.parser')
            bulk_obj = DbOperations.Get_object_for_bulkop(False,'martin_corporation_news')
            news_data = soup.find_all('li', {'class': "wd_item"})
            if news_data:
                for news in news_data:
                    news_dict = Helper.get_news_dict()

                    title_data = news.find('div',{'class','wd_title'})
                    title = title_data.text if title_data else ""

                    url_data = news.find('a', {'href': True})
                    url = url_data['href'] if url_data else ''

                    description_data = news.find('div',{'class':'wd_subtitle'})
                    description = description_data.text if description_data else ''

                    text_data = news.find('div', {'class': 'wd_summary'})
                    text = text_data.text if text_data else ''

                    publish_date_data = news.find('div',{'class':'wd_date'})
                    publish_date = Helper.parse_date(publish_date_data.text) if publish_date_data and publish_date_data.text != '' else ''

                    news_dict.update(
                        {"title": title, "url": url, "formatted_sub_header": title, "description": description, "link": url,
                         "publishedAt":publish_date,'date':publish_date,"news_provider": "martin corporation","text":text})

                    bulk_obj.insert(news_dict)

                    if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                        bulk_obj.execute()
                        bulk_obj = DbOperations.Get_object_for_bulkop(False,'martin_corporation_news')

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                    bulk_obj.execute()

                count += 100
            else:
                print("News Not Found")
                loop = False

url = "https://news.lockheedmartin.com/news-releases?l=100&o={count}"
news_obj = martin_corporation(url)
news_obj.crawler_news()