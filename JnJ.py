from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
import json
from DbOps import DbOperations

class johnson_and_johnson(object):
    def __init__(self,url,body=None):
        self.url = url
        self.body = body
    def crawler_news(self):
        loop = True
        page = 1
        while loop:
            response = crawler.MakeRequest(self.url.format(page=page),'Get',postData=self.body)
            soup = BeautifulSoup(response.content, 'html.parser')
            bulk_obj = DbOperations.Get_object_for_bulkop(False,'jnj_news')
            news_data = soup.find_all('div', {'class': "MediaPromo-title"})
            if news_data:
                for news in news_data:
                    news_dict = Helper.get_news_dict()

                    title_data = news.find('div',{'class','ResponsiveText-text'})
                    title = title_data.text if title_data else ""

                    url_data = news.find('a', {'href': True})
                    url = url_data['href'] if url_data else ''

                    url_response = crawler.MakeRequest(url,'Get')
                    url_soup_obj = BeautifulSoup(url_response.content, 'html.parser')
                    url_response_data = url_soup_obj.find('script',{'type':'application/ld+json'})
                    url_response_data = json.loads(url_response_data.text)

                    if url_response_data:
                        publish_date =  Helper.parse_date(url_response_data['datePublished']) if 'datePublished' in url_response_data else ''
                        news_provider =  url_response_data['publisher']['name'] if 'publisher' in url_response_data and 'name' in url_response_data['publisher'] else ''
                        industry_name = news_provider
                        news_dict.update({"news_provider": news_provider,"industry_name":industry_name,"publishedAt":publish_date,'date':publish_date})

                    description_data = url_soup_obj.find('div',{'class':'FullBleedLede-dek'})
                    description = description_data.text if description_data else ''

                    news_dict.update(
                        {"title": title, "url": url, "formatted_sub_header": title, "description": description, "link": url})

                    bulk_obj.insert(news_dict)

                    if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                        bulk_obj.execute()
                        bulk_obj = DbOperations.Get_object_for_bulkop(False,'jnj_well_news')

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                    bulk_obj.execute()

                page += 1

            else:
                print("News Not Found")
                loop = False

url = "https://www.jnj.com/latest-news?all&00000153-423a-dd44-a3d3-f63a0ed40000-page={page}"
news_obj = johnson_and_johnson(url)
news_obj.crawler_news()