import requests
import json
from datetime import timedelta
from datetime import datetime


def interval(func: callable):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        interval = args
        print("requesting " + interval[1] + " - " + interval[2])
        return res

    return wrapper

# def minus_day_from_end(func: callable, end):
#     def wrapper(*args, **kwargs):
#         one_day = timedelta(days=1)
#         end = datetime.strptime(end, '%Y-%m-%d')
#         end = end.date() - one_day
#         func(*args, **kwargs)



class BTCApi:

    @interval
    def make_request(self, start, end):

        one_day = timedelta(days=1)
        end = datetime.strptime(end, '%Y-%m-%d')
        end = end.date() - one_day

        response_data = requests.get('https://api.coindesk.com/v1/bpi/historical/close.json',
                                     params={'start': start, 'end': end})
        raw_response = json.loads(response_data.content)
        response = raw_response['bpi']
        return response

    def put_req_data_to_dict(self, data_from_db: dict, start, end):
        dates = self.make_request(start, end)
        for date, price in dates.items():
            data_from_db[date] = price



a = BTCApi()
b = a.make_request("2022-01-01", "2022-01-02")
print(b)