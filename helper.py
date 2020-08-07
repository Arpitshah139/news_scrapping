import datetime
import pandas as pd

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

    @staticmethod
    def parse_date(date_string, format=None):
            if format is not None:
                    return pd.to_datetime(date_string, format=format)
            elif ((date_string.find('-') <= 2 and date_string.find('.') == -1 and date_string.find('/') == -1) or (
                    date_string.find('.') <= 2 and date_string.find('-') == -1 and date_string.find('/') == -1) or (
                          date_string.find('/') <= 2 and date_string.find('-') == -1 and date_string.find('.') == -1)):
                    return pd.to_datetime(date_string, dayfirst=True)
            else:
                    return pd.to_datetime(date_string, yearfirst=True)