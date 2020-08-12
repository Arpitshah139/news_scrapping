from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations
import re
import hashlib

class xinyiglass(object):
    def __init__(self,url,body=None):
        self.url = url
        self.body = body
    def crawler_news(self):
        loop = True
        page = 7
        while loop:
            response = crawler.MakeRequest(self.url.format(page=page),'Get',postData=self.body)
            soup = BeautifulSoup(response.content, 'html.parser')
            bulk_obj = DbOperations.Get_object_for_bulkop(False,'xinyiglass_news')
            news_list = soup.find('div',{'class':'NewsList'})
            if news_list:
                news_data = news_list.find_all('li')
                if news_data:
                    for news in news_data:
                        news_dict = Helper.get_news_dict()

                        title_data = news.find('div',{'class':'title'})
                        title = title_data.text if title_data else ""

                        url_data = news.find('a', {'href': True})
                        url = "https://www.xinyiglass.com/"+str(url_data['href']) if url_data else ''

                        regex = re.compile(r'[\n\r\t]')
                        description_data = news.find('div',{'class':'info'})
                        description = regex.sub("", description_data.text) if description_data else ''

                        date = news.find('span')
                        year_month = news.find('em')
                        publish_date = Helper.parse_date((year_month.text)+"-"+str(date.text)) if date and year_month else ''

                        news_dict.update(
                            {"title": title, "news_title_uid": hashlib.md5(title.encode()).hexdigest(),
                             "url": url, "link": url, "news_url_uid": hashlib.md5(url.encode()).hexdigest(),
                             "description": description.strip(), "text": description.strip(),
                             "publishedAt": publish_date, 'date': publish_date, "publishedAt_scrapped": publish_date,
                             "company_id": "xinyiglass", "ticker": "xinyiglass_scrapped", "industry_name": "xinyiglass",
                             "news_provider": "xinyiglass" })

                        bulk_obj.insert(news_dict)

                        if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                            bulk_obj.execute()
                            bulk_obj = DbOperations.Get_object_for_bulkop(False,'xinyiglass_news')

                    if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                        bulk_obj.execute()

                    page += 1
                else:
                    print("News Not Found")
                    loop = False
            else:
                print("News Not Found")
                loop = False

url = "https://www.xinyiglass.com/en/companynews/list.aspx?page={page}"
news_obj = xinyiglass(url)
news_obj.crawler_news()