import datetime

class Helper(object):

    @staticmethod
    def get_news_dict():
        return {
                "publishedAt_scrapped": datetime.datetime.now(),
                "url":"",
                "date": "",
                "news_provider": "",
                "formatted_text": "",
                "is_scrapped": 1,
                "news_url_uid": "",
                "ticker": "",
                "formatted_sub_header": "",
                "publishedAt": "",
                "industry_name": "",
                "description":"" ,
                "filetype": "",
                "title": "",
                "text": "",
                "company_id": "",
                "news_title_uid": "",
                "topic_name": "",
                "link": "",
                "sub_header": "",
                "is_used": 1
            }